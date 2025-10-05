from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import GitHubRefType, WorkflowType, WorkflowStatus


class WorkflowResults:
    _workflows: dict = None
    _missing: dict = None

    @property
    def workflows(self):
        return list(dict(sorted(self._workflows.items())).values())

    def __init__(self) -> None:
        self._workflows = {}
        self._repos = {}
        self._missing = {}

    def get_or_create(self, workflow: WorkflowComponent, job_count: int) -> dict:
        if str(workflow) not in self._workflows:
            self._workflows[str(workflow)] = {
                'instance': workflow,
                'job_count': job_count,
            }

        return self._workflows[str(workflow)]

    def add_missing_workflows(self, workflow: WorkflowComponent, parent_workflow: WorkflowComponent) -> None:
        if str(workflow) not in self._missing:
            self._missing[str(workflow)] = {}

        if str(parent_workflow) not in self._missing[str(workflow)]:
            self._missing[str(workflow)][str(parent_workflow)] = []
        self._missing[str(workflow)][str(parent_workflow)].append(parent_workflow)

    def for_csv(self) -> list:
        """
        org
        repo
        workflow
        fork
        archived
        stars
        ref
        ref_type
        ref_resolved_to
        ref_resolved_type
        workflow_type
        workflow_url
        """
        header = [
            'org',                      # 1
            'repo',                     # 2
            'workflow',                 # 3
            'fork',                     # 4
            'archived',                 # 5
            'stars',                    # 6
            'ref',                      # 7
            'ref_type',                 # 8
            'ref_resolved_to',          # 9
            'ref_resolved_type',        # 10
            'workflow_type',            # 11
            'workflow_url',             # 12
            'jobs_count',               # 13
            'workflow_status',          # 14
            'parent_workflows',         # 15
        ]

        rows = [header]
        for workflow_name, workflow in self._workflows.items():
            if workflow['instance'].repo.ref_type == GitHubRefType.COMMIT:
                resolved_ref = workflow['instance'].repo.resolved_ref
                resolved_type = workflow['instance'].repo.resolved_ref_type
            else:
                resolved_type = GitHubRefType.COMMIT
                resolved_ref = workflow['instance'].repo.ref_commit

            row = [
                workflow['instance'].repo.org.name,                                 # 1
                workflow['instance'].repo.name,                                     # 2
                workflow['instance'].path,                                          # 3
                1 if workflow['instance'].repo.fork else 0,                         # 4
                1 if workflow['instance'].repo.archive else 0,                      # 5
                workflow['instance'].repo.stars,                                    # 6
                workflow['instance'].repo.ref,                                      # 7
                GitHubRefType(workflow['instance'].repo.ref_type).name.lower(),     # 8
                resolved_ref,                                                       # 9
                GitHubRefType(resolved_type).name.lower(),                          # 10
                WorkflowType(workflow['instance'].type).name.lower(),               # 11
                workflow['instance'].url(True),                                     # 12
                workflow['job_count'],                                              # 13
                self._friendly_status(workflow['instance'].status),                 # 14
                "\n".join(self._get_parents_for_missing(workflow_name)),            # 15
            ]

            rows.append(row)

        return rows

    def _get_parents_for_missing(self, workflow_name: str) -> list:
        if not workflow_name in self._missing:
            return []
        parents = []
        for name, workflows in self._missing[workflow_name].items():
            for workflow in workflows:
                parents.append(workflow.url(True))
        return parents

    def _friendly_status(self, status: WorkflowStatus) -> str:
        if status == WorkflowStatus.ERROR:
            return 'error'
        elif status == WorkflowStatus.MISSING:
            return 'missing'
        elif status == WorkflowStatus.SUBMODULE:
            return 'submodule'
        return ''
