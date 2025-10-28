import threading
from contextlib import nullcontext
from src.commands.process.process_helper import ProcessHelper
from src.commands.service import Service
from src.database.models import WorkflowDataModel, JobDataModel, StepDataModel
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import WorkflowStatus, WorkflowType
from src.libs.exceptions import UnknownWorkflowType
from src.libs.instances.action import ActionInstance
from src.libs.instances.workflow import WorkflowInstance
from src.libs.utils import Utils


class ServiceProcess(Service, ProcessHelper):
    lock: threading.Lock = None
    threads: int = None

    def run(self) -> bool:
        # Thanks SQLite3 :>
        self.lock = threading.Lock() if self.threads > 1 else nullcontext()

        self.log.info(f"Processing workflows")
        self._process_workflows()

        self.log.info("Extracting variables")
        self._extract_variables()

        self.log.info("Populating variable value mappings")
        self._populate_variable_value_mappings()

        return True

    def _process_workflows(self) -> None:
        while True:
            batch = self.database.next_to_process(self.threads)
            if not batch:
                break

            if self.threads == 1:
                self._process_workflow(batch)
            else:
                arguments = [(workflow,) for workflow in batch]
                Utils.multithread(self._process_workflow, arguments)

            self.database.commit()

    def _process_workflow(self, workflow: WorkflowComponent) -> bool:
        self.log.info(f"Processing workflow {workflow}")
        if not workflow.data and workflow.type != WorkflowType.DOCKER:
            self.log.error(f"Could not load JSON for {workflow}")
            with self.lock:
                self.database.workflows().update_status(workflow.id, WorkflowStatus.ERROR)
            return False

        if workflow.type == WorkflowType.WORKFLOW:
            instance = WorkflowInstance(workflow.data, workflow.repo)
            with self.lock:
                for trigger, properties in instance.on_data.items():
                    self.database.workflows().set_data(workflow.id, 'on', trigger)
                    for name, value in properties.items():
                        self.database.workflows().set_data(workflow.id, f"on-{trigger}-{name}", value)

                for name, data in instance.properties(['on', 'jobs']):
                    self.database.workflows().set_data(workflow.id, name, data)

                for job in instance.jobs:
                    self._index_job(job, workflow)
        elif workflow.type == WorkflowType.ACTION:
            instance = ActionInstance(workflow.data, workflow.repo)
            with self.lock:
                self.database.workflows().set_data(workflow.id, 'name', instance.name)
                self._index_action(instance, workflow)

        elif workflow.type == WorkflowType.DOCKER:
            pass
        else:
            raise UnknownWorkflowType(f"Unknown workflow type for {workflow}")

        with self.lock:
            self.database.workflows().update_status(workflow.id, WorkflowStatus.PROCESSED)
        return True

    def _extract_variables(self) -> bool:
        items = {
            'workflow': self.database.workflows,
            'job': self.database.jobs,
            'step': self.database.steps
        }

        for name, component in items.items():
            self.log.info(f"Extracting {name} variables")

            id = 0
            while True:
                batch = component().find_next_data(id, self.threads)
                if not batch or len(batch) == 0:
                    break

                if self.threads == 1:
                    self._extract_variables_item(batch[0], name)
                else:
                    arguments = [(record, name,) for record in batch]
                    Utils.multithread(self._extract_variables_item, arguments)

                # Get the id of the last item, as it's all returned sorted it'd be the highest one for the next lookup.
                id = batch[-1].id

                self.database.commit()

        return True

    def _extract_variables_item(self, data: WorkflowDataModel | JobDataModel | StepDataModel, name: str) -> None:
        variables = self._extract_variables_from_text(data.value)
        if data.property == 'env':
            variables.append(f"env.{data.name}")
        if len(variables) > 0:
            with self.lock:
                self.database.vars().create_variables(name, data.id, variables)
        return None
