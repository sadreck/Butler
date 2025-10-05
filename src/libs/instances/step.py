from src.libs.instances.base import InstanceBase


class StepInstance(InstanceBase):
    _number: int = 0

    @property
    def number(self) -> int:
        return self._number

    @number.setter
    def number(self, value: int):
        self._number = value

    @property
    def name(self) -> str:
        return self.data.get('name', '')

    @property
    def uses(self) -> str:
        return self.data.get('uses', '')

    @uses.setter
    def uses(self, value: str) -> None:
        self.data['uses'] = value

    @property
    def with_(self) -> dict:
        return self.data.get('with', {})

    def load(self) -> None:
        pass
