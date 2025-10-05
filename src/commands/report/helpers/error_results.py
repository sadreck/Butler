from src.libs.components.workflow import WorkflowComponent


class ErrorResults:
    workflows: dict = None

    @property
    def count(self) -> int:
        return len(self.workflows)

    def __init__(self):
        self.workflows = {}

    def get_or_create(self, workflow_error: WorkflowComponent, workflow_parent: WorkflowComponent) -> dict:
        if str(workflow_error) not in self.workflows:
            self.workflows[str(workflow_error)] = {
                'workflow': workflow_error,
                'parents': {}
            }

        if str(workflow_parent) not in self.workflows[str(workflow_error)]['parents']:
            self.workflows[str(workflow_error)]['parents'][str(workflow_parent)] = workflow_parent
            self.workflows[str(workflow_error)]['parents'] = dict(sorted(self.workflows[str(workflow_error)]['parents'].items()))

        self.workflows = dict(sorted(self.workflows.items()))

        return self.workflows[str(workflow_error)]['parents'][str(workflow_parent)]
