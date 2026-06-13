import os
import argparse
from src.commands.secvars.secvars import ServiceSecretsAndVariables
from src.commands.command import Command
from src.database.database import Database
from src.libs.exceptions import InvalidCommandLine
from src.github.client import GitHubClient


class CommandSecretsAndVariables(Command):
    @staticmethod
    def load_command_line(subparsers: any) -> None:
        subparser = subparsers.add_parser("secvars", help="Download Secrets and Variables from GitHub")

        subparser.add_argument("--org", type=str, help="Organisation to download secrets and variables for")
        subparser.add_argument("--database", default="database.db", type=str, help="Path to SQLite database to create or connect to")
        subparser.add_argument("--resume-next", default=True, action="store_true", help="Resume downloads on server errors")
        subparser.add_argument("--threads", default=1, type=int, help="Enable multithreading")

        Command.define_shared_arguments(subparser)

    def load_arguments(self, arguments: argparse.Namespace) -> dict:
        return {
            'org': '' if arguments.org is None or len(arguments.org.strip()) == 0 else arguments.org.strip(),
            'database': '' if arguments.database is None or len(arguments.database.strip()) == 0 else os.path.realpath(arguments.database.strip()),
            'resume_next': arguments.resume_next or False,
            'threads': int(arguments.threads),
        }

    def validate_command_arguments(self, arguments: dict) -> None:
        # Validate database.
        if len(arguments['database']) == 0:
            raise InvalidCommandLine(f"--database cannot be empty")
        elif not arguments['database'].lower().endswith('.sqlite3') and not arguments['database'].lower().endswith('.db'):
            raise InvalidCommandLine(f"--database {arguments['database']} is not a SQLite database (must end with .sqlite3 or .db)")

        if len(arguments['org']) == 0:
            raise InvalidCommandLine(f"--org cannot be empty")

        if arguments['threads'] <= 0:
            arguments['threads'] = 1

    def execute(self, arguments: dict) -> bool:
        database = Database(arguments['database'], arguments['db_debug'], arguments['db_debug_auto_commit'])

        service = ServiceSecretsAndVariables(self.log, database)
        service.github_client = GitHubClient(self.tokens, self.log)
        service.org = arguments['org']
        service.resume_next = arguments['resume_next']
        service.threads = arguments['threads']
        return service.run()
