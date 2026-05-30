import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined


class ReportHelper:
    def render(self, data: dict) -> str:
        templates_path = os.path.join(Path(__file__).resolve().parent, 'templates')
        if not os.path.isdir(templates_path):
            raise FileNotFoundError(f"Templates path not found: {templates_path}")
        env = Environment(loader=FileSystemLoader(templates_path), undefined=StrictUndefined)
        template = env.get_template('parent.html')

        output = template.render(data)
        return output
