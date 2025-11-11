from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import GitHubRefType
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

    def add_error_workflow(self, workflow: WorkflowComponent, error_workflow: WorkflowComponent | None) -> dict:
        action_name = workflow.action_name()
        if action_name not in self.errors:
            self.errors[action_name] = {
                'instance': workflow,
                'workflows': {},
                'count': 0
            }
        self.errors[action_name]['count'] += 1

        if error_workflow is None:
            return self.errors[action_name]

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

    def csv_for_missing(self) -> list:
        header = [
            'parent_org',
            'parent_repo',
            'parent_workflow',
            'parent_ref',
            'parent_ref_type',
            'parent_fork',
            'parent_archived',
            'parent_job',
            'parent_step',
            'parent_url',
            'missing_org',
            'missing_repo'
            'missing_workflow',
            'missing_ref',
            'missing_external',
            'missing_url'
        ]
        rows = [header]

        for parent_name, parent_workflow in self.missing.items():
            for child_name, child_workflow in parent_workflow['workflows'].items():
                for location in child_workflow['locations']:
                    rows.append([
                        parent_workflow['instance'].repo.org.name,
                        parent_workflow['instance'].repo.name,
                        parent_workflow['instance'].path,
                        parent_workflow['instance'].repo.ref,
                        GitHubRefType(parent_workflow['instance'].repo.ref_type).name.lower(),
                        1 if parent_workflow['instance'].repo.fork else 0,
                        1 if parent_workflow['instance'].repo.archive else 0,
                        parent_workflow['instance'].url(True),
                        location['job_shortname'],
                        location['step'],
                        child_workflow['instance'].repo.org.name,
                        child_workflow['instance'].repo.name,
                        child_workflow['instance'].path,
                        child_workflow['instance'].repo.ref,
                        1 if child_workflow['external'] else 0,
                        child_workflow['instance'].url(True),
                    ])

        return rows

    def csv_for_errors(self) -> list:
        return []
