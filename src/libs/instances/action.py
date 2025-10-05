from src.libs.instances.base import InstanceBase
from src.libs.instances.local_checkouts import LocalCheckoutParser
from src.libs.instances.step import StepInstance


class ActionInstance(InstanceBase, LocalCheckoutParser):
    _name: str = None
    _using: str = None
    _steps: list = None
    _type: str = None
    _inputs: dict = None
    _outputs: dict = None

    @property
    def name(self) -> str:
        return self._name or ''

    @property
    def using(self):
        return self._using or ''

    @property
    def type(self) -> str:
        return self._type or ''

    @property
    def steps(self) -> list:
        return self._steps or []

    @property
    def total_steps(self) -> int:
        return len(self.steps) if self.steps else 0

    @property
    def inputs(self):
        return self._inputs or {}

    @property
    def outputs(self):
        return self._outputs or {}
    
    def load(self) -> None:
        self._steps = []
        self._name = self.data.get('name', '')
        self._using = self.data.get('runs', {}).get('using', '')
        self._type = self._determine_type()
        self._inputs = self.data.get('inputs', {})
        self._outputs = self.data.get('outputs', {})

        runs = self.data.get('runs', {})
        if isinstance(runs, dict):
            steps = runs.get('steps', [])
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

    def _determine_type(self) -> str:
        using = self.using.lower()
        if using.startswith('node'):
            return 'node'
        elif using in ['docker', 'composite']:
            return using
        elif using == '':
            return 'not-set'
        raise ValueError(f"Unknown action 'using': {using}")
