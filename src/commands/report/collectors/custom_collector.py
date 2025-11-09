import os
from datetime import datetime
from src.commands.report.collector_base import CollectorBase
from src.libs.exceptions import InvalidCustomQueryFile
from src.libs.utils import Utils


class CustomCollector(CollectorBase):
    _shortname = 'custom_queries'

    def generate_output_paths(self):
        self.output_paths = {}

    def run(self, custom_queries: list) -> bool:
        data = {
            'org': self.org.name,
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        for i, file in enumerate(custom_queries):
            shortname = f'{self._shortname}_{i}'

            self.log.debug(f"Loading custom query file: {file}")
            query = self._load_custom_query(file)

            self.log.info(f"Running query: {query['name']}")
            results = self.database.select(query['sql'], {'org_id': self.org.id})

            self.log.info(f"Processing {len(results)} results")
            csv_results = self._process_results(results)

            self.outputs['csv'][shortname] = {
                'title': query['name'],
                'path': os.path.join(self.output_path, f'{query['filename']}.csv'),
                'file': f'{query['filename']}.csv',
                'count': len(results)
            }
            self.write_to_csv(self.outputs['csv'][shortname]['path'], csv_results)

        return True

    def _process_results(self, results: list) -> list:
        if len(results) == 0:
            return []

        # Add header.
        rows = [list(results[0].keys())]
        for result in results:
            rows.append(list(result.values()))
        return rows

    def _load_custom_query(self, file: str) -> dict:
        required_properties = ['version', 'name', 'filename', 'sql']
        data = Utils.load_yaml(Utils.read_file(file))
        if not data:
            raise InvalidCustomQueryFile(f"Invalid YAML in custom query file: {file}")

        for property in required_properties:
            if property not in data:
                raise InvalidCustomQueryFile(f"Property {property} is missing from custom query file: {file}")

        return data
