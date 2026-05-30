import csv
import os
from loguru import logger
from src.commands.report.report_helper import ReportHelper
from src.commands.report.table_elements import Table
from src.database.database import Database
from src.libs.components.org import OrgComponent
from src.libs.exceptions import InvalidCustomQueryFile
from src.libs.utils import Utils


class QueryProcessor(ReportHelper):
    query: dict = None
    database: Database = None
    log: logger = None
    org: OrgComponent = None
    output_path: str = None

    def __init__(self, log: logger, database: Database, org: OrgComponent, output_path: str, query_file: str):
        self.log = log
        self.database = database
        self.org = org
        self.output_path = output_path
        self.query = self._load_query_file(query_file)

    def _load_query_file(self, file: str) -> dict:
        required_properties = ['version', 'name', 'filename', 'sql']
        data = Utils.load_yaml(Utils.read_file(file))
        if not data:
            raise InvalidCustomQueryFile(f"Invalid YAML in custom query file: {file}")

        for property in required_properties:
            if property not in data:
                raise InvalidCustomQueryFile(f"Property {property} is missing from custom query file: {file}")

        return data

    def run(self) -> dict:
        self.log.info(f"Executing SQL Query for {self.query['name']}")
        raw_results = self.database.select(self.query['sql'], {'org': self.org.id})

        self.log.info(f"Processing {len(raw_results)} CSV results")
        results = self._process_results_csv(raw_results)

        output_csv = os.path.join(self.output_path, f'{self.query['filename']}.csv')
        self.write_to_csv(output_csv, results)

        self.log.info(f"Processing {len(raw_results)} HTML results")
        table = self._generate_table(raw_results)

        output_html = os.path.join(self.output_path, f'{self.query['filename']}.html')
        self.write_to_html(output_html, table)
        return {
            'count': len(raw_results),
            'html': os.path.basename(output_html),
            'csv': os.path.basename(output_csv),
            'name': self.query['name'],
        }

    def _process_results_csv(self, results: list) -> list:
        if len(results) == 0:
            return []

        # Add header.
        rows = [list(results[0].keys())]
        for result in results:
            rows.append(list(result.values()))
        return rows

    def write_to_html(self, output_file: str, table: Table) -> None:
        self.log.info(f"Saving HTML output to {output_file}")
        if os.path.isfile(output_file):
            os.remove(output_file)

        data = {
            'table': table,
            'org': self.org.name,
            'template_to_load': 'generic'
        }

        html = self.render(data)
        with open(output_file, 'w') as file:
            file.write(html)

    def write_to_csv(self, output_file: str, rows: list) -> None:
        self.log.info(f"Saving CSV output to {output_file}")
        if os.path.isfile(output_file):
            os.remove(output_file)

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        return None

    def _generate_table(self, raw_results: list) -> Table:
        table = Table(self.query.get('columns', {}))
        table.load_rows(raw_results)

        return table
