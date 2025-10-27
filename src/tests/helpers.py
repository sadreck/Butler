import os
import tempfile
import argparse


def _args_download(**overrides) -> argparse.Namespace:
    defaults = {
        # Shared
        'verbose': False,
        'very_verbose': False,
        'token': [],
        'db_debug': False,
        'db_debug_auto_commit': False,

        # Per Command
        'repo': [],
        'workflow': [],
        'database': 'database.db',
        'resume_next': True,
        'all_branches': False,
        'all_tags': False,
        'include_forks': False,
        'include_archived': False,
        'all_repos': False,
        'threads': 1,
    }

    data = {**defaults, **overrides}
    return argparse.Namespace(**data)

def _args_process(**overrides) -> argparse.Namespace:
    defaults = {
        # Shared
        'verbose': False,
        'very_verbose': False,
        'token': [],
        'db_debug': False,
        'db_debug_auto_commit': False,

        # Per Command
        'database': 'database.db',
        'threads': 1,
    }

    data = {**defaults, **overrides}
    return argparse.Namespace(**data)

def _get_db_path() -> str:
    output_database = os.path.join(tempfile.gettempdir(), "butler-testing.db")
    if os.path.isfile(output_database):
        os.remove(output_database)
    return output_database
