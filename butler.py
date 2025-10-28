import argparse
from src.commands.database.command import CommandDatabase
from src.commands.process.command import CommandProcess
from src.commands.report.command import CommandReport
from src.libs.utils import Utils
from src.libs.exceptions import InvalidCommandLine
from src.commands.download.command import CommandDownload


__VERSION__ = '0.9.1 Beta'
commands = {
    'download': CommandDownload,
    'database': CommandDatabase,
    'process': CommandProcess,
    'report': CommandReport,
}

parser = argparse.ArgumentParser(prog="butler", description=f"Butler - GitHub Actions Oversight v{__VERSION__}")
subparsers = parser.add_subparsers(dest="command")

for name, command in commands.items():
    command.load_command_line(subparsers)

args = parser.parse_args()

if args.command is None:
    parser.print_help()
    exit(1)

logger = Utils.init_logger(args.verbose if 'verbose' in args else None, args.very_verbose if 'very_verbose' in args else None)

try:
    command = commands[args.command](logger)
    if not command.run(args):
        logger.warning("Execution did not return a success status, please review the logs manually")
        exit(1)
    exit(0)
except InvalidCommandLine as e:
    logger.critical(e)
except Exception as e:
    # Only show trace for Exceptions that _we_ didn't raise.
    logger.opt(exception=e).trace(e)
    logger.critical(e)
    if not Utils.is_logging_debug_or_trace(logger):
        logger.critical("To see more details about this error, run the same command using -vv")

exit(1)
