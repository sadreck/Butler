from src.commands.report.helpers.third_party_instance import ThirdPartyInstance
from src.libs.components.workflow import WorkflowComponent
from src.libs.constants import GitHubRefType


class ThirdPartyResults:
    _actions: dict = None
    trusted_orgs: list = None
    deprecated_actions: list = None

    @property
    def actions(self) -> list:
        return list(self._actions.values())

    def __init__(self, trusted_orgs: list, deprecated_actions: list) -> None:
        self._actions = {}
        self.trusted_orgs = [name.lower() for name in trusted_orgs]
        self.deprecated_actions = [name.lower() for name in deprecated_actions]

    def get_or_create(self, action: WorkflowComponent, workflow: WorkflowComponent, title: str) -> ThirdPartyInstance:
        name = action.action_name().lower()
        if name not in self._actions:
            self._actions[name] = ThirdPartyInstance(action, workflow)
            self._actions[name].name = name
            self._actions[name].stars = action.repo.stars
            self._actions[name].trusted = action.repo.org.name.lower() in self.trusted_orgs
            self._actions = dict(sorted(self._actions.items()))

        self._actions[name].increment_usage()
        if action.repo.ref_type == GitHubRefType.TAG:
            item = self._actions[name].add_tag(
                action.repo.ref,
                self._is_deprecated_ref(name, action.repo.ref),
                title,
                action.repo.ref_commit
            )
        elif action.repo.ref_type == GitHubRefType.BRANCH:
            item = self._actions[name].add_branch(
                action.repo.ref,
                self._is_deprecated_ref(name, action.repo.ref),
                title,
                action.repo.ref_commit
            )
        elif action.repo.ref_type == GitHubRefType.COMMIT:
            item = self._actions[name].add_commit(
                action.repo.ref,
                action.repo.resolved_ref,
                action.repo.resolved_ref_type,
                self._is_deprecated_commit(name, action.repo.resolved_ref),
                title
            )
        else:
            raise Exception(f"Unknown action repo ref type: {action.repo.ref_type}")

        if str(workflow) not in item['workflows']:
            item['workflows'][str(workflow)] = workflow
        return self._actions[name]

    def _is_deprecated_ref(self, name: str, ref: str) -> bool:
        return f"{name}@{ref}".lower() in self.deprecated_actions

    def _is_deprecated_commit(self, name: str, ref: str) -> bool:
        for action in self.deprecated_actions:
            action_name, version = action.split('@', 1)
            if name.lower() == action_name and ref.startswith(version):
                return True
        return False

    def count(self, what: str) -> int:
        count = 0
        match what.lower():
            case 'all':
                count = len(self._actions)
            case 'trusted-orgs':
                for name, action in self._actions.items():
                    if action.trusted:
                        count += 1
            case 'untrusted-orgs':
                for name, action in self._actions.items():
                    if not action.trusted:
                        count += 1
            case 'tags':
                for name, action in self._actions.items():
                    count += len(action.tags)
            case 'branches':
                for name, action in self._actions.items():
                    count += len(action.branches)
            case 'commits':
                for name, action in self._actions.items():
                    count += len(action.commits)
            case 'archived':
                for name, action in self._actions.items():
                    if action.action.repo.archive:
                        count += 1
            case 'forked':
                for name, action in self._actions.items():
                    if action.action.repo.fork:
                        count += 1
            case 'sources':
                for name, action in self._actions.items():
                    if action.action.repo.fork is False and action.action.repo.archive is False:
                        count += 1
            case 'deprecated':
                for name, action in self._actions.items():
                    for commit_name, commit in action.commits.items():
                        if commit['deprecated']:
                            count += 1

                    for branch_name, branch in action.branches.items():
                        if branch['deprecated']:
                            count += 1

                    for tag_name, tag in action.tags.items():
                        if tag['deprecated']:
                            count += 1
            case 'supported':
                for name, action in self._actions.items():
                    for commit_name, commit in action.commits.items():
                        if not commit['deprecated']:
                            count += 1

                    for branch_name, branch in action.branches.items():
                        if not branch['deprecated']:
                            count += 1

                    for tag_name, tag in action.tags.items():
                        if not tag['deprecated']:
                            count += 1

        return count

    def for_csv(self) -> list:
        """
        # These are repo-specific.
        action_org
        action_repo
        action_workflow
        action_fork
        action_archived
        action_stars
        action_trusted_org

        # These are ref-specific.
        action_ref
        action_ref_type
        action_ref_resolved_to (commit for branch/tag, branch/tag for commit)
        action_deprecated
        action_url

        # These are parent-workflow-specific.
        parent_org
        parent_repo
        parent_workflow
        parent_fork
        parent_archived
        parent_ref
        parent_ref_type
        parent_url
        """
        header = [
            'action_org',                   # 1
            'action_repo',                  # 2
            'action_workflow',              # 3
            'action_fork',                  # 4
            'action_archived',              # 5
            'action_stars',                 # 6
            'action_trusted_org',           # 7
            'action_deprecated',            # 8
            'action_ref',                   # 9
            'action_ref_type',              # 10
            'action_ref_resolved_to',       # 11
            'action_ref_resolved_type',     # 12
            'action_url',                   # 13
            'parent_org',                   # 14
            'parent_repo',                  # 15
            'parent_workflow',              # 16
            'parent_fork',                  # 17
            'parent_archived',              # 18
            'parent_ref',                   # 19
            'parent_ref_type',              # 20
            'parent_url',                   # 21
        ]
        rows = [header]

        for result in self.actions:
            for ref, info in result.refs().items():
                for parent_workflow_name, parent_workflow in info['workflows'].items():
                    row = [
                        result.action.repo.org.name,                                # 1
                        result.action.repo.name,                                    # 2
                        result.name,                                                # 3
                        1 if result.action.repo.fork else 0,                        # 4
                        1 if result.action.repo.archive else 0,                     # 5
                        result.action.repo.stars,                                   # 6
                        1 if result.trusted else 0,                                 # 7
                        1 if info['deprecated'] else 0,                             # 8
                        ref,                                                        # 9
                        info['type'],                                               # 10
                        info['resolved_ref'],                                       # 11
                        info['resolved_type'],                                      # 12
                        info['permalink_url'],                                      # 13
                        parent_workflow.repo.org.name,                              # 14
                        parent_workflow.repo.name,                                  # 15
                        parent_workflow.path,                                       # 16
                        1 if parent_workflow.repo.fork else 0,                      # 17
                        1 if parent_workflow.repo.archive else 0,                   # 18
                        parent_workflow.repo.ref,                                   # 19
                        GitHubRefType(parent_workflow.repo.ref_type).name.lower(),  # 20
                        parent_workflow.url(True),                                  # 21
                    ]
                    rows.append(row)

        return rows
