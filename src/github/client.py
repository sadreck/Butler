import re
import base64
import time
from loguru import logger
from src.github.api import GitHubApi
from src.github.exceptions import (
    AccountNotFound, UnknownAccountType, HttpNotFound, GitHubException, HttpEmptyRepo, HttpAccessBlocked,
    HttpNoCommitFound, HttpInvalidState, HttpInvalidRequest, RepoNotFound, RefNotFound, ErrorDownloadingFile
)
from src.libs.components.repo import RepoComponent
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import RepoVisibility, GitHubRefType, RepoStatus


class GitHubClient:
    _api: GitHubApi = None
    log: logger = None

    def __init__(self, access_tokens: list[str], log: logger):
        self.log = log
        self._api = GitHubApi(access_tokens, log)

    def get_account_type(self, account_name: str) -> str:
        return self.get_account(account_name).get('type', '').lower()

    def get_account(self, account_name: str) -> dict:
        return self._api.get(f'/users/{account_name}')

    def get_org_repos(self, account_name: str, include_forks: bool, include_archived: bool) -> list:
        account_type = self.get_account_type(account_name)
        if len(account_type) == 0:
            raise AccountNotFound(account_name)
        elif account_type not in ['organization', 'user']:
            raise UnknownAccountType(account_name)

        params = {'per_page': 100, 'sort': 'full_name'}
        fork_repos = 0
        archived_repos = 0
        count = 0
        account_type = 'orgs' if account_type == 'organization' else 'users'
        url = f'/{account_type}/{account_name}/repos'
        while True:
            response_headers = {}
            try:
                page_repos = self._api.get(url, params, None, response_headers)
            except HttpNotFound:
                # This shouldn't happen as we're getting the org/account above, but it's happened a couple of times.
                raise AccountNotFound(account_name)

            repos = []
            for repo in page_repos:
                count += 1
                self.log.info(f"[{count}] Loading {repo['full_name']}")

                if repo['fork']:
                    fork_repos += 1
                    if not include_forks:
                        continue

                if repo['archived']:
                    archived_repos += 1
                    if not include_archived:
                        continue

                repos.append(self._load_repo_component(repo))

            if len(repos) > 0:
                yield repos

            # Invalidate as we'll be using the 'next url' from the headers.
            params = None
            url = self._get_next_url(response_headers)
            if not url:
                break

    def _load_repo_component(self, data: dict) -> RepoComponent:
        repo = RepoComponent(data['full_name'])
        repo.visibility = RepoVisibility.PRIVATE if data['private'] else RepoVisibility.PUBLIC
        repo.ref = data['default_branch']
        repo.ref_type = GitHubRefType.BRANCH
        repo.stars = data['stargazers_count']
        repo.fork = data['fork']
        repo.archive = data['archived']
        return repo

    def _get_next_url(self, headers: dict) -> str | None:
        header = headers.get('Link', headers.get('link', ''))
        if len(header) == 0:
            return None

        pattern = r'(?<=<)([\S]*)(?=>; rel="next")'
        match = re.search(pattern, header, re.IGNORECASE)
        if not match:
            return None
        return match.group(1).strip()

    def ls(self, repo: RepoComponent, path: str) -> list[str]:
        listing = self._get_path_or_file_info(repo, path)
        if not isinstance(listing, list):
            return []
        return [file['path'] for file in listing]

    def file(self, workflow: WorkflowComponent) -> dict:
        return self._get_path_or_file_info(workflow.repo, workflow.path)

    def _get_path_or_file_info(self, repo: RepoComponent, path: str) -> list | dict:
        url = f"/repos/{repo.org.name}/{repo.name}/contents/{path.lstrip('/')}"
        params = {} if len(repo.ref) == 0 else {'ref': repo.ref}
        return self._api.get(url, params)

    def get_repo(self, repo: RepoComponent, return_component: bool) -> dict:
        data = self._api.get(f'/repos/{repo.org.name}/{repo.name}')
        return self._load_repo_component(data) if return_component else data

    def get_tag(self, repo: RepoComponent, sha: str) -> str:
        data = self._api.get(f'/repos/{repo.org.name}/{repo.name}/git/tags/{sha}')
        return data.get('tag', '')

    def _identify_ref(self, repo: RepoComponent) -> dict:
        result = {
            'type': GitHubRefType.UNKNOWN,
            'sha': None
        }
        if len(repo.ref) == 0:
            return result
        elif repo.is_fulfilled():
            result['type'] = repo.ref_type
            result['sha'] = repo.ref_commit
            return result

        # Check for a commit first to save some API calls.
        if len(repo.ref) == 40:
            commit = self._get_git_commit(repo, repo.ref)
            if commit:
                self.log.trace(f"{repo.ref} is a commit for {repo}")
                result['type'] = GitHubRefType.COMMIT
                result['sha'] = commit['sha']
                return result

        branch = self._get_git_ref(repo, f'heads/{repo.ref}')
        if branch:
            self.log.trace(f"{repo.ref} is a branch for {repo}")
            result['type'] = GitHubRefType.BRANCH
            result['sha'] = branch['object']['sha']
            return result

        tag = self._get_git_ref(repo, f"tags/{repo.ref}")
        if tag:
            self.log.trace(f"{repo.ref} is a tag for {repo}")
            result['type'] = GitHubRefType.TAG
            result['sha'] = tag['object']['sha']
            return result

        # We check the commit again, as it could be a shorthand.
        commit = self._get_git_commit(repo, repo.ref)
        if commit:
            self.log.trace(f"{repo.ref} is a commit for {repo}")
            result['type'] = GitHubRefType.COMMIT
            result['sha'] = commit['sha']
            return result

        return result

    def _get_git_ref(self, repo: RepoComponent, ref: str) -> dict | None:
        try:
            return self._api.get(f'/repos/{repo.org.name}/{repo.name}/git/ref/{ref}')
        except GitHubException:
            return None

    def _get_git_commit(self, repo: RepoComponent, sha: str) -> dict | None:
        try:
            return self._api.get(f"/repos/{repo.org.name}/{repo.name}/commits/{sha}")
        except GitHubException:
            return None

    def _get_git_tag(self, repo: RepoComponent, sha: str) -> str | None:
        try:
            data = self._api.get(f"/repos/{repo.org.name}/{repo.name}/git/tags/{sha}")
            return data.get('tag', None)
        except GitHubException:
            return None

    def _get_repo_status_from_exception(self, e: Exception) -> RepoStatus:
        if isinstance(e, HttpEmptyRepo):
            return RepoStatus.EMPTY
        elif isinstance(e, HttpAccessBlocked):
            return RepoStatus.BLOCKED
        elif isinstance(e, HttpNotFound):
            return RepoStatus.MISSING
        elif isinstance(e, HttpNoCommitFound):
            return RepoStatus.COMMIT_MISSING
        elif isinstance(e, HttpInvalidRequest):
            return RepoStatus.INVALID_REQUEST
        elif isinstance(e, HttpInvalidState):
            return RepoStatus.GIT_ERROR
        return RepoStatus.UNKNOWN

    def fulfill_component(self, repo: RepoComponent) -> bool:
        try:
            data = self.get_repo(repo, False)
            if len(repo.ref) == 0:
                repo.ref = data.get('default_branch', '')
            repo.visibility = RepoVisibility.PRIVATE if data['private'] else RepoVisibility.PUBLIC
            repo.status = RepoStatus.OK
            repo.stars = data['stargazers_count']
            repo.fork = data['fork']
            repo.archive = data['archived']
        except Exception as e:
            repo.status = self._get_repo_status_from_exception(e)
            raise RepoNotFound(str(repo))

        ref_info = self._identify_ref(repo)
        if ref_info['type'] != GitHubRefType.UNKNOWN:
            # This will update the passed object as well.
            repo.ref_type = ref_info['type']
            repo.ref_commit = ref_info['sha']
            repo.status = RepoStatus.OK
            return True

        # Sometimes the passed commit is a reference to a signed tag which is not directly accessible through the UI.
        # For example:
        #   aws-actions/configure-aws-credentials@5579c002bb4778aa43395ef1df492868a9a1c83f
        # That is the hash of the v4.0.2 tag which is e3dd6a429d7300a6a4c196c26e071d42e0343502.
        # However, when it's signed it's assigned a different hash. Since we couldn't download the file using the first
        # hash, we must check if this is why by trying to figure out if it's a tag.

        # If tag is missing it will throw an exception.
        try:
            tag = self._get_git_tag(repo, repo.ref)
            if tag:
                self.log.debug(f"Found tag {tag} for {repo.ref} in {repo}")
                repo.ref_commit = repo.ref
                repo.ref = str(tag) if tag is not None else ''
                repo.ref_type = GitHubRefType.TAG
                repo.status = RepoStatus.OK
                return True
        except GitHubException as e:
            pass

        raise RefNotFound(str(repo))

    def download(self, workflow: WorkflowComponent, path: str = None) -> str | None:
        url = workflow.download_url(path)
        is_authenticated = workflow.repo.visibility == RepoVisibility.PRIVATE
        try:
            contents = self._api.get(url, authenticated=is_authenticated)
            # If it's via the API the contents will be base64 encoded.
            if is_authenticated:
                contents = base64.b64decode(contents['content']).decode('utf-8')
            return contents
        except HttpNotFound:
            raise ErrorDownloadingFile(f"Could not download file for {workflow}")

    def download_action(self, workflow: WorkflowComponent) -> str | None:
        contents = None
        for action_file in ['action.yml', 'action.yaml', 'Dockerfile']:
            try:
                path = action_file
                if workflow.path:
                    path = f"{workflow.path}/{action_file}"
                contents = self.download(workflow, path)
                workflow.add_action_file_to_path(action_file)
                workflow.update_workflow_type()
                break
            except ErrorDownloadingFile:
                # Nothing.
                pass
        return contents

    def get_submodule(self, workflow: WorkflowComponent) -> WorkflowComponent | None:
        try:
            file = self.file(workflow)
        except HttpNotFound:
            return None

        if isinstance(file, list):
            self.log.warning(f"It's a path, not a file: {str(workflow)}")
            return None
        elif file.get('type', '') != 'submodule':
            return None

        submodule = WorkflowComponent(file['html_url'])
        # If the incoming component is an action, set the submodule to the same, etc.
        submodule.type = workflow.type
        return submodule

    def get_tag_from_commit(self, repo: RepoComponent, commit: str) -> str | None:
        for batch in self.list_tags_or_branches(repo, GitHubRefType.TAG):
            for ref in batch:
                if commit == ref.get('commit', {}).get('sha', ''):
                    return ref['name']
        return None

    def get_branch_from_commit(self, repo: RepoComponent, commit: str) -> str | None:
        for batch in self.list_tags_or_branches(repo, GitHubRefType.BRANCH):
            for ref in batch:
                if commit == ref.get('commit', {}).get('sha', ''):
                    return ref['name']
        return None

    def list_tags_or_branches(self, repo: RepoComponent, ref_type: GitHubRefType) -> list[dict]:
        url = f"/repos/{repo.org.name}/{repo.name}/"
        url += 'branches' if ref_type == GitHubRefType.BRANCH else 'tags'

        params = {'per_page': 100}
        while True:
            response_headers = {}
            try:
                page_data = self._api.get(url, params, None, response_headers)
            except HttpNotFound:
                raise RepoNotFound(str(repo))

            yield page_data

            params = None
            url = self._get_next_url(response_headers)
            if not url:
                break

    def halt_and_continue(self, minutes: int) -> None:
        self._api.refresh_tokens()
        if not self._api.has_valid_token():
            self.log.info(f"Reached API rate limit - waiting {minutes} minutes")
            time.sleep(minutes * 60)
            self._api.refresh_tokens()
