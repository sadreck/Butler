import re
from itertools import product


class JobRunner:
    @staticmethod
    def parse(data: dict) -> list:
        runs_on = JobRunner._get_runs_on(data.get('runs-on', None))
        if '$' and '{' not in runs_on:
            return [runs_on]
        elif isinstance(runs_on, str) and '$' in runs_on and 'fromjson' in runs_on.lower():
            return []

        strategy = data.get('strategy', {})
        if not isinstance(strategy, dict):
            return []
        matrix = strategy.get('matrix', {}) or {}
        parsed_runners = JobRunner._parse_matrix(runs_on, matrix, strategy)
        runners = JobRunner._post_process_runners(parsed_runners)
        return runners

    @staticmethod
    def _post_process_runners(parsed_runners: list) -> list:
        if len(parsed_runners) == 0:
            return []

        runners = []
        for runner in parsed_runners:
            if runner.isnumeric():
                continue

            if runner.startswith('runs-on,') or runner == 'runs-on':
                runners.append('runs-on.com')
                continue

            if runner.startswith('${{'):
                if '&&' and '||' in runner:
                    # This regex looks for strings between '&&' or '||' and captures the quoted values
                    matches = re.findall(r"&&\s*'([^']*)'|\|\|\s*'([^']*)'", runner)
                    results = [match for pair in matches for match in pair if match]
                    if len(results) > 0:
                        runners.extend(results)
                        continue
                    if len(results) == 0:
                        print("No regex matches")
                        print(runner)
                        print(parsed_runners)
                        exit()

            if '${{' in runner:
                if 'needs.' in runner and 'outputs.' in runner:
                    # Loading the runner from the output of another step.
                    continue
                elif 'inputs.' in runner:
                    # Maybe someday in the future. So probably never.
                    continue
                elif 'github.' in runner:
                    # Maybe someday in the future. So probably never.
                    continue

                # Sometimes it can look like this: "${{ 'macos-14-large' }}"
                match = re.search(r"\$\{\{\s*'([^']+)'\s*\}\}", runner)
                if match:
                    runners.append(match.group(1))
                    continue

            # Catch-all for anything not hitting any conditions above.
            runners.append(runner)
        return list(sorted(set(runners)))

    @staticmethod
    def _case_insensitive_exists_in_dict(data: dict, key: str) -> bool:
        for name, value in data.items():
            if str(name).lower() == str(key).lower():
                return True
        return False

    @staticmethod
    def _case_insensitive_get_from_dict(data: dict, key: str, default: any = None) -> any:
        for name, value in data.items():
            if str(name).lower() == str(key).lower():
                return value
        return default

    @staticmethod
    def _get_runs_on(runs_on: any) -> str:
        if runs_on is None:
            # No runner specified - does the workflow even work?
            return ''
        elif isinstance(runs_on, str):
            # A single runner has been assigned, this could be a matrix value as well.
            return runs_on.strip()
        elif isinstance(runs_on, list):
            """
            # https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#jobsjob_idruns-on

            If you specify an array of strings or variables, your workflow will execute on any runner that matches all
            of the specified runs-on values. For example, here the job will only run on a self-hosted runner that has
            the labels linux, x64, and gpu:

            runs-on: [self-hosted, linux, x64, gpu]
            """
            # In this instance, we only care about the first element as that's the runner, the others are labels.
            return runs_on[0].strip()
        elif isinstance(runs_on, dict):
            """
            https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#jobsjob_idruns-on

            A key: value pair using the `group` or `labels` keys
            """
            if 'group' in runs_on and 'labels' in runs_on:
                return 'group-and-labels'
            elif 'group' in runs_on:
                return runs_on['group']
            elif 'labels' in runs_on:
                return 'labels'
                # return runs_on['labels']

        return ''

    @staticmethod
    def _parse_matrix(runs_on: str, matrix: dict, strategy: dict) -> list:
        variables = JobRunner._get_matrix_variables(runs_on)
        if len(variables) == 0:
            return []
        elif isinstance(matrix, str) and 'fromjson' in matrix.lower():
            # This is determined in runtime.
            return []

        runners = []
        variable_location = JobRunner._where_are_the_variables(variables, matrix, strategy)
        # if variable_location is None:
        if all(not value for value in variable_location.values()):
            print("DEBUG: Variable location is None")
            exit()

        # If there are nested references like matrix.config.os instead of just matrix.os
        is_nested_matrix = any(key.count('.') > 1 for key in variables)

        if variable_location['matrix']:
            if is_nested_matrix:
                runners = JobRunner._generate_nested_runners(variables, runs_on, matrix)
            else:
                runners = JobRunner._generate_combinations(variables, runs_on, matrix)
        elif variable_location['include']:
            if is_nested_matrix:
                runners = JobRunner._generate_from_nested_and_include(variables, runs_on, matrix)
            else:
                runners = JobRunner._generate_from_include(variables, runs_on, matrix)
        elif variable_location['strategy']:
            if is_nested_matrix:
                runners = JobRunner._generate_nested_runners(variables, runs_on, strategy)
            else:
                runners = JobRunner._generate_combinations(variables, runs_on, strategy)

        if any("${{" in item for item in runners):
            # Still has variables.
            try:
                if variable_location['include']:
                    if is_nested_matrix:
                        runners = JobRunner._generate_from_nested_and_include(variables, runs_on, matrix)
                    else:
                        runners = JobRunner._generate_from_include(variables, runs_on, matrix)
            except Exception as e:
                pass

        return sorted(list(set(runners)))

    @staticmethod
    def _where_are_the_variables(variables: dict, matrix: dict, strategy: dict) -> dict:
        locations = {
            'matrix': False,
            'include': False,
            'dynamic': False,
            'strategy': False
        }

        for seed, variable in variables.items():
            if variable.count('.') > 0:
                # Nested variable
                variable = variable.split('.')[0]

            if JobRunner._case_insensitive_exists_in_dict(matrix, variable):
                value = JobRunner._case_insensitive_get_from_dict(matrix, variable)
                if isinstance(value, str) and 'fromjson' in value.lower():
                    locations['dynamic'] = True
                else:
                    locations['matrix'] = True
            elif JobRunner._case_insensitive_exists_in_dict(strategy, variable):
                value = JobRunner._case_insensitive_get_from_dict(strategy, variable)
                if value:
                    locations['strategy'] = True

            includes = matrix.get('include', [])
            if isinstance(includes, str) and 'fromjson' in includes.lower():
                locations['dynamic'] = True
            else:
                for include in matrix.get('include', []):
                    if not isinstance(include, dict):
                        continue
                    if JobRunner._case_insensitive_exists_in_dict(include, variable):
                        value = JobRunner._case_insensitive_get_from_dict(include, variable)
                        if isinstance(value, str) and 'fromjson' in value.lower():
                            locations['dynamic'] = True
                        else:
                            locations['include'] = True

        return locations

    @staticmethod
    def _generate_from_nested_and_include(template_map: dict, runner_template: str, data: dict) -> list:
        data = data['include']
        # First, get the name of the parent property.
        key = template_map[next(iter(template_map))].split('.')[0]

        runners = []
        for item in data:
            runner = runner_template
            for seed, variable in template_map.items():
                variable = variable.replace(f"{key}.", '')
                value = item[key][variable]
                runner = runner.replace(seed, str(value))

            runners.append(runner)

        return runners

    @staticmethod
    def _generate_from_include(template_map: dict, runner_template: str, data: dict) -> list:
        data = data['include']
        runners = []
        for item in data:
            runner = runner_template
            for seed, variable in template_map.items():
                if variable not in item:
                    runner = None
                    break
                value = item[variable]
                if isinstance(value, list):
                    value = value[0]
                runner = runner.replace(seed, str(value))

            if runner is not None:
                runners.append(runner)

        return runners

    @staticmethod
    def _generate_nested_runners(template_map: dict, runner_template: str, data: dict) -> list:
        # First, get the name of the parent property.
        key = template_map[next(iter(template_map))].split('.')[0]
        data = data[key]
        if isinstance(data, str) and 'fromjson' in data.lower():
            # This is determined in runtime.
            return []
        runners = []

        for item in data:
            if isinstance(item, str) and 'fromjson' in item.lower():
                continue
            runner = runner_template
            for seed, variable in template_map.items():
                variable = variable.replace(f"{key}.", '')
                if '.' in variable:
                    # It's nested.
                    parts = variable.split('.')
                    item_temp = item.copy()
                    for part in parts:
                        item_temp = item_temp[part]

                    value = item_temp
                else:
                    value = item[variable]

                if isinstance(value, list):
                    runner = value[0]
                else:
                    runner = runner.replace(seed, str(value))

            runners.append(runner)

        return runners

    @staticmethod
    def _generate_combinations(template_map: dict, runner_template: str, data: dict):
        # Get the keys used in the template, like 'os' and 'version'
        keys = [template_map[placeholder] for placeholder in template_map]

        # Get all combinations of values from the data
        # combinations = list(product(*(data[key] for key in keys)))
        # combinations = list(product(*(JobRunner._case_insensitive_get_from_dict(data, key) for key in keys)))
        values = [JobRunner._case_insensitive_get_from_dict(data, key) for key in keys]
        values = [v for v in values if v is not None]
        combinations = list(product(*values))

        # Generate output by replacing the placeholders in the runner_template
        results = []
        for combo in combinations:
            result = runner_template
            for placeholder, value in zip(template_map, combo):
                if isinstance(value, list):
                    value = value[0]
                result = result.replace(placeholder, str(value))
            results.append(result)

        return results

    @staticmethod
    def _get_matrix_variables(runs_on: str) -> dict:
        # First, extract all the matrix variables from `runs_on`, for example if there's a matrix.os extract 'os'.
        matrix_variables_pattern = r'(\${{\s*matrix\.([a-zA-Z0-9_.-]+)\s*}})'
        matrix_variables = re.findall(matrix_variables_pattern, runs_on)
        if len(matrix_variables) == 0:
            return {}
        return dict(matrix_variables)