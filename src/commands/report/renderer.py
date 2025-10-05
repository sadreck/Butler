import csv
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from src.libs.utils import Utils


class Renderer:
    def render(self, template_name: str, template_nav_name: str, data: dict, output_file: str = None) -> str:
        templates_path = os.path.join(Path(__file__).resolve().parent, 'templates')
        if not os.path.isdir(templates_path):
            raise FileNotFoundError(f"Templates path not found: {templates_path}")
        env = Environment(loader=FileSystemLoader(templates_path), undefined=StrictUndefined)
        template = env.get_template('parent_template.html')

        data['template_to_load'] = template_name
        data['template_nav_name'] = template_nav_name

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