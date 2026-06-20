import threading
import concurrent.futures
from contextlib import nullcontext
from src.database.models import OrganisationModel, RepositoryModel
from src.libs.constants import SecretVariableCategory, SecretVariableType, SecretVariableVisibility
from src.libs.components.secvar import SecretVariableComponent
from src.commands.download.download_helper import DownloadHelper
from src.commands.service import Service
from src.github.client import GitHubClient
from src.github.exceptions import TooManyRequests, ApiRateLimitExceeded, OrgNotFound
from src.libs.components.org import OrgComponent
from src.libs.constants import PollStatus, OrgStatus
from src.libs.exceptions import InvalidCommandLine
from src.libs.utils import Utils


class ServiceSecretsAndVariables(Service, DownloadHelper):
    org: str = None
    lock: threading.Lock = None
    resume_next: bool = None
    github_client: GitHubClient = None
    threads: int = None

    _combinations: list = [
        {'label': 'actions / secrets', 'category': SecretVariableCategory.ACTIONS, 'type': SecretVariableType.SECRET},
        {'label': 'actions / variables', 'category': SecretVariableCategory.ACTIONS, 'type': SecretVariableType.VARIABLE},
        {'label': 'agents / secrets', 'category': SecretVariableCategory.AGENTS, 'type': SecretVariableType.SECRET},
        {'label': 'agents / variables', 'category': SecretVariableCategory.AGENTS, 'type': SecretVariableType.VARIABLE},
        {'label': 'dependabot / secrets', 'category': SecretVariableCategory.DEPENDABOT, 'type': SecretVariableType.SECRET},
    ]

    def run(self) -> bool:
        # Thanks SQLite3 :>
        self.lock = threading.Lock() if self.threads > 1 else nullcontext()

        while True:
            try:
                self.log.info(f"Collecting repositories for {self.org}...")
                self._collect_targets()

                org = self.database.orgs().find(self.org)
                if not org:
                    raise InvalidCommandLine(f"Organisation {self.org} not found")

                self.log.info(f"Collecting secrets and variables for {org.name}")
                self._collect_secrets_and_variables(org)

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
        orgs, repos = Utils.filter_orgs_and_repos([self.org])
        self.log.debug(f"Input has {len(orgs)} organisations and {len(repos)} repositories")
        self._collect_orgs(orgs)

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
                for batch in self.github_client.get_org_repos(org.name, True, True):
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

    def _collect_secrets_and_variables(self, org: OrganisationModel) -> None:
        components = []
        for item in self._combinations:
            self.log.info(f"Getting organisation {item['label']}")
            try:
                results = self.github_client.get_secrets(org.name, item['category'], item['type'], None, None)
                components.extend(self._create_components(org.id, results, item['category'], item['type']))
            except Exception as e:
                self.log.warning(f"Could not get {item['label']}")

        self.log.info(f"Writing to database")
        for component in components:
            self.database.secvars().create(0, component)

        self.database.commit()

        self.log.info(f"Getting organisation repos")
        repos = self.database.repos().all(org.id)
        self.log.info(f"Got {len(repos)} repos")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit all repositories to the executor
            future_to_repo = {executor.submit(self._fetch_secvar_repo_single, org, repo): repo for repo in repos}

            for future in concurrent.futures.as_completed(future_to_repo):
                repo = future_to_repo[future]
                try:
                    # Retrieve the data returned by fetch_repo_data
                    returned_repo, components = future.result()

                    # 3. Write to the database safely in the main thread
                    if components:
                        self.log.info(f"Writing {len(components)} components to database for {returned_repo.name}")
                        with self.lock:
                            for component in components:
                                self.database.secvars().create(repo.id, component)

                            self.database.commit()

                except Exception as e:
                    self.log.error(f"Unhandled exception processing repo {repo.name}: {e}")

    def _fetch_secvar_repo_single(self, org: OrganisationModel, repo: RepositoryModel) -> tuple[object, list]:
        components = []
        self.log.info(f"Getting secrets and variables for {repo.name}")
        for item in self._combinations:
            self.log.info(f"Getting data for repo {repo.name} and {item['label']}")
            try:
                results = self.github_client.get_secrets(org.name, item['category'], item['type'], None, repo.name)
                components.extend(self._create_components(org.id, results, item['category'], item['type']))
            except Exception as e:
                self.log.warning(f"Could not get {item['label']} for {repo.name}")

        return repo, components

    def _create_components(self, org_id: int, items: list, category: SecretVariableCategory, type: SecretVariableType) -> list[SecretVariableComponent]:
        components = []
        for item in items:
            component = SecretVariableComponent()
            component.category = category
            component.type = type
            component.name = item['name']
            if component.type == SecretVariableType.VARIABLE:
                component.value = item['value']
            component.created_at = item['created_at']
            component.updated_at = item['updated_at']

            if 'visibility' in item:
                match item['visibility']:
                    case 'all':
                        component.visibility = SecretVariableVisibility.ALL
                    case 'private':
                        component.visibility = SecretVariableVisibility.PRIVATE
                    case 'selected':
                        component.visibility = SecretVariableVisibility.SELECTED

                        repos = []
                        for repo in item['repos']:
                            repo = self.database.repos().find(org_id, repo, None)
                            repos.append(repo)
                        component.repos = repos

            components.append(component)
        return components
