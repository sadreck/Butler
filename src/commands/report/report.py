import os
from src.commands.report.collectors.error_collector import ErrorCollector
from src.commands.report.collectors.runner_collector import RunnerCollector
from src.commands.report.collectors.third_party_collector import ThirdPartyCollector
from src.commands.report.collectors.variable_collector import VariableCollector
from src.commands.report.collectors.workflow_collector import WorkflowCollector
from src.commands.service import Service
from src.github.exceptions import OrgNotFound
from src.libs.components.org import OrgComponent


class ServiceReport(Service):
    output_path: str = None
    repo: str = None
    config: dict = None
    export_formats: list = None

    def run(self) -> bool:
        # First create the output folder if it does not exist.
        if not os.path.isdir(self.output_path):
            self.log.trace(f"Creating output path {self.output_path}")
            os.makedirs(self.output_path)

        db_org = self.database.orgs().find(self.repo)
        if not db_org:
            raise OrgNotFound(f"Organisation not found: {self.repo}")
        org = OrgComponent.from_model(db_org)

        variable_collector = VariableCollector(self.log, self.database, self.config, org, self.output_path, self.export_formats)
        variable_collector.run()

        runner_collector = RunnerCollector(self.log, self.database, self.config, org, self.output_path, self.export_formats)
        runner_collector.run()

        third_party_collector = ThirdPartyCollector(self.log, self.database, self.config, org, self.output_path, self.export_formats)
        third_party_collector.run()

        # error_collector = ErrorCollector(self.log, self.database, self.config, org, self.output_path)
        # error_collector.run()

        workflow_collector = WorkflowCollector(self.log, self.database, self.config, org, self.output_path, self.export_formats)
        workflow_collector.run()

        return True
