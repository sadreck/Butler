from src.database.models import OrganisationModel, RepositoryModel
from src.github.exceptions import HttpNotFound
from src.libs.components.org import OrgComponent
from src.libs.components.repo import RepoComponent
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import RepoStatus, WorkflowStatus, WorkflowType
from src.libs.exceptions import UnknownWorkflowType
from src.libs.instances.workflow import WorkflowInstance
from src.libs.utils import Utils


class DownloadHelper:
    _cache_orgs: dict = None

    def _create_org(self, org: OrgComponent) -> OrganisationModel:
        if self._cache_orgs is None:
            self._cache_orgs = {}

        key = org.name.lower()
        if key not in self._cache_orgs:
            self._cache_orgs[key] = self.database.orgs().create(org)
        return self._cache_orgs[key]

    def _create_repo(self, repo: RepoComponent) -> RepositoryModel:
        return self.database.repos().create(repo)

    def _repo_already_stored(self, repo_db: RepositoryModel | None) -> bool:
        if not repo_db:
            return False

        if len(repo_db.ref) > 0:
            # Repo is already stored, skip.
            return True
        elif repo_db.status == RepoStatus.REDIRECT:
            # Repo is redirected and has already been saved.
            return True
        elif repo_db.status != RepoStatus.NONE:
            # Repo saved and is either missing, error, etc.
            return True

        return False

    def _fetch_repo(self, repo: RepoComponent) -> RepoComponent:
        try:
            repo = self.github_client.get_repo(repo, True)
        except HttpNotFound as e:
            repo.status = RepoStatus.MISSING
        return repo

    def _create_workflow(self, workflow: WorkflowComponent) -> any:
        return self.database.workflows().create(workflow)

    def _filter_workflows(self, files: list, only_workflows: list) -> list[str]:
        workflows = []
        skipped = 0
        for file in files:
            if not Utils.is_yaml_extension(file):
                self.log.warning(f"Skipping workflow file, wrong extension: {file}")
                continue

            if len(only_workflows) > 0:
                filename = Utils.remove_yaml_extension(file).lower()
                if filename not in only_workflows:
                    skipped += 1
                    continue

            workflows.append(file)

        if skipped > 0:
            self.log.trace(f"\tFound {len(files)} workflows but skipped {skipped} due to --workflows argument")

        return workflows

    def _ls_workflows(self, repo: RepoComponent, only_workflows: list) -> list[WorkflowComponent]:
        try:
            files = self.github_client.ls(repo, '.github/workflows')
        except HttpNotFound:
            files = []
        files = self._filter_workflows(files, only_workflows)

        workflows = []
        for file in files:
            workflow = WorkflowComponent(f"{repo.org.name}/{repo.name}/{file}@{repo.ref}")
            workflow.status = WorkflowStatus.NONE
            workflow.repo = repo
            workflows.append(workflow)
        return workflows

    def _download(self, workflow: WorkflowComponent) -> str | None:
        if Utils.is_yaml_extension(workflow.path):
            return self.github_client.download(workflow)

        if workflow.type != WorkflowType.ACTION:
            raise UnknownWorkflowType(f"Workflow path does not have yaml extension and is not marked as an action")

        return self.github_client.download_action(workflow)

    def _mark_missing(self, workflow: WorkflowComponent) -> None:
        self.database.workflows().update_status(workflow.id, WorkflowStatus.MISSING)

    def _process_contents(self, workflow: WorkflowComponent, contents: str, debug_result: dict) -> dict | None:
        data = Utils.load_yaml(contents, debug=debug_result)
        if not data or isinstance(data, str):
            self.log.warning(f"Could not load YAML")
            return None

        instance = WorkflowInstance(data, workflow.repo)
        for job in instance.jobs:
            for step in job.steps:
                uses = step.uses
                if not uses:
                    continue
                elif uses.startswith('${{'):
                    continue

                with self.lock:
                    child_org, child_repo, child_workflow = self._create_child_workflow(uses)

                    # Create a relationship between the 2 workflows
                    self.database.workflows().link_workflows(workflow, child_workflow)

        return data

    def _create_child_workflow(self, uses: str) -> (OrgComponent, RepoComponent, WorkflowComponent):
        org = OrgComponent(uses)
        org_db = self.database.orgs().create(org)
        org.id = org_db.id

        repo = RepoComponent(uses)
        repo.org.id = org.id
        repo_db = self.database.repos().create(repo)
        repo.id = repo_db.id

        workflow = WorkflowComponent(uses)
        workflow.repo.id = repo.id
        workflow.repo.org.id = repo.org.id
        if uses.lower().startswith('docker://'):
            workflow.type = WorkflowType.DOCKER
        workflow_db = self.database.workflows().create(workflow)
        workflow.id = workflow_db.id

        return org, repo, workflow
