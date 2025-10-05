from src.database.helpers.db_base import DBBase
from src.database.models import VariableModel


class DBVars(DBBase):
    def create_variables(self, name: str, id: int, variables: list) -> bool:
        if name in ['workflow', 'workflows']:
            return self._create_workflow_variables(id, variables)
        elif name in ['job', 'jobs']:
            return self._create_job_variables(id, variables)
        elif name in ['step', 'steps']:
            return self._create_step_variables(id, variables)
        return False

    def _create_workflow_variables(self, workflow_data_id: int, variables: list) -> bool:
        return self.create(variables, workflow_data_id, 0, 0)

    def _create_job_variables(self, job_data_id: int, variables: list) -> bool:
        return self.create(variables, 0, job_data_id, 0)

    def _create_step_variables(self, step_data_id: int, variables: list) -> bool:
        return self.create(variables, 0, 0, step_data_id)

    def create(self, variables: list, workflow_data_id: int, job_data_id: int, step_data_id: int) -> bool:
        if workflow_data_id <= 0 and job_data_id <= 0 and step_data_id <= 0:
            raise ValueError("All of workflow, job, and step data ids are empty")

        for name in variables:
            variable = VariableModel(name=name, workflow_data_id=workflow_data_id, job_data_id=job_data_id, step_data_id=step_data_id)
            self.add(variable)

        self.save()
        return True

    def count(self) -> int:
        return self.session.query(VariableModel).count()
