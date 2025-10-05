from src.libs.components.repo import RepoComponent


class InstanceBase:
    _id: int = 0
    _data: dict = None
    _repo: RepoComponent = None

    def __init__(self, data: dict, repo: RepoComponent):
        if not isinstance(data, dict):
            raise ValueError(f'InstanceBase.load() expects a dict, got {type(data)}')
        self._data = data
        self._repo = repo
        self.load()

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def data(self) -> dict:
        return self._data

    @property
    def repo(self) -> RepoComponent:
        return self._repo

    def load(self) -> None:
        raise NotImplemented("InstanceBase.load() is not implemented")

    def properties(self, exclude: list) -> any:
        for name, data in self.data.items():
            if name in exclude:
                continue
            yield name, data
