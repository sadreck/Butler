from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import GitHubRefType, WorkflowType, WorkflowStatus, RepoVisibility


class WorkflowResults:
    _workflows: dict = None
    _repos: dict = None
    _missing: dict = None

    @property
    def workflows(self) -> list:
        return list(dict(sorted(self._workflows.items())).values())

    @property
    def repos(self) -> list:
        return list(dict(sorted(self._repos.items())).values())

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

        if str(workflow.repo) not in self._repos:
            self._repos[str(workflow.repo)] = {
                'instance': workflow.repo,
                'count': 0
            }
        self._repos[str(workflow.repo)]['count'] += 1

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
        visibility
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
            'visibility',               # 7
            'ref',                      # 8
            'ref_type',                 # 9
            'ref_resolved_to',          # 10
            'ref_resolved_type',        # 11
            'workflow_type',            # 12
            'workflow_url',             # 13
            'jobs_count',               # 14
            'workflow_status',          # 15
            'parent_workflows',         # 16
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
                RepoVisibility(workflow['instance'].repo.visibility).name.lower(),  # 7
                workflow['instance'].repo.ref,                                      # 8
                GitHubRefType(workflow['instance'].repo.ref_type).name.lower(),     # 9
                resolved_ref,                                                       # 10
                GitHubRefType(resolved_type).name.lower(),                          # 11
                WorkflowType(workflow['instance'].type).name.lower(),               # 12
                workflow['instance'].url(True),                                     # 13
                workflow['job_count'],                                              # 14
                self._friendly_status(workflow['instance'].status),                 # 15
                "\n".join(self._get_parents_for_missing(workflow_name)),            # 16
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

    def count_repos(self) -> int:
        return len(self._repos)

    def count_workflows_and_actions(self) -> int:
        return len(self._workflows)

    def count_archived_repos(self) -> int:
        count = 0
        for repo in self.repos:
            if repo['instance'].archive:
                count += 1
        return count

    def count_forked_repos(self) -> int:
        count = 0
        for repo in self.repos:
            if repo['instance'].fork:
                count += 1
        return count

    def count_workflows(self) -> int:
        count = 0
        for workflow in self.workflows:
            if workflow['instance'].type == WorkflowType.WORKFLOW:
                count += 1
        return count

    def count_actions(self) -> int:
        count = 0
        for workflow in self.workflows:
            if workflow['instance'].type == WorkflowType.ACTION:
                count += 1
        return count

    def count_docker(self) -> int:
        count = 0
        for workflow in self.workflows:
            if workflow['instance'].type == WorkflowType.DOCKER:
                count += 1
        return count