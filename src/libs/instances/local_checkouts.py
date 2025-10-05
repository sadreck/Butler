import os
import re
from src.libs.instances.step import StepInstance


class LocalCheckoutParser:
    def _process_local_checkouts(self):
        local_checkouts = self._find_local_checkouts(self.steps)
        for step in self.steps:
            if not step.uses:
                continue
            elif len(step.uses) == 0:
                continue
            elif not step.uses.startswith('./'):
                continue

            uses = self._expand_local_action(step.uses, local_checkouts)
            if uses:
                step.uses = uses

    def _find_local_checkouts(self, steps: list[StepInstance]) -> list:
        checkouts = []
        for step in steps:
            if not step.uses:
                continue
            elif not step.uses.startswith('actions/checkout@'):
                continue
            elif not step.with_:
                continue
            elif not isinstance(step.with_, dict) or len(step.with_) == 0:
                continue

            repo = step.with_.get('repository', '')
            ref = step.with_.get('ref', '')
            path = step.with_.get('path', '')

            if not repo or len(repo) == 0:
                repo = str(self.repo)

            if not repo:
                continue
            elif not path:
                continue

            if not path.startswith('./'):
                path = f"./{path}"

            if ref and '${{' in ref:
                # Getting it from a variable, ignore.
                ref = ''

            checkouts.append({
                'repo': repo.rstrip('/'),
                'ref': ref or '',
                'path': path
            })
        return checkouts

    def _expand_local_action(self, uses: str, local_checkouts: list) -> str | None:
        action = None
        for local_checkout in local_checkouts:
            if uses.startswith(local_checkout['path']):
                path = uses.replace(local_checkout['path'], '')
                action = f"{local_checkout['repo']}{path}"

                if len(local_checkout['ref']) > 0:
                    action += f"@{local_checkout['ref']}"
                break

        if action is None:
            # If it's not a local checkout, it's probably a relative path in the org.
            uses = os.path.normpath(uses)
            path = re.sub(r'^(?:\./|\.\./)+', '', uses)
            action = f"{self.repo.org.name}/{self.repo.name}/{path}@{self.repo.ref}"

        return action
