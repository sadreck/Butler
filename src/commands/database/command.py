import os
import argparse
from src.commands.command import Command
from src.commands.database.database import ServiceDatabase
from src.database.database import Database


class CommandDatabase(Command):
    _validate_token = False

    @staticmethod
    def load_command_line(subparsers: any) -> None:
        subparser = subparsers.add_parser("database", help="Database Functions")

        subparser.add_argument("--database", default="database.db", type=str, help="Path to SQLite database to create or connect to")
        subparser.add_argument("--purge", default=False, action="store_true", help="Purge entire database")
        subparser.add_argument("--reprocess", default=False, action="store_true", help="Reset all processed data")

        Command.define_shared_arguments(subparser)

    def load_arguments(self, arguments: argparse.Namespace) -> dict:
        return {
            'database': '' if arguments.database is None or len(arguments.database.strip()) == 0 else os.path.realpath(arguments.database.strip()),
            'purge': arguments.purge or False,
            'reprocess': arguments.reprocess or False
        }

    def execute(self, arguments: dict) -> bool:
        database = Database(arguments['database'], arguments['db_debug'], arguments['db_debug_auto_commit'], False)

        service = ServiceDatabase(self.log, database)
        service.purge = arguments['purge']
        service.reprocess = arguments['reprocess']
        return service.run()
