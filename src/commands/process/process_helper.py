import re
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import VariableMappingType, VariableMappingGroupType
from src.libs.instances.action import ActionInstance
from src.libs.instances.job import JobInstance
from src.libs.instances.step import StepInstance


class ProcessHelper:
    def _index_action(self, action: ActionInstance, workflow: WorkflowComponent) -> bool:
        job_db = self.database.jobs().create(workflow.id, 'type', action.type)
        action.id = job_db.id

        for name, properties in action.inputs.items():
            self.database.jobs().set_data(action.id, 'input', {'name': name})
            self.database.jobs().set_data(action.id, f"input-{name}", properties)

        for name, properties in action.outputs.items():
            self.database.jobs().set_data(action.id, 'output', {'name': name})
            self.database.jobs().set_data(action.id, f"output-{name}", properties)

        for name, data in action.properties(['inputs', 'outputs']):
            self.database.jobs().set_data(action.id, name, data)

        for step in action.steps:
            self._index_step(step, action)

        return True

    def _index_job(self, job: JobInstance, workflow: WorkflowComponent) -> bool:
        job_db = self.database.jobs().create(workflow.id, job.name, job.shortname)
        job.id = job_db.id

        self.database.jobs().set_data(job.id, 'runner', job.runners)

        for name, data in job.properties(['steps']):
            self.database.jobs().set_data(job.id, name, data)

        for step in job.steps:
            self._index_step(step, job)

        return True

    def _index_step(self, step: StepInstance, job: JobInstance | ActionInstance) -> bool:
        step_db = self.database.steps().create(job.id, step.number)
        step.id = step_db.id

        for name, data in step.properties([]):
            self.database.steps().set_data(step.id, name, data)

        return True

    def _extract_variables_from_text(self, text: str) -> list:
        pattern = r'\{\{\s*(.*?)\s*\}\}'
        variables = re.findall(pattern, text)
        all_variables = []
        for variable in variables:
            # Replace any unwanted characters.
            # variable = re.sub(r'[!()\[\],\'\"]', ' ', variable)
            variable = re.sub(r'[!(),\'\"]', ' ', variable)
            # The + ensures that consecutive spaces or pipes are treated as a single separator.
            parts = re.split(r'[| ]+', variable)
            for part in parts:
                if part.lower().startswith(('github.', 'secrets.', 'vars.', 'env.', 'inputs.', 'outputs.', 'steps.', 'matrix.', 'needs.', 'runner.')):
                    all_variables.append(part.strip())

        return sorted(set(all_variables))

    def _populate_variable_value_mappings(self) -> None:
        # Write variables from steps.
        sql = f"""
            INSERT INTO variables_value_mapping (
                type,
                type_join_id,
                group_type,
                name,
                value
            )

            SELECT
                {VariableMappingType.STEPS},
                s.id AS step_id,
                {VariableMappingGroupType.ENV},
                ('env.' || sd.name) AS env_var_name,
                v.name AS env_var_value
            -- First table is step_data, filter is defined in WHERE.
            FROM step_data sd
            -- Join with variables and get all ${{}} extracted values that do not
            -- begin with 'env.%'. This is because the variables table will also
            -- have an instance of 'env.%' if those are used within any commands.
            -- We are just looking for the definitions of those instead right now.
            JOIN variables v ON v.step_data_id = sd.id AND v.name NOT LIKE 'env.%'
            -- Join with steps, jobs, workflows, to get all data for the identified
            -- variables.
            JOIN steps s ON s.id = sd.step_id
            -- For the first step_data filter, filter by 'ENV' variables.
            WHERE sd.property = 'env'
        """
        self.log.info("Populating env variables from steps")
        self.database.execute(sql)
        self.database.commit()

        # Write variables from jobs.
        sql = f"""
            INSERT INTO variables_value_mapping (
                type,
                type_join_id,
                group_type,
                name,
                value
            )

            SELECT
                {VariableMappingType.JOBS},
                j.id AS job_id,
                {VariableMappingGroupType.ENV},
                ('env.' || jd.name) AS env_var_name,
                v.name AS env_var_value
            -- First table is job_data, filter is defined in WHERE.
            FROM job_data jd
            -- Join with variables and get all ${{}} extracted values that do not
            -- begin with 'env.%'. This is because the variables table will also
            -- have an instance of 'env.%' if those are used within any commands.
            -- We are just looking for the definitions of those instead right now.
            JOIN variables v ON v.job_data_id = jd.id AND v.name NOT LIKE 'env.%'
            -- Join with jobs, workflows, to get all data for the identified vars.
            JOIN jobs j ON j.id = jd.job_id
            JOIN workflows w ON w.id = j.workflow_id
            -- For the first job_data filter, filter by 'ENV' variables.
            WHERE jd.property = 'env'
        """
        self.log.info("Populating env variables from jobs")
        self.database.execute(sql)
        self.database.commit()

        # Write variables from workflows.
        sql = f"""
            INSERT INTO variables_value_mapping (
                type,
                type_join_id,
                group_type,
                name,
                value
            )

            SELECT
                {VariableMappingType.WORKFLOWS},
                w.id AS workflow_id,
                {VariableMappingGroupType.ENV},
                ('env.' || wd.name) AS env_var_name,
                v.name AS env_var_value
            -- First table is job_data, filter is defined in WHERE.
            FROM workflow_data wd
            -- Join with variables and get all ${{}} extracted values that do not
            -- begin with 'env.%'. This is because the variables table will also
            -- have an instance of 'env.%' if those are used within any commands.
            -- We are just looking for the definitions of those instead right now.
            JOIN variables v ON v.workflow_data_id = wd.id AND v.name NOT LIKE 'env.%'
            -- Join with workflows, to get all data for the identified vars.
            JOIN workflows w ON w.id = wd.workflow_id
            -- For the first job_data filter, filter by 'ENV' variables.
            WHERE wd.property = 'env'
        """
        self.log.info("Populating env variables from workflows")
        self.database.execute(sql)
        self.database.commit()
        return None
