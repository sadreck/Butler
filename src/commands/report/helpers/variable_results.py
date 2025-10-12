from src.libs.components.workflow import WorkflowComponent


class VariableResults:
    _workflows: dict = None
    _secrets: dict = None
    _variables: dict = None

    @property
    def secrets(self) -> dict:
        return dict(sorted(self._secrets.items()))

    @property
    def variables(self) -> dict:
        return dict(sorted(self._variables.items()))

    @property
    def workflows(self):
        return list(self._workflows.values())

    @property
    def all(self) -> dict:
        secrets_and_variables = {**self._secrets, **self._variables}
        return dict(sorted(secrets_and_variables.items()))

    def __init__(self):
        self._secrets = {}
        self._variables = {}
        self._workflows = {}

    def count(self, what: str) -> int:
        match what.lower():
            case 'secrets':
                return len(self._secrets)
            case 'variables':
                return len(self._variables)
            case 'all':
                return len(self._secrets) + len(self._variables)
            case 'workflows':
                return len(self._workflows)
            case _:
                return 0

    def get_or_create(self, workflow: WorkflowComponent, variable_name: str) -> str:
        if not str(workflow) in self._workflows:
            self._workflows[str(workflow)] = {
                'workflow': workflow,
                'variables': {},
                'secrets': {}
            }

        variable_name = variable_name.lower()
        if variable_name.startswith('secrets.'):
            variable_name = variable_name[len('secrets.'):].upper()
            if variable_name not in self._secrets:
                self._secrets[variable_name] = {
                    'name': variable_name,
                    'count': 0,
                    'type': 'secret'
                }
            if variable_name not in self._workflows[str(workflow)]['secrets']:
                self._workflows[str(workflow)]['secrets'][variable_name] = {
                    'name': variable_name,
                    'count': 0,
                    'type': 'secret'
                }

            self._secrets[variable_name]['count'] += 1
            self._workflows[str(workflow)]['secrets'][variable_name]['count'] += 1
        elif variable_name.startswith('vars.'):
            variable_name = variable_name[len('vars.'):].upper()
            if variable_name not in self._variables:
                self._variables[variable_name] = {
                    'name': variable_name,
                    'count': 0,
                    'type': 'variable'
                }
            if variable_name not in self._workflows[str(workflow)]['variables']:
                self._workflows[str(workflow)]['variables'][variable_name] = {
                    'name': variable_name,
                    'count': 0,
                    'type': 'variable'
                }

            self._variables[variable_name]['count'] += 1
            self._workflows[str(workflow)]['variables'][variable_name]['count'] += 1
        else:
            raise ValueError(f"Unknown variable type: {variable_name}")

        return variable_name

    def csv_for_variables(self, org: str) -> list:
        header = ['org', 'name', 'type']

        rows = [header]
        for name, item in self.all.items():
            rows.append([
                org,
                item['name'],
                item['type']
            ])
        return rows

    def csv_for_workflows(self) -> list:
        header = ['org', 'repo', 'workflow', 'ref', 'url', 'name', 'type']

        rows = [header]
        for result in self.workflows:
            for name, info in result['secrets'].items():
                rows.append([
                    result['workflow'].repo.org.name,
                    result['workflow'].repo.name,
                    result['workflow'].path,
                    result['workflow'].repo.ref,
                    result['workflow'].url(True),
                    name,
                    info['type']
                ])

            for name, info in result['variables'].items():
                rows.append([
                    result['workflow'].repo.org.name,
                    result['workflow'].repo.name,
                    result['workflow'].path,
                    result['workflow'].repo.ref,
                    result['workflow'].url(True),
                    name,
                    info['type']
                ])

        return rows
