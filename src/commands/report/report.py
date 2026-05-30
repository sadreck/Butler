import os
from src.commands.report.index_generator import IndexGenerator
from src.commands.report.query_processor import QueryProcessor
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

        queries_path = os.path.join(os.path.dirname(__file__), 'queries')
        query_files = [str(os.path.join(queries_path, file)) for file in os.listdir(queries_path)]

        outputs = []
        for query_file in query_files:
            instance = QueryProcessor(self.log, self.database, org, self.output_path, query_file)
            output = instance.run()
            outputs.append(output)

        index_path = os.path.join(self.output_path, 'index.html')
        index_generator = IndexGenerator(self.log, org)
        index_generator.run(outputs, index_path)
        self.log.success(f"Report generated and saved at {index_path}")
        return True
