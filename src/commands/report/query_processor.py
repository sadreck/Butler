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
    config: dict = None

    def __init__(self, log: logger, database: Database, org: OrgComponent, output_path: str, config: dict, query_file: str):
        self.log = log
        self.database = database
        self.org = org
        self.output_path = output_path
        self.config = config
        self.query = self._load_query_file(query_file)

    def _load_query_file(self, file: str) -> dict:
        required_properties = ['version', 'name', 'filename', 'sql', 'group']
        data = Utils.load_yaml(Utils.read_file(file))
        if not data:
            raise InvalidCustomQueryFile(f"Invalid YAML in custom query file: {file}")

        for property in required_properties:
            if property not in data:
                raise InvalidCustomQueryFile(f"Property {property} is missing from custom query file: {file}")

        return data

    def run(self) -> dict:
        self.log.info(f"Executing SQL Query for {self.query['name']}")
        raw_results = self._execute_query()

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
            'group': self.query['group'],
            'description': self.query['description'],
        }

    def _execute_query(self) -> list:
        sql, params = self._prepare_query(self.query['sql'])
        params['org'] = self.org.id

        return self.database.select(sql, params)

    def _prepare_query(self, sql: str) -> tuple[str, dict]:
        params = {}
        if '$_TRUSTED_ORGS_$' in sql:
            org_ids = self._get_trusted_org_ids()
            trusted_params = {f'trusted_org_{i}': org_id for i, org_id in enumerate(org_ids)}
            params.update(trusted_params)
            sql = sql.replace("$_TRUSTED_ORGS_$", ", ".join(f":{k}" for k in trusted_params))

        if '$_UNSUPPORTED_RUNNERS_$' in sql:
            unsupported_runners = self.config.get('unsupported_runners', []) or []
            runner_params = {f'unsupported_runner_{i}': runner for i, runner in enumerate(unsupported_runners)}
            params.update(runner_params)
            sql = sql.replace("$_UNSUPPORTED_RUNNERS_$", ", ".join(f":{k}" for k in runner_params))
        return sql, params

    def _get_trusted_org_ids(self) -> list:
        ids = []
        for org_name in (self.config.get('trusted-orgs', []) or []):
            org = self.database.orgs().find(org_name)
            if org:
                ids.append(org.id)
        return ids

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
            'template_to_load': 'generic',
            'name': self.query['name'],
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
