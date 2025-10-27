import threading
from contextlib import nullcontext
from src.commands.download.download_helper import DownloadHelper
from src.commands.service import Service
from src.github.client import GitHubClient
from src.github.exceptions import TooManyRequests, ApiRateLimitExceeded, OrgNotFound, RefNotFound, RepoNotFound
from src.libs.components.org import OrgComponent
from src.libs.components.repo import RepoComponent
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import PollStatus, RepoStatus, GitHubRefType, WorkflowStatus, WorkflowType, OrgStatus
from src.libs.exceptions import InvalidCommandLine
from src.libs.utils import Utils


class ServiceDownload(Service, DownloadHelper):
    repos: list = None
    lock: threading.Lock = None
    resume_next: bool = None
    github_client: GitHubClient = None
    all_branches: bool = None
    all_tags: bool = None
    include_forks: bool = None
    include_archived: bool = None
    threads: int = None
    only_workflows: list = None

    def run(self) -> bool:
        # Thanks SQLite3 :>
        self.lock = threading.Lock() if self.threads > 1 else nullcontext()

        while True:
            try:
                self.log.info("Collecting repositories...")
                self._collect_targets()

                self.log.info("Scanning for workflows")
                self._scan_workflows()

                self.log.info("Loading repository details")
                self._load_repository_details()

                self.log.info("Downloading workflows")
                self._download_workflows()

                self.log.info("Resolving commits to tags/branches")
                self._resolve_commits()

                break
            except (TooManyRequests, ApiRateLimitExceeded) as e:
                if self.resume_next:
                    self.github_client.halt_and_continue(5)
                    continue
                raise
            except Exception as e:
                if self.resume_next and 'Server Error' in str(e):
                    self.github_client.halt_and_continue(2)
                    continue
                raise

        if self.database.debug:
            self.log.info(f"Total SQL Queries: {self.database.total_queries}")

        self.log.info(f"Total API Calls: {self.github_client._api.total_requests}")
        return True

    def _collect_targets(self) -> None:
        orgs, repos = Utils.filter_orgs_and_repos(self.repos)
        self.log.debug(f"Input has {len(orgs)} organisations and {len(repos)} repositories")

        if len(orgs) > 0:
            if self.all_branches:
                raise InvalidCommandLine(f"--all-branches cannot be used with organisations: {orgs}")
            elif self.all_tags:
                raise InvalidCommandLine(f"--all-tags cannot be used with organisations: {orgs}")

        if self.all_branches or self.all_tags:
            repos = self._populate_branches_or_tags(repos, self.all_branches, self.all_tags)

        self._collect_orgs(orgs)
        self._collect_repos(repos)

    def _populate_branches_or_tags(self, all_repos: list[RepoComponent], fetch_branches: bool, fetch_tags: bool) -> list[RepoComponent]:
        repos = []
        refs_to_fetch = []
        if fetch_branches:
            refs_to_fetch.append(GitHubRefType.BRANCH)
        if fetch_tags:
            refs_to_fetch.append(GitHubRefType.TAG)

        for repo in all_repos:
            self.log.info(f"Fetching repo {repo}")
            repo = self._fetch_repo(repo)

            for ref_type in refs_to_fetch:
                self.log.info(f"Fetching branches/tags for {repo}")
                for batch in self.github_client.list_tags_or_branches(repo, ref_type):
                    for item in batch:
                        component = RepoComponent(str(repo))
                        component.ref = item['name']
                        component.ref_type = ref_type
                        component.ref_commit = item['commit']['sha']
                        component.visibility = repo.visibility
                        repos.append(component)

        return repos

    def _collect_orgs(self, orgs: list[OrgComponent]) -> None:
        count = 0
        for org in orgs:
            count += 1
            self.log.info(f"Processing {org} ({count}/{len(orgs)})")

            org_db = self._create_org(org)
            org.id = org_db.id

            if org_db.poll_status == PollStatus.SCANNED:
                self.log.debug(f"Organisation {org_db.name} already scanned - skipping")
                continue
            elif org_db.poll_status == PollStatus.NONE:
                self.log.info(f"Organisation {org_db.name} is new or was not marked as pending before")
                self.database.orgs().set_poll_status(org_db.id, PollStatus.PENDING)

            try:
                for batch in self.github_client.get_org_repos(org.name, self.include_forks, self.include_archived):
                    for repo in batch:
                        repo.org.id = org_db.id
                        self._save_repo(repo)
            except OrgNotFound as e:
                self.log.error(f"Organisation {org.name} not found")
                self.database.orgs().set_status(org_db.id, OrgStatus.MISSING)

            self.database.orgs().set_poll_status(org_db.id, PollStatus.SCANNED)

            self.log.trace(f"Writing to database...")
            self.database.commit()

        self.log.trace(f"Writing to database...")
        self.database.commit()

    def _collect_repos(self, repos: list[RepoComponent]) -> None:
        count = 0
        batch_size = 100
        i = 0
        for batch in Utils.split_list(repos, self.threads):
            count += len(batch)
            i += len(batch)

            self.log.info(f"Processing ({count}/{len(repos)}) repositories")
            if len(batch) == 1:
                self._save_repo(batch[0])
            else:
                arguments = [(repo,) for repo in batch]
                Utils.multithread(self._save_repo, arguments)

            if i >= batch_size:
                i = 0
                self.log.trace(f"Writing to database...")
                self.database.commit()

        self.log.trace(f"Writing to database...")
        self.database.commit()

    def _save_repo(self, repo: RepoComponent) -> None:
        with self.lock:
            self.log.info(f"Saving repository {repo}")
            if repo.org.id == 0:
                repo.org.id = self._create_org(repo.org).id

            if len(repo.ref) > 0:
                repo.poll_status = PollStatus.PENDING
                repo_db = self.database.repos().create(repo)
                return

            # At this point, there is no `ref` in the object.
            # Search if the repo is already in the database.
            repo_db = self.database.repos().find(repo.org.id, repo.name, None)
            if self._repo_already_stored(repo_db):
                return

        # Either there's no database record, or the stored one also has an empty ref.
        fresh_repo = self._fetch_repo(repo)
        with self.lock:
            if fresh_repo.org.name.lower() == repo.org.name.lower() and fresh_repo.name.lower() == repo.name.lower():
                fresh_repo.org.id = repo.org.id
                fresh_repo.poll_status = PollStatus.SCANNED if repo.status == RepoStatus.MISSING else PollStatus.PENDING
                if repo_db:
                    fresh_repo.id = repo_db.id
                    self.database.repos().update(fresh_repo)
                else:
                    self.database.repos().create(fresh_repo)
                return

            # Here, the fetched repo is different to the one passed to the function, this happens when a repo is redirected.
            fresh_repo.org.id = self._create_org(fresh_repo.org).id
            fresh_repo_db = self.database.repos().create(fresh_repo)

            repo.redirect_id = fresh_repo_db.id
            repo.status = RepoStatus.REDIRECT
            self.database.repos().create(repo)

    def _resolve_commits(self) -> None:
        while True:
            batch = self.database.next_commit_to_resolve(self.threads)
            if not batch:
                break

            if self.threads == 1:
                self._resolve_commit(batch)
            else:
                arguments = [(repo,) for repo in batch]
                Utils.multithread(self._resolve_commit, arguments)

            self.database.commit()

    def _resolve_commit(self, repo: RepoComponent) -> None:
        # First search for a tag (most likely).
        self.log.info(f"Trying to find a tag with commit {repo.ref} in {repo}")
        ref = self.github_client.get_tag_from_commit(repo, repo.ref_commit)
        ref_type = GitHubRefType.TAG
        if not ref:
            self.log.info(f"Trying to find a branch with commit {repo.ref} in {repo}")
            ref = self.github_client.get_branch_from_commit(repo, repo.ref_commit)
            ref_type = GitHubRefType.BRANCH
            if not ref:
                self.log.warning(f"Could not resolve commit {repo.ref} in {repo}")
                with self.lock:
                    self.database.repos().set_ref_resolved_fields(repo.id, '', GitHubRefType.MISSING)
                return None
            else:
                self.log.info(f"Found branch {ref} with commit {repo.ref} in {repo}")
        else:
            self.log.info(f"Found tag {ref} with commit {repo.ref} in {repo}")

        with self.lock:
            self.database.repos().set_ref_resolved_fields(repo.id, ref, ref_type)
        return None

    def _scan_workflows(self) -> None:
        while True:
            batch = self.database.next_repo_to_scan(self.threads)
            if not batch:
                break

            if self.threads == 1:
                self._scan_repo_workflows(batch)
            else:
                arguments = [(repo,) for repo in batch]
                Utils.multithread(self._scan_repo_workflows, arguments)

            self.database.commit()

    def _scan_repo_workflows(self, repo: RepoComponent) -> None:
        self.log.info(f"Searching for workflows in {repo}")
        workflows = self._ls_workflows(repo, self.only_workflows)

        with self.lock:
            if len(workflows) > 0:
                for workflow in workflows:
                    self.log.debug(f"\tSaving {workflow}")
                    workflow_db = self._create_workflow(workflow)
            else:
                self.database.repos().set_status(repo.id, RepoStatus.NO_WORKFLOWS)

            self.database.repos().set_poll_status(repo.id, PollStatus.SCANNED)

    def _download_workflows(self) -> None:
        while True:
            batch = self.database.next_workflow_to_download(self.threads)
            if not batch:
                break

            if self.threads == 1:
                self._download_single_workflow(batch)
            else:
                arguments = [(workflow,) for workflow in batch]
                Utils.multithread(self._download_single_workflow, arguments)

            self.database.commit()

    def _download_single_workflow(self, workflow: WorkflowComponent) -> None:
        self.log.info(f"Downloading {workflow}")
        if not self._fulfill_repo(workflow.repo):
            with self.lock:
                self._mark_missing(workflow)
            return None

        previous_type = workflow.type
        previous_path = workflow.path
        contents = self._download(workflow)
        if previous_type != workflow.type or previous_path != workflow.path:
            with self.lock:
                self.database.workflows().update_type_and_path(workflow)

        if contents is None:
            # Could not download file - could happen for many reasons, one of which
            # is that it's a submodule.
            self.log.info(f"Could not find {workflow} - checking if it's a submodule")
            submodule = self.github_client.get_submodule(workflow)
            if submodule is None:
                self.log.warning(f"Workflow {workflow} not found")
                with self.lock:
                    self._mark_missing(workflow)
                return None

            self.log.info(f"Found submodule {submodule}")
            with self.lock:
                # Mark the workflow as 'submodule'.
                self.database.workflows().update_status(workflow.id, WorkflowStatus.SUBMODULE)

                # Create the new submodule workflow.
                submodule_org = self._create_org(submodule.repo.org)
                submodule.repo.org.id = submodule_org.id

                submodule_repo = self._create_repo(submodule.repo)
                submodule.repo.id = submodule_repo.id

                submodule_workflow = self._create_workflow(submodule)

                # Set the parent workflow's redirect_id to the new submodule workflow.
                workflow.redirect_id = submodule_workflow.id
                self.database.workflows().update_redirect_id(workflow.id, workflow.redirect_id)
                return None

        data = {} if contents else None
        debug = {'error': ''}
        if workflow.type != WorkflowType.DOCKER:
            data = self._process_contents(workflow, contents, debug)

        with self.lock:
            if data is None:
                self.database.workflows().update_contents(workflow.id, contents, debug['error'])
                self.database.workflows().update_status(workflow.id, WorkflowStatus.ERROR)
            else:
                self.database.workflows().update_contents(workflow.id, contents, data)
                self.database.workflows().update_status(workflow.id, WorkflowStatus.DOWNLOADED)

        return None

    def _load_repository_details(self) -> None:
        while True:
            batch = self.database.next_repo_to_fulfill(self.threads)
            if not batch:
                break

            if self.threads == 1:
                self._fulfill_repo(batch)
            else:
                arguments = [(repo,) for repo in batch]
                Utils.multithread(self._fulfill_repo, arguments)

            self.database.commit()

    def _fulfill_repo(self, repo: RepoComponent) -> bool:
        if repo.is_fulfilled():
            return True

        try:
            self.log.info(f"Validating repo {repo}")
            self.github_client.fulfill_component(repo)

            with self.lock:
                self.database.repos().update(repo)
            return True
        except (RefNotFound, RepoNotFound) as e:
            self.log.error(f"Repo {repo}@{repo.ref} not found")
            with self.lock:
                self.database.repos().set_status(repo.id, RepoStatus.MISSING)
        return False
