from src.libs.components.workflow import WorkflowComponent


class RunnerResults:
    _runners: dict = None
    _workflows: dict = None
    supported_runners: list = None
    unsupported_runners: list = None

    def __init__(self, supported_runners: list, unsupported_runners: list) -> None:
        self._runners = {}
        self._workflows = {}
        self.supported_runners = [name.lower() for name in supported_runners]
        self.unsupported_runners = [name.lower() for name in unsupported_runners]

    def count(self, what: str) -> int:
        match what.lower():
            case 'runners':
                return len(self._runners)
            case 'workflows':
                return len(self._workflows)
            case 'self-hosted':
                return sum(1 for item in self._runners.values() if item.get("self_hosted") is True)
            case 'github':
                return sum(1 for item in self._runners.values() if item.get("self_hosted") is False)
            case 'unsupported':
                return sum(1 for item in self._runners.values() if item.get("supported") is False)
            case _:
                return 0

    @property
    def runners(self) -> list:
        return list(dict(sorted(self._runners.items())).values())

    @property
    def workflows(self) -> list:
        return list(dict(sorted(self._workflows.items())).values())

    def get_or_create(self, workflow: WorkflowComponent, runner_name: str) -> dict:
        runner = {
            'count': 0,
            'name': runner_name.lower(),
            'self_hosted': self._is_self_hosted_runner(runner_name),
            'supported': self._is_self_hosted_runner(runner_name) or self._is_runner_supported(runner_name),
        }

        if runner_name.lower() not in self._runners:
            self._runners[runner_name.lower()] = runner

        self._runners[runner_name.lower()]['count'] += 1

        # Now add the workflows.
        if str(workflow) not in self._workflows:
            self._workflows[str(workflow)] = {
                'workflow': workflow,
                'runners': {},
            }

        if runner_name.lower() not in self._workflows[str(workflow)]['runners']:
            self._workflows[str(workflow)]['runners'][runner_name.lower()] = runner
            self._workflows[str(workflow)]['runners'] = dict(sorted(self._workflows[str(workflow)]['runners'].items()))

        return self._runners[runner_name.lower()]

    def _is_runner_supported(self, runner_name: str) -> bool:
        return runner_name.lower() in self.supported_runners

    def _is_unsupported_runner(self, runner_name: str) -> bool:
        return runner_name.lower() in self.unsupported_runners

    def _is_self_hosted_runner(self, runner_name: str) -> bool:
        # When it doesn't belong in neither supported nor unsupported.
        return self._is_runner_supported(runner_name) is False and self._is_unsupported_runner(runner_name) is False

    def csv_for_runners(self, org: str) -> list:
        header = ['org', 'runner', 'total', 'self_hosted', 'supported']
        rows = [header]
        for runner in self.runners:
            rows.append([
                org,
                runner['name'],
                runner['count'],
                1 if runner['self_hosted'] else 0,
                1 if runner['supported'] else 0
            ])

        return rows

    def csv_for_workflows(self) -> list:
        header = ['org', 'repo', 'workflow', 'ref', 'url', 'runner', 'self_hosted', 'supported']
        rows = [header]
        for result in self.workflows:
            for name, runner in result['runners'].items():
                rows.append([
                    result['workflow'].repo.org.name,
                    result['workflow'].repo.name,
                    result['workflow'].path,
                    result['workflow'].repo.ref,
                    result['workflow'].url(True),
                    runner['name'],
                    1 if runner['self_hosted'] else 0,
                    1 if runner['supported'] else 0
                ])
        return rows
