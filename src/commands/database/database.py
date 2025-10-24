from src.commands.service import Service
from src.database.models import WorkflowDataModel, JobModel, JobDataModel, StepModel, StepDataModel, WorkflowModel, VariableModel, VariableValueMappingModel, ConfigModel
from src.libs.constants import WorkflowStatus, PollStatus
from src.libs.exceptions import InvalidCommandLine


class ServiceDatabase(Service):
    purge: bool = None
    reprocess: bool = None
    list_orgs: bool = None

    def run(self) -> bool:
        if self.purge:
            self.log.info("Purging database")
            return self._purge_database()
        elif self.reprocess:
            self.log.info("Resetting processed data")
            return self._reprocess_database()
        elif self.list_orgs:
            self.log.info("Listing orgs")
            return self._list_orgs()
        else:
            raise InvalidCommandLine("No valid arguments passed")

    def _purge_database(self) -> bool:
        self.log.info("Getting database tables")
        tables = self.database.get_tables()
        self.log.info(f"Got {len(tables)} tables")

        for table in tables:
            self.log.info(f"Purging {table}")
            self.database.execute(f"DELETE FROM {table}")
            self.database.commit()

        return True

    def _reprocess_database(self) -> bool:
        tables = [
            WorkflowDataModel.__tablename__,
            JobModel.__tablename__,
            JobDataModel.__tablename__,
            StepModel.__tablename__,
            StepDataModel.__tablename__,
            VariableModel.__tablename__,
            VariableValueMappingModel.__tablename__,
            # ConfigModel.__tablename__, # Commented out on purpose.
        ]

        for table in tables:
            self.log.info(f"Purging {table}")
            self.database.execute(f"DELETE FROM {table}")
            self.database.commit()

        self.log.info("Updating workflow statuses")
        sql = f"UPDATE {WorkflowModel.__tablename__} SET status = :new_status WHERE status = :old_status OR status = :error"
        self.database.execute(sql, {'new_status': WorkflowStatus.DOWNLOADED, 'old_status': WorkflowStatus.PROCESSED, 'error': WorkflowStatus.ERROR})
        self.database.commit()

        return True

    def _list_orgs(self) -> bool:
        sql = """
            SELECT
                o.name,
                COUNT(r.id) AS total_repos
            FROM organisations o
            LEFT JOIN repositories r ON r.org_id = o.id
            WHERE
                o.poll_status = :scanned
            GROUP BY o.name
            ORDER BY o.name
        """
        results = self.database.select(sql, {'scanned': PollStatus.SCANNED})

        for result in results:
            self.log.success(f"{result['name']} organisation with {result['total_repos']} repositories")

        return False
