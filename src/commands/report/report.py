import os

from src.commands.report.collectors.custom_collector import CustomCollector
from src.commands.report.collectors.index_generator import IndexGenerator
from src.commands.report.collectors.runner_collector import RunnerCollector
from src.commands.report.collectors.third_party_collector import ThirdPartyCollector
from src.commands.report.collectors.variable_collector import VariableCollector
from src.commands.report.collectors.workflow_collector import WorkflowCollector
from src.commands.report.collectors.error_collector import ErrorCollector
from src.commands.service import Service
from src.github.exceptions import OrgNotFound
from src.libs.components.org import OrgComponent


class ServiceReport(Service):
    output_path: str = None
    repo: str = None
    config: dict = None
    custom_queries: list = None

    def run(self) -> bool:
        # First create the output folder if it does not exist.
        if not os.path.isdir(self.output_path):
            self.log.trace(f"Creating output path {self.output_path}")
            os.makedirs(self.output_path)

        db_org = self.database.orgs().find(self.repo)
        if not db_org:
            raise OrgNotFound(f"Organisation not found: {self.repo}")
        org = OrgComponent.from_model(db_org)

        collectors = [
            WorkflowCollector,
            ThirdPartyCollector,
            VariableCollector,
            RunnerCollector,
            ErrorCollector,
        ]

        outputs = {}
        for collector in collectors:
            instance = collector(self.log, self.database, self.config, org, self.output_path)
            instance.run()
            outputs[instance.shortname] = instance.outputs

        if len(self.custom_queries) > 0:
            instance = CustomCollector(self.log, self.database, self.config, org, self.output_path)
            instance.run(self.custom_queries)
            outputs[instance.shortname] = instance.outputs

        index_generator = IndexGenerator(self.log, self.database, self.config, org, self.output_path)
        index_generator.generated_outputs = outputs
        index_generator.run()

        self.log.success(f"Report generated and saved at {index_generator.outputs['html']}")
        return True
