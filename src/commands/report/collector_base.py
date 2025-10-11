import csv
import os
from loguru import logger
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from src.libs.utils import Utils
from src.database.database import Database
from src.libs.components.org import OrgComponent


class CollectorBase:
    database: Database = None
    log: logger = None
    org: OrgComponent = None
    config: dict = None
    output_path: str = None
    export_formats: list = None
    outputs: dict = None
    _shortname: str = None

    @property
    def shortname(self) -> str:
        if not self._shortname:
            raise NotImplementedError(f"_shortname not defined in collector")
        return self._shortname

    def __init__(self, log: logger, database: Database, config: dict, org: OrgComponent, output_path: str, export_formats: list):
        self.log = log
        self.database = database
        self.config = config
        self.org = org
        self.output_path = output_path
        self.export_formats = export_formats

        self.outputs = {
            'html': {},
            'csv': {},
            'info': {}
        }

        self.generate_output_paths()

    def generate_output_paths(self):
        raise NotImplementedError("generate_output_paths() not implemented")

    def run(self) -> bool:
        raise NotImplementedError("run() not implemented")

    def render(self, template_name: str, template_nav_name: str, data: dict, output_file: str = None) -> str:
        templates_path = os.path.join(Path(__file__).resolve().parent, 'templates')
        if not os.path.isdir(templates_path):
            raise FileNotFoundError(f"Templates path not found: {templates_path}")
        env = Environment(loader=FileSystemLoader(templates_path), undefined=StrictUndefined)
        template = env.get_template('parent_template.html')

        data['template_to_load'] = template_name
        data['template_nav_name'] = template_nav_name

        #
        # Define custom filters.
        #
        def format_number(number: int) -> str | int:
            try:
                return f"{int(number):,}"
            except (ValueError, TypeError):
                return number

        env.filters['format_number'] = format_number

        output = template.render(data)
        if output_file:
            if not Utils.write_file(output_file, output):
                raise IOError(f"Failed to write output file: {output_file}")
        return output

    def write_to_csv(self, output_file: str, rows: list) -> None:
        self.log.info(f"Saving CSV output to {output_file}")
        if os.path.isfile(output_file):
            os.remove(output_file)

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

        return None