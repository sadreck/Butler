import os
import argparse
from pathlib import Path
from src.commands.command import Command
from src.commands.report.report import ServiceReport
from src.database.database import Database
from src.libs.exceptions import InvalidCommandLine
from src.libs.utils import Utils


class CommandReport(Command):
    _validate_token: bool = False

    @staticmethod
    def load_command_line(subparsers: any) -> None:
        subparser = subparsers.add_parser("report", help="Generate Report for GitHub Organisation")

        subparser.add_argument("--database", default="database.db", type=str, help="Path to SQLite database to create or connect to")
        subparser.add_argument("--repo", required=True, default='', type=str, help="Repo to generate report from")
        subparser.add_argument("--output", required=True, default='', type=str, help="Location to store output files")
        subparser.add_argument("--config", default=None, type=str, help="Configuration file (defaults to default_config.yaml)")
        subparser.add_argument("--custom-query", action="append", type=str, help="Path to custom query yaml file")

        Command.define_shared_arguments(subparser)

    def load_arguments(self, arguments: argparse.Namespace) -> dict:
        return {
            # Strip, remove empty, and duplicates.
            'database': '' if arguments.database is None or len(arguments.database.strip()) == 0 else os.path.realpath(arguments.database.strip()),
            'output': '' if arguments.output is None or len(arguments.output.strip()) == 0 else os.path.realpath(arguments.output.strip()),
            'repo': '' if arguments.repo is None or len(arguments.repo.strip()) == 0 else arguments.repo.strip(),
            'config': '' if arguments.config is None else os.path.realpath(arguments.config.strip()),
            'custom_queries': [] if arguments.custom_query is None else Utils.strip_and_clean_list(arguments.custom_query),
        }

    def validate_command_arguments(self, arguments: dict) -> None:
        # Validate database.
        if len(arguments['database']) == 0:
            raise InvalidCommandLine(f"--database cannot be empty")
        elif not arguments['database'].lower().endswith('.sqlite3') and not arguments['database'].lower().endswith('.db'):
            raise InvalidCommandLine(f"--database {arguments['database']} is not a SQLite database (must end with .sqlite3 or .db)")
        elif not os.path.isfile(arguments['database']):
            raise InvalidCommandLine(f"--database does not exist: {arguments['database']}")

        if len(arguments['output']) == 0:
            raise InvalidCommandLine(f"--output-path cannot be empty")

        if arguments['config'] is None or len(arguments['config']) == 0:
            arguments['config'] = os.path.join(Path(__file__).resolve().parent, 'default_config.yaml')

        if not os.path.isfile(arguments['config']):
            raise InvalidCommandLine(f"--config files does not exist: {arguments['config']}")

        # Overwrite the path with its contents
        arguments['config'] = Utils.load_yaml(Utils.read_file(arguments['config']))

        for file in arguments['custom_queries']:
            if not os.path.isfile(file):
                raise InvalidCommandLine(f"--custom-query file does not exist: {file}")

    def execute(self, arguments: dict) -> bool:
        database = Database(arguments['database'], arguments['db_debug'], arguments['db_debug_auto_commit'])

        service = ServiceReport(self.log, database)
        service.output_path = arguments['output']
        service.repo = arguments['repo']
        service.config = arguments['config']
        service.custom_queries = arguments['custom_queries']

        return service.run()
