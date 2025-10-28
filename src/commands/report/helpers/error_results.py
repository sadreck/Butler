from src.libs.components.workflow import WorkflowComponent
from src.libs.instances.workflow import WorkflowInstance


class ErrorResults:
    missing: dict = None
    errors: dict = None

    def __init__(self):
        self.missing = {}
        self.errors = {}

    def add_missing_workflow(self, workflow: WorkflowComponent, missing_workflow: WorkflowComponent) -> dict:
        action_name = workflow.action_name()
        if action_name not in self.missing:
            self.missing[action_name] = {
                'instance': workflow,
                'workflows': {},
                'count': 0
            }
        self.missing[action_name]['count'] += 1

        instance = WorkflowInstance(workflow.data, workflow.repo)
        locations = []
        for job in instance.jobs:
            for step in job.steps:
                if step.uses == missing_workflow.name:
                    locations.append({
                        'job_name': job.name,
                        'job_shortname': job.shortname,
                        'step': step.number,
                        'step_name': step.name
                    })

        child_action = missing_workflow.action_name()
        if not child_action in self.missing[action_name]['workflows']:
            self.missing[action_name]['workflows'][child_action] = {
                'instance': missing_workflow,
                'external': missing_workflow.repo.org.name.lower() != workflow.repo.org.name.lower(),
                'locations': []
            }
        self.missing[action_name]['workflows'][child_action]['locations'].extend(locations)

        return self.missing[action_name]

    def add_error_workflow(self, workflow: WorkflowComponent, error_workflow: WorkflowComponent) -> dict:
        action_name = workflow.action_name()
        if action_name not in self.errors:
            self.errors[action_name] = {
                'instance': workflow,
                'workflows': {},
                'count': 0
            }
        self.errors[action_name]['count'] += 1

        instance = WorkflowInstance(workflow.data, workflow.repo)
        locations = []
        for job in instance.jobs:
            for step in job.steps:
                if step.uses == error_workflow.name:
                    locations.append({
                        'job_name': job.name,
                        'job_shortname': job.shortname,
                        'step': step.number,
                        'step_name': step.name
                    })

        child_action = error_workflow.action_name()
        if not child_action in self.errors[action_name]['workflows']:
            self.errors[action_name]['workflows'][child_action] = {
                'instance': error_workflow,
                'locations': []
            }
        self.errors[action_name]['workflows'][child_action]['locations'].extend(locations)

        return self.errors[action_name]

    def count(self, what: str) -> int:
        match what.lower():
            case 'missing':
                return len(self.missing)
            case 'errors':
                return len(self.errors)
            case _:
                return 0
