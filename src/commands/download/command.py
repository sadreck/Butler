import os
import argparse
from src.commands.command import Command
from src.commands.download.download import ServiceDownload
from src.database.database import Database
from src.libs.exceptions import InvalidCommandLine
from src.libs.utils import Utils
from src.github.client import GitHubClient


class CommandDownload(Command):
    @staticmethod
    def load_command_line(subparsers: any) -> None:
        subparser = subparsers.add_parser("download", help="Download Workflows from GitHub")

        subparser.add_argument("--repo", action="append", type=str, help="Target formatted as: org, org/name, or org/name@branch. To load targets from file use an absolute path or a path starting with ./")
        subparser.add_argument("--workflow", action="append", type=str, help="Download specific workflows, extension is optional")
        subparser.add_argument("--database", default="database.db", type=str, help="Path to SQLite database to create or connect to")
        subparser.add_argument("--resume-next", default=True, action="store_true", help="Resume downloads on server errors")
        subparser.add_argument("--all-branches", default=False, action="store_true", help="Download all branches, only works with --repo")
        subparser.add_argument("--all-tags", default=False, action="store_true", help="Download all tags, only works with --repo")
        subparser.add_argument("--include-forks", default=False, action="store_true", help="Include forked repos when --repo is an org")
        subparser.add_argument("--include-archived", default=False, action="store_true", help="Include archived repos when --repo is an org")
        subparser.add_argument("--threads", default=1, type=int, help="Enable multithreading")

        Command.define_shared_arguments(subparser)

    def load_arguments(self, arguments: argparse.Namespace) -> dict:
        return {
            # Strip, remove empty, and duplicates.
            'repos': [] if arguments.repo is None else Utils.strip_and_clean_list(arguments.repo),
            'workflows': [] if arguments.workflow is None else Utils.strip_and_clean_list(arguments.workflow),
            'database': '' if arguments.database is None or len(arguments.database.strip()) == 0 else os.path.realpath(arguments.database.strip()),
            'resume_next': arguments.resume_next or False,
            'all_branches': arguments.all_branches or False,
            'all_tags': arguments.all_tags or False,
            'include_forks': arguments.include_forks or False,
            'include_archived': arguments.include_archived or False,
            'threads': int(arguments.threads),
        }

    def validate_command_arguments(self, arguments: dict) -> None:
        # Validate repositories.
        if len(arguments['repos']) == 0:
            raise InvalidCommandLine("--repo cannot be empty")

        repos = []
        for repo in arguments['repos']:
            if repo.startswith('./') or repo.startswith('/'):
                self.log.trace(f"Loading --repo batch file {repo}")
                contents = Utils.read_file(repo)
                if contents is None:
                    raise InvalidCommandLine(f"--repo batch file {repo} does not exist or cannot be read")
                batch_repos = [item for item in sorted(set(contents.split("\n"))) if item and item.strip()]
                repos.extend(batch_repos)
            else:
                repos.append(repo)

        arguments['repos'] = list(sorted(set(repos)))
        self.log.trace(f"Total repositories loaded: {len(arguments['repos'])}")

        workflows = [Utils.remove_yaml_extension(name).lower() for name in arguments['workflows']]
        arguments['workflows'] = list(set(workflows))
        if len(arguments['workflows']) > 0:
            self.log.trace(f"Only the following workflows will be downloaded: {arguments['workflows']}")

        # Validate database.
        if len(arguments['database']) == 0:
            raise InvalidCommandLine(f"--database cannot be empty")
        elif not arguments['database'].lower().endswith('.sqlite3') and not arguments['database'].lower().endswith('.db'):
            raise InvalidCommandLine(f"--database {arguments['database']} is not a SQLite database (must end with .sqlite3 or .db)")

        if arguments['threads'] <= 0:
            arguments['threads'] = 1

    def execute(self, arguments: dict) -> bool:
        database = Database(arguments['database'], arguments['db_debug'], arguments['db_debug_auto_commit'])

        service = ServiceDownload(self.log, database)
        service.github_client = GitHubClient(self.tokens, self.log)
        service.repos = arguments['repos']
        service.resume_next = arguments['resume_next']
        service.all_tags = arguments['all_tags']
        service.all_branches = arguments['all_branches']
        service.include_forks = arguments['include_forks']
        service.include_archived = arguments['include_archived']
        service.threads = arguments['threads']
        service.only_workflows = arguments['workflows']
        return service.run()
