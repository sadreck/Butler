import hashlib
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import GitHubRefType


class ThirdPartyInstance:
    action: WorkflowComponent = None
    workflow: WorkflowComponent = None
    trusted: bool = None
    name: str = None
    usage: int = None
    tags: dict = None
    branches: dict = None
    commits: dict = None
    stars: int = None

    @property
    def stars_formatted(self) -> str:
        if self.stars < 1000:
            return str(self.stars)
        stars = self.stars / 1000
        return f"{stars:.1f}k".rstrip("0").rstrip(".")

    def __init__(self, action: WorkflowComponent, workflow: WorkflowComponent) -> None:
        self.trusted = False
        self.name = ''
        self.usage = 0
        self.tags = {}
        self.branches = {}
        self.commits = {}
        self.action = action
        self.workflow = workflow
        self.stars = 0

    def refs(self) -> dict:
        return self.tags | self.branches | self.commits

    def increment_usage(self) -> int:
        self.usage += 1
        return self.usage

    def add_tag(self, tag: str, is_deprecated: bool, title: str, commit: str) -> dict:
        if tag not in self.tags:
            self.tags[tag] = {
                'label': 'Tag',
                'type': 'tag',
                'resolved_ref': commit,
                'resolved_type': GitHubRefType(GitHubRefType.COMMIT).name.lower(),
                'deprecated': is_deprecated,
                'title': title,
                'usage': 0,
                'url': f'https://github.com/{self.action.repo.org.name}/{self.action.repo.name}/tree/{tag}/{self.action.path}',
                'permalink_url': f'https://github.com/{self.action.repo.org.name}/{self.action.repo.name}/tree/{commit}/{self.action.path}',
                'workflows': {},
                'unique': hashlib.md5(f"{self.name}-{tag}".encode()).hexdigest(),
            }
            self.tags = dict(sorted(self.tags.items()))
        self.tags[tag]['usage'] += 1
        return self.tags[tag]

    def add_branch(self, branch: str, is_deprecated: bool, title: str, commit: str) -> dict:
        if branch not in self.branches:
            self.branches[branch] = {
                'label': 'Branch',
                'type': 'branch',
                'resolved_ref': commit,
                'resolved_type': GitHubRefType(GitHubRefType.COMMIT).name.lower(),
                'deprecated': is_deprecated,
                'title': title,
                'usage': 0,
                'url': f'https://github.com/{self.action.repo.org.name}/{self.action.repo.name}/tree/{branch}/{self.action.path}',
                'permalink_url': f'https://github.com/{self.action.repo.org.name}/{self.action.repo.name}/tree/{commit}/{self.action.path}',
                'workflows': {},
                'unique': hashlib.md5(f"{self.name}-{branch}".encode()).hexdigest(),
            }
            self.branches = dict(sorted(self.branches.items()))
        self.branches[branch]['usage'] += 1
        return self.branches[branch]

    def add_commit(self, commit: str, resolved_ref: str, resolved_ref_type: GitHubRefType, is_deprecated: bool, title: str) -> dict:
        if commit not in self.commits:
            self.commits[commit] = {
                'label': 'Commit',
                'type': 'commit',
                'resolved_ref': 'unknown' if resolved_ref == '' else resolved_ref,
                'resolved_type': GitHubRefType(resolved_ref_type).name.lower(),
                'deprecated': is_deprecated,
                'title': title,
                'usage': 0,
                'url': f'https://github.com/{self.action.repo.org.name}/{self.action.repo.name}/tree/{commit}/{self.action.path}',
                'permalink_url': f'https://github.com/{self.action.repo.org.name}/{self.action.repo.name}/tree/{commit}/{self.action.path}',
                'workflows': {},
                'unique': hashlib.md5(f"{self.name}-{commit}".encode()).hexdigest(),
            }
            self.commits = dict(sorted(self.commits.items()))
        self.commits[commit]['usage'] += 1
        return self.commits[commit]
