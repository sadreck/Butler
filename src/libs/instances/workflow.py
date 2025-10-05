from src.libs.instances.base import InstanceBase
from src.libs.instances.job import JobInstance
from src.libs.instances.workflow_on import WorkflowOn


class WorkflowInstance(InstanceBase):
    _name: str = None
    _jobs: list[JobInstance] = None
    _on: WorkflowOn = None

    @property
    def jobs(self) -> list:
        return self._jobs or []

    @property
    def name(self) -> str:
        return self._name or ''

    @property
    def total_jobs(self):
        return len(self._jobs) if self._jobs else 0

    @property
    def on_events(self) -> list:
        return self._on.trigger_events

    @property
    def on_data(self) -> dict:
        return self._on.triggers

    def load(self) -> None:
        self._jobs = []
        self._name = self.data.get('name', '')
        self._on = WorkflowOn(self.data.get('on', None))

        jobs = self.data.get('jobs', None)
        if isinstance(jobs, dict):
            for name, data in jobs.items():
                if data is None or not isinstance(data, dict):
                    continue
                job = JobInstance(data, self.repo)
                job.shortname = name
                self._jobs.append(job)
