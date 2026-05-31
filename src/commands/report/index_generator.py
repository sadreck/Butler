from loguru import logger
from src.libs.components.org import OrgComponent
from src.commands.report.report_helper import ReportHelper


class IndexGenerator(ReportHelper):
    log: logger = None
    org: OrgComponent = None

    def __init__(self, log: logger, org: OrgComponent):
        self.log = log
        self.org = org

    def run(self, outputs: list, output_file: str):
        data = {
            'outputs': outputs,
            'org': self.org.name,
            'template_to_load': 'index'
        }
        html = self.render(data)
        with open(output_file, 'w') as file:
            file.write(html)
