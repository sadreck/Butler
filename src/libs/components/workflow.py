import json
from src.libs.components.base import BaseComponent
from src.libs.components.repo import RepoComponent
from src.libs.constants import WorkflowType, RepoStatus, RepoVisibility, GitHubRefType
from src.libs.utils import Utils


class WorkflowComponent(BaseComponent):
    _id: int = None
    _repo: RepoComponent = None
    _redirect_id: int = None
    _path: str = None
    _type: WorkflowType = None
    _contents: str = None
    _data: dict | list = None
    _status: RepoStatus = None

    @property
    def id(self) -> int:
        return self._id or 0

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def repo(self) -> RepoComponent:
        return self._repo

    @repo.setter
    def repo(self, value: RepoComponent):
        self._repo = value

    @property
    def redirect_id(self) -> int:
        return self._redirect_id or 0

    @redirect_id.setter
    def redirect_id(self, value: int):
        self._redirect_id = value

    @property
    def path(self) -> str:
        return self._path or ''

    @path.setter
    def path(self, value: str):
        self._path = value

    @property
    def type(self) -> WorkflowType:
        return self._type or WorkflowType.NONE

    @type.setter
    def type(self, value: WorkflowType):
        self._type = value

    @property
    def type_name(self) -> str:
        return WorkflowType(self.type).name.lower()

    @property
    def status(self) -> RepoStatus:
        return self._status or RepoStatus.NONE

    @status.setter
    def status(self, value: RepoStatus):
        self._status = value

    @property
    def contents(self) -> str:
        return self._contents or ''

    @contents.setter
    def contents(self, value: str):
        self._contents = value

    @property
    def data(self) -> dict | list | None:
        return self._data

    @data.setter
    def data(self, value: dict | list | None):
        self._data = value

    @property
    def data_string(self) -> str:
        return json.dumps(self.data) if self.data else ''

    def __init__(self, name: str):
        info = self._parse_component(name)
        self._repo = RepoComponent(name)
        self._path = info['path']
        self.update_workflow_type()

    def _detect_workflow_type(self) -> WorkflowType:
        if self.path.endswith('Dockerfile'):
            return WorkflowType.DOCKER
        elif self.path.endswith('action.yml') or self.path.endswith('action.yaml'):
            return WorkflowType.ACTION
        elif Utils.is_yaml_extension(self.path):
            return WorkflowType.WORKFLOW
        return WorkflowType.ACTION

    def update_workflow_type(self) -> None:
        self._type = self._detect_workflow_type()

    def download_url(self, path: str = None, ref: str = None) -> str | None:
        path = path or self.path
        ref = ref or self.repo.ref

        if path is None or ref is None:
            return None
        elif len(path) == 0 or len(ref) == 0:
            return None
        elif len(self.repo.org.name) == 0 or len(self.repo.name) == 0:
            return None

        ref_path = ''
        if self.repo.ref_type == GitHubRefType.BRANCH:
            ref_path = 'refs/heads/'
        elif self.repo.ref_type == GitHubRefType.TAG:
            ref_path = 'refs/tags/'

        if self.repo.visibility == RepoVisibility.PUBLIC:
            # return f"https://raw.githubusercontent.com/{self.repo.org.name}/{self.repo.name}/{ref}/{path.lstrip('/')}"
            return f"https://raw.githubusercontent.com/{self.repo.org.name}/{self.repo.name}/{ref_path}{ref}/{path.lstrip('/')}"
        return f"https://api.github.com/repos/{self.repo.org.name}/{self.repo.name}/contents/{path.lstrip('/')}?ref={ref}"

    def browser_url(self) -> str:
        return f'https://github.com/{self.repo.org.name}/{self.repo.name}/blob/{self.repo.ref}/{self.path}'

    def __str__(self) -> str:
        name = str(self.repo)
        if len(self.path) > 0:
            name += f'/{self.path}'
        name += '' if len(self.repo.ref) == 0 else f"@{self.repo.ref}"
        return name

    def action_name(self) -> str:
        name = str(self.repo)
        if len(self.path) > 0:
            name += f'/{self.path}'

        if name.endswith('/action.yml'):
            name = name[:-len('/action.yml')]
        elif name.endswith('/action.yaml'):
            name = name[:-len('/action.yaml')]
        elif name.endswith('/Dockerfile'):
            name = name[:-len('/Dockerfile')]

        return name

    @classmethod
    def from_dict(cls, data: dict, includes_contents: bool = True):
        required_keys = [
            'org_name',
            'repo_name',
            'repo_ref',
            'repo_ref_type',
            'repo_resolved_ref',
            'repo_resolved_ref_type',
            'workflow_id',
            'workflow_redirect_id',
            'workflow_path',
            'workflow_type',
            'workflow_status',
        ]

        if includes_contents:
            required_keys.append('workflow_data')
            required_keys.append('workflow_contents')

        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {missing_keys}")

        instance = cls(f"{data['org_name']}/{data['repo_name']}/{data['workflow_path']}@{data['repo_ref']}")
        instance.id = data['workflow_id']
        instance.redirect_id = data['workflow_redirect_id']
        instance.type = data['workflow_type']
        instance.status = data['workflow_status']
        if includes_contents:
            instance.data = Utils.load_json(data['workflow_data'], None)
            instance.content = data['workflow_contents']
        instance.repo = RepoComponent.from_dict(data)
        instance.repo.ref_type = data['repo_ref_type']
        instance.repo.resolved_ref = data['repo_resolved_ref']
        instance.repo.resolved_ref_type = data['repo_resolved_ref_type']
        return instance

    def add_action_file_to_path(self, filename: str) -> None:
        self.path = filename if len(self.path) == 0 else f'{self.path.rstrip("/")}/{filename}'

    def url(self, permalink: bool = False) -> str:
        ref = self.repo.ref_commit if permalink else self.repo.ref
        return f"https://github.com/{self.repo.org.name}/{self.repo.name}/blob/{ref}/{self.path}"
