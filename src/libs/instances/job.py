from src.libs.instances.base import InstanceBase
from src.libs.instances.job_runner import JobRunner
from src.libs.instances.local_checkouts import LocalCheckoutParser
from src.libs.instances.step import StepInstance


class JobInstance(InstanceBase, LocalCheckoutParser):
    _steps: list[StepInstance] = None
    _shortname: str = None
    _runners: list = None

    @property
    def shortname(self) -> str:
        return self._shortname or ''

    @shortname.setter
    def shortname(self, value: str):
        self._shortname = value

    @property
    def name(self) -> str:
        return self.data.get('name', '')

    @property
    def steps(self) -> list:
        return self._steps or []

    @property
    def total_steps(self) -> int:
        return len(self.steps) if self.steps else 0

    @property
    def runners(self) -> list:
        return self._runners or []

    @property
    def uses(self) -> str | None:
        return self.data.get('uses', None)

    def load(self) -> None:
        self._shortname = ''
        self._steps = []
        self._runners = JobRunner.parse(self.data)

        steps = self.data.get('steps', None)
        if isinstance(steps, list):
            number = 0
            for data in steps:
                if data is None or not isinstance(data, dict):
                    continue
                number += 1
                step = StepInstance(data, self.repo)
                step.number = number
                self._steps.append(step)

        self._process_local_checkouts()

    def step(self, number: int) -> StepInstance | None:
        for step in self.steps:
            if step.number == number:
                return step
        return None
