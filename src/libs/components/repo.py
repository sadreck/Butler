from src.libs.components.base import BaseComponent
from src.libs.components.org import OrgComponent
from src.libs.constants import GitHubRefType, RepoVisibility, PollStatus, RepoStatus
from src.libs.exceptions import InvalidRepoFormat


class RepoComponent(BaseComponent):
    _id: int = None
    _org: OrgComponent = None
    _redirect_id: int = None
    _name: str = None
    _ref: str = None
    _ref_type: GitHubRefType = None
    _ref_commit: str = None
    _resolved_ref: str = None
    _resolved_ref_type: GitHubRefType = None
    _visibility: RepoVisibility = None
    _poll_status: PollStatus = None
    _status: RepoStatus = None
    _stars: int = None
    _fork: bool = None
    _archive: bool = None

    @property
    def id(self) -> int:
        return self._id or 0

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def org(self) -> OrgComponent:
        return self._org

    @property
    def name(self) -> str:
        return self._name or ''

    @property
    def redirect_id(self) -> int:
        return self._redirect_id or 0

    @redirect_id.setter
    def redirect_id(self, value: int):
        self._redirect_id = value

    @property
    def ref(self) -> str:
        return self._ref or ''

    @ref.setter
    def ref(self, value: str):
        self._ref = value

    @property
    def ref_type(self) -> GitHubRefType:
        return self._ref_type or GitHubRefType.UNKNOWN

    @ref_type.setter
    def ref_type(self, value: GitHubRefType):
        self._ref_type = value

    @property
    def resolved_ref(self) -> str:
        return self._resolved_ref or ''

    @resolved_ref.setter
    def resolved_ref(self, value: str):
        self._resolved_ref = value

    @property
    def resolved_ref_type(self) -> GitHubRefType:
        return self._resolved_ref_type or GitHubRefType.UNKNOWN

    @resolved_ref_type.setter
    def resolved_ref_type(self, value: GitHubRefType):
        self._resolved_ref_type = value

    @property
    def ref_commit(self) -> str:
        return self._ref_commit or ''

    @ref_commit.setter
    def ref_commit(self, value: str):
        self._ref_commit = value

    @property
    def visibility(self) -> RepoVisibility:
        return self._visibility or RepoVisibility.NONE

    @visibility.setter
    def visibility(self, value: RepoVisibility):
        self._visibility = value

    @property
    def poll_status(self) -> PollStatus:
        return self._poll_status or PollStatus.NONE

    @poll_status.setter
    def poll_status(self, value: PollStatus):
        self._poll_status = value

    @property
    def status(self) -> RepoStatus:
        return self._status or RepoStatus.NONE

    @status.setter
    def status(self, value: RepoStatus):
        self._status = value

    @property
    def stars(self) -> int:
        return self._stars or 0

    @stars.setter
    def stars(self, value: int):
        self._stars = value

    @property
    def fork(self) -> bool:
        return self._fork or False

    @fork.setter
    def fork(self, value: bool):
        self._fork = value

    @property
    def archive(self):
        return self._archive or False

    @archive.setter
    def archive(self, value: bool):
        self._archive = value

    @property
    def source(self):
        return self.fork is False and self.archive is False

    def __init__(self, name: str):
        info = self._parse_component(name)
        if len(info['org']) == 0 or len(info['repo']) == 0:
            raise InvalidRepoFormat(f"Invalid repo component name: {name}")

        self._org = OrgComponent(info['org'])
        self._name = info['repo']
        self._ref = info['ref']

    def __str__(self) -> str:
        return self.org.name + '/' + self.name

    def is_fulfilled(self) -> bool:
        if self.ref_type == GitHubRefType.UNKNOWN:
            return False
        elif len(self.ref_commit) == 0:
            return False
        elif self.visibility == RepoVisibility.NONE:
            return False
        elif self.status == RepoStatus.NONE:
            return False
        return True

    @classmethod
    def from_dict(cls, data: dict):
        required_keys = [
            'org_id',
            'org_name',
            'repo_id',
            'repo_visibility',
            'repo_name',
            'repo_ref',
            'repo_ref_type',
            'repo_ref_commit',
            'repo_resolved_ref',
            'repo_resolved_ref_type',
            'repo_status',
            'repo_poll_status',
            'repo_redirect_id',
            'repo_stars',
            'repo_fork',
            'repo_archive',
        ]

        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")

        instance = cls(f"{data['org_name']}/{data['repo_name']}@{data['repo_ref']}")
        instance.org.id = data['org_id']
        instance.id = data['repo_id']
        instance.visibility = data['repo_visibility']
        instance.ref_type = data['repo_ref_type']
        instance.ref_commit = data['repo_ref_commit']
        instance.resolved_ref = data['repo_resolved_ref']
        instance.resolved_ref_type = data['repo_resolved_ref_type']
        instance.status = data['repo_status']
        instance.poll_status = data['repo_poll_status']
        instance.redirect_id = data['repo_redirect_id']
        instance.stars = data['repo_stars']
        instance.fork = data['repo_fork']
        instance.archive = data['repo_archive']
        return instance
