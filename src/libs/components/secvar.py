from datetime import datetime
from src.libs.constants import SecretVariableCategory, SecretVariableType, SecretVariableVisibility


class SecretVariableComponent:
    _id: int = None
    _repos: list = None
    _category: SecretVariableCategory = None
    _type: SecretVariableType = None
    _name: str = None
    _value: str = None
    _visibility: SecretVariableVisibility = None
    _created_at: datetime = None
    _updated_at: datetime = None

    @property
    def id(self) -> int:
        return self._id or 0

    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def repos(self) -> list:
        return self._repos

    @repos.setter
    def repos(self, value: list):
        self._repos = value

    @property
    def category(self) -> SecretVariableCategory:
        return self._category

    @category.setter
    def category(self, value: SecretVariableCategory):
        self._category = value

    @property
    def type(self) -> SecretVariableType:
        return self._type

    @type.setter
    def type(self, value: SecretVariableType):
        self._type = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def value(self) -> str:
        return self._value or ''

    @value.setter
    def value(self, value: str):
        self._value = value

    @property
    def visibility(self) -> SecretVariableVisibility:
        return self._visibility

    @visibility.setter
    def visibility(self, value: SecretVariableVisibility):
        self._visibility = value

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @created_at.setter
    def created_at(self, value: datetime | str):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        self._created_at = value

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @updated_at.setter
    def updated_at(self, value: datetime | str):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        self._updated_at = value
