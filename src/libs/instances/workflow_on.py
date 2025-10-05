class WorkflowOn:
    _triggers: dict = None

    _valid_trigger_events: list = [
        'branch_protection_rule',
        'check_run',
        'check_suite',
        'create',
        'delete',
        'deployment',
        'deployment_status',
        'discussion',
        'discussion_comment',
        'fork',
        'gollum',
        'issue_comment',
        'issues',
        'label',
        'merge_group',
        'milestone',
        'page_build',
        'public',
        'pull_request',
        'pull_request_review',
        'pull_request_review_comment',
        'pull_request_target',
        'push',
        'registry_package',
        'release',
        'repository_dispatch',
        'schedule',
        'status',
        'watch',
        'workflow_call',
        'workflow_dispatch',
        'workflow_run'
    ]

    @property
    def triggers(self) -> dict:
        return self._triggers

    @property
    def trigger_events(self) -> list:
        return list(self._triggers.keys())

    def __init__(self, data: any):
        self._triggers = {}

        if data is None:
            return

        if isinstance(data, str):
            if data in self._valid_trigger_events:
                self._triggers[data] = {}
            # Nothing else to do, it's a single string.
            return
        elif isinstance(data, list):
            for name in data:
                if name in self._valid_trigger_events:
                    self._triggers[name] = {}
            # Nothing else to do, it's a list so there's no child properties.
            return
        elif not isinstance(data, dict):
            return

        # From here on, we're processing a more complex config/dict.
        for event, properties in data.items():
            if event not in self._valid_trigger_events:
                continue

            self._triggers[event] = {
                'branches': self._get_properties(properties, 'branches'),
                'tags': self._get_properties(properties, 'tags'),
                'types': self._get_properties(properties, 'types'),
            }

    def _get_properties(self, properties: any, key: str) -> list:
        if not isinstance(properties, dict):
            return []
        elif key not in properties or properties[key] is None:
            return []

        items = properties[key]
        if isinstance(items, str):
            return [items]
        elif isinstance(items, list):
            return items
        return []
