import hashlib
import sys
import os
import yaml
import json
from collections.abc import Callable
from itertools import islice
from pathlib import Path
from loguru import logger
from yaml.constructor import Constructor
from src.libs.components.org import OrgComponent
from src.libs.components.repo import RepoComponent
from src.libs.thread_executor import ThreadExecutor


class Utils:
    @staticmethod
    def init_logger(v: bool | None, vv: bool | None):
        from loguru import logger

        # Set logging level.
        logging_level = "INFO"
        if v or vv:
            logging_level = "TRACE" if vv else "DEBUG"

        logger.remove()
        logger.add(
            sys.stdout,
            format="{time:[HH:mm:ss]} | <level>{level: <8}</level> | {message}",
            colorize=True,
            level=logging_level
        )

        return logger

    @staticmethod
    def is_logging_debug_or_trace(log: logger) -> bool:
        for index, sink in log._core.handlers.items():
            if sink.levelno < 10:
                return True
        return False

    @staticmethod
    def read_file(path: str) -> str | None:
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return None

    @staticmethod
    def write_file(path: str, data: str) -> bool:
        try:
            with open(path, 'w') as f:
                f.write(data)
            return True
        except Exception as e:
            return False

    @staticmethod
    def strip_and_clean_list(items: list[str]) -> list[str]:
        return list(set(filter(None, (item.strip() for item in items if item is not None))))

    @staticmethod
    def is_true(value: any) -> bool:
        if value is None:
            return False
        elif isinstance(value, bool):
            return value
        return str(value).lower() in ['true', 'on', 'yes', '1']

    @staticmethod
    def get_tests_assets_folder() -> str | None:
        current_path = Path(__file__).resolve().parent
        for parent in [current_path] + list(current_path.parents):
            tests_folder = parent / 'tests'
            assets_folder = tests_folder / 'assets'

            if assets_folder.is_dir():
                return str(assets_folder)

        return None

    @staticmethod
    def is_yaml_extension(name: str) -> bool:
        return Utils.is_extension(name, '.yml') or Utils.is_extension(name, '.yaml')

    @staticmethod
    def is_extension(path: str, extension: str) -> bool:
        return path.lower().endswith(extension.lower())

    @staticmethod
    def md5(data: str) -> str:
        return hashlib.md5(data.encode()).hexdigest()

    @staticmethod
    def split_list(data: list, size: int) -> list | None:
        iterator = iter(data)
        while True:
            chunk = list(islice(iterator, size))
            if not chunk:
                break
            yield chunk

    @staticmethod
    def wait_for_threads(threads: list, exit_on_error: bool) -> None:
        for thread in threads:
            thread.join()

        if not exit_on_error:
            return

        for thread in threads:
            if thread.exception:
                raise thread.exception

    @staticmethod
    def remove_yaml_extension(name: str) -> str:
        name = os.path.basename(name)
        if name.lower().endswith('.yml'):
            name = name[:-len('.yml')]
        elif name.lower().endswith('.yaml'):
            name = name[:-len('.yaml')]

        return name

    @staticmethod
    def multithread(function: Callable, arguments: list[tuple]) -> None:
        threads = []
        for args in arguments:
            thread = ThreadExecutor(target=function, args=args)
            threads.append(thread)
            thread.start()

        Utils.wait_for_threads(threads, True)

    @staticmethod
    def load_yaml(text: str, treat_as_text: bool = True) -> dict | None:
        # https://stackoverflow.com/a/36463915
        def add_bool(self, node):
            return self.construct_scalar(node)

        # Same, but leaving dates alone.
        def convert_date(self, node):
            return self.construct_scalar(node)

        if treat_as_text:
            Constructor.add_constructor(u'tag:yaml.org,2002:bool', add_bool)
            Constructor.add_constructor(u'tag:yaml.org,2002:timestamp', convert_date)

        try:
            return yaml.load(text, yaml.loader.Loader)
        except Exception as e:
            return None

    @staticmethod
    def load_json(data: any, default: any = None) -> dict | None:
        try:
            return json.loads(data)
        except Exception as e:
            return default

    @staticmethod
    def filter_orgs_and_repos(items: list) -> tuple[list, list]:
        orgs = []
        repos = []
        for item in items:
            if len(item.strip()) == 0:
                continue
            elif '/' in item:
                repos.append(RepoComponent(item.strip()))
            else:
                orgs.append(OrgComponent(item.strip()))
        return orgs, repos
