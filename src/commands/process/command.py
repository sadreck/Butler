import os
import argparse
from src.commands.command import Command
from src.commands.process.process import ServiceProcess
from src.database.database import Database
from src.libs.exceptions import InvalidCommandLine


class CommandProcess(Command):
    _validate_token: bool = False

    @staticmethod
    def load_command_line(subparsers: any) -> None:
        subparser = subparsers.add_parser("process", help="Process downloaded workflows")

        subparser.add_argument("--database", default="database.sqlite3", type=str, help="Path to SQLite database to create or connect to")
        subparser.add_argument("--threads", default=1, type=int, help="Enable multithreading")

        Command.define_shared_arguments(subparser)

    def load_arguments(self, arguments: argparse.Namespace) -> dict:
        return {
            # Strip, remove empty, and duplicates.
            'database': '' if arguments.database is None or len(arguments.database.strip()) == 0 else os.path.realpath(arguments.database.strip()),
            'threads': int(arguments.threads),
        }

    def validate_command_arguments(self, arguments: dict) -> None:
        # Validate database.
        if len(arguments['database']) == 0:
            raise InvalidCommandLine(f"--database cannot be empty")
        elif not arguments['database'].lower().endswith('.sqlite3'):
            raise InvalidCommandLine(f"--database {arguments['database']} is not a SQLite database (must end with .sqlite3)")
        elif not os.path.isfile(arguments['database']):
            raise InvalidCommandLine(f"--database does not exist: {arguments['database']}")

        if arguments['threads'] <= 0:
            arguments['threads'] = 1

    def execute(self, arguments: dict) -> bool:
        database = Database(arguments['database'], arguments['db_debug'], arguments['db_debug_auto_commit'])

        service = ServiceProcess(self.log, database)
        service.threads = arguments['threads']

        return service.run()
