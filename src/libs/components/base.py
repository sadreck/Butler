import re


class BaseComponent:
    def _parse_component(self, component: str) -> dict:
        data = {
            'org': '',
            'repo': '',
            'ref': '',
            'path': ''
        }

        if component is None or len(component) == 0:
            return data

        if component.lower().startswith('https://'):
            data['org'], data['repo'], data['ref'], data['path'] = self._load_from_url(component)
        elif component.lower().startswith('docker://'):
            data['org'], data['repo'], data['ref'], data['path'] = self._load_from_docker(component)
        else:
            data['org'], data['repo'], data['ref'], data['path'] = self._load_from_string(component)
        return data

    def _load_from_url(self, component_url: str) -> tuple[str, str, str, str]:
        pattern = (
            r"github\.com/(?P<org>[^/]+)/(?P<repo>[^/]+)"
            r"(?:/(tree|blob)/(?P<ref>[^/]+)(?:/(?P<path>.*))?)?$"
        )

        match = re.search(pattern, component_url)
        if not match:
            return '', '', '', ''

        return match.group('org') or '', match.group('repo') or '', match.group('ref') or '', match.group('path') or ''

    def _load_from_string(self, component: str) -> tuple[str, str, str, str]:
        org = ''
        repo = ''
        ref = ''
        path = ''

        if '@' in component:
            component, branch = component.rsplit('@', 1)
            ref = branch.strip()

        parts = component.split('/')
        if len(parts) >= 1:
            org = parts[0].strip()

        if len(parts) >= 2:
            repo = parts[1].strip()

        if len(parts) >= 3:
            path = '/'.join(parts[2:])

        return org, repo, ref, path

    def _load_from_docker(self, component: str) -> tuple[str, str, str, str]:
        org = ''
        repo = ''
        ref = ''
        path = ''

        if component.lower().startswith('docker://'):
            component = component[len('docker://'):]

        if '/' in component:
            org, component = component.rsplit('/', 1)
        else:
            org = '_'

        if ':' in component:
            repo, ref = component.split(':', 1)
        else:
            repo = component

        return org, repo, ref, path
