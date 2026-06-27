import os
import argparse
from loguru import logger
from src.github.api import GitHubApi
from src.libs.exceptions import InvalidCommandLine


class Command:
    _tokens: list = None
    _validate_token: bool = True

    @property
    def tokens(self) -> list:
        return self._tokens

    @staticmethod
    def load_command_line(subparsers: any) -> None:
        raise NotImplementedError("Command.load_command_line() not implemented")

    def load_arguments(self, arguments: argparse.Namespace) -> dict:
        raise NotImplementedError("Command.load_arguments() not implemented")

    def execute(self, arguments: dict) -> bool:
        raise NotImplementedError("Command.execute() not implemented")

    @staticmethod
    def define_shared_arguments(subparser) -> None:
        # Add default flags.
        subparser.add_argument("--verbose", "-v", action="store_true", default=False, help="Debug output")
        subparser.add_argument("--very-verbose", "-vv", action="store_true", default=False, help="Trace output")
        subparser.add_argument("--token", default=[], action="append", help="Environment variable(s) to load PAT from (default is GITHUB_TOKEN), and supports wildcards like GITHUB_TOKEN_*")
        subparser.add_argument("--gh-app-key", default="", help="Environment variable to load the GitHub App's secret key from")
        subparser.add_argument("--gh-app-client-id", default="", help="GitHub App Client ID")
        subparser.add_argument("--db-debug", action="store_true", default=False, help="Enable Database Debug Stats")
        subparser.add_argument("--db-debug-auto-commit", action="store_true", default=False, help="Enable Database Auto-Commit")

    def __init__(self, log: logger):
        self.log = log

    def run(self, arguments: argparse.Namespace) -> bool:
        self.log.trace("Loading default arguments")
        default_arguments = self.load_default_arguments(arguments)

        # This can be overridden if needed.
        if not self.validate_default_arguments():
            raise InvalidCommandLine("Command line arguments could not be validated")

        self.log.trace("Loading command arguments")
        command_arguments = self.load_arguments(arguments)
        if not isinstance(command_arguments, dict):
            raise TypeError("Coding error: Return of function load_arguments() must be a dict")
        command_arguments.update(default_arguments)

        # Log Trace
        for name, value in command_arguments.items():
            self.log.trace(f"{name} is {value}")

        self.log.trace("Validating command arguments")
        self.validate_command_arguments(command_arguments)

        return self.execute(command_arguments)

    def load_default_arguments(self, arguments: argparse.Namespace) -> dict:
        gh_app = {
            'key': arguments.gh_app_key if 'gh_app_key' in arguments and len(arguments.gh_app_key) > 0 else '',
            'client_id': arguments.gh_app_client_id if 'gh_app_client_id' in arguments and len(arguments.gh_app_client_id) > 0 else '',
            'org': arguments.org if 'org' in arguments and arguments.org is not None and len(arguments.org) > 0 else '',
            'defined': False
        }
        gh_app['defined'] = len(gh_app['key']) > 0 and len(gh_app['client_id']) > 0 and len(gh_app['org']) > 0

        token_names = sorted(set(arguments.token))
        # Fallback to GITHUB_TOKEN only when a GH App Key was not passed
        if len(token_names) == 0 and not gh_app['defined']:
            token_names = ["GITHUB_TOKEN"]

        self._tokens = []
        if self._validate_token:
            self._tokens = self._load_tokens(token_names, gh_app)

        return {
            'db_debug': arguments.db_debug or False,
            'db_debug_auto_commit': arguments.db_debug or False
        }

    def validate_default_arguments(self) -> bool:
        # Override if required.
        return True

    def validate_command_arguments(self, arguments: dict) -> None:
        # Override if required - throw exceptions on errors.
        return None

    def _load_tokens(self, token_names: list, gh_app: dict) -> list:
        tokens = []
        if gh_app['defined']:
            self.log.info(f"Generating PAT from GitHub App (environment variable is {gh_app['key']}, ClientId {gh_app['client_id']})")
            gh_app_key = os.getenv(gh_app['key'], '')
            if len(gh_app_key) == 0:
                raise InvalidCommandLine(f"Environment variable passed in --gh-app-key is empty: {gh_app['key']}")

            token = GitHubApi.generate_pat_from_gh_app(gh_app['org'], gh_app_key, gh_app['client_id'])
            if token is None:
                raise InvalidCommandLine(f"Could not generate PAT for GitHub App")
            tokens.append(token)

        for token_name in token_names:
            if '*' in token_name:
                """
                If a token is defined as such: GITHUB_TOKEN_*
                It will be loaded as:

                    GITHUB_TOKEN_1
                    GITHUB_TOKEN_2
                    ...
                    GITHUB_TOKEN_N

                    Until the first empty value is found.
                """
                index = 0
                while True:
                    index += 1
                    name = token_name.replace('*', str(index))

                    pat = os.getenv(name, '')
                    if len(pat) == 0:
                        break
                    tokens.append(pat)
            else:
                pat = os.getenv(token_name, '')
                if len(pat) == 0:
                    raise InvalidCommandLine(f"Environment variable passed in --token is empty: {token_name}")
                tokens.append(pat)

        return sorted(set(tokens))
