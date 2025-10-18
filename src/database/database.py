import os
from src.database.database_helper import DatabaseHelper
from src.database.helpers.db_config import DBConfig
from src.database.helpers.db_jobs import DBJob
from src.database.helpers.db_repos import DBRepo
from src.database.helpers.db_steps import DBStep
from src.database.helpers.db_vars import DBVars
from src.database.helpers.db_workflows import DBWorkflow
from src.database.models import Base
from sqlalchemy import create_engine, Engine, text, MetaData, event
from sqlalchemy.orm import sessionmaker
from src.database.helpers.db_orgs import DBOrg
from src.libs.exceptions import DatabaseVersionMismatch


class Database(DatabaseHelper):
    __VERSION__: str = '1.0.0'
    _engine: Engine = None
    _sessionmaker: sessionmaker = None
    _session = None

    _orgs: DBOrg | None = None
    _repos: DBRepo | None = None
    _workflows: DBWorkflow | None = None
    _jobs: DBJob | None = None
    _steps: DBStep | None = None
    _vars: DBVars | None = None
    _config: DBConfig | None = None

    _total_queries: int = 0
    _debug: bool = False
    _auto_commit: bool = False

    @property
    def session(self):
        return self._session

    @property
    def total_queries(self) -> int:
        return self._total_queries

    @property
    def debug(self) -> bool:
        return self._debug

    @property
    def auto_commit(self) -> bool:
        return self._auto_commit

    def __init__(self, sqlite_file, debug: bool = False, auto_commit: bool = False, check_version: bool = True):
        is_new_database = not os.path.exists(sqlite_file)
        self._debug = debug
        self._auto_commit = auto_commit
        self._engine = create_engine(f"sqlite:///{sqlite_file}")
        self._sessionmaker = sessionmaker(bind=self._engine)
        self._session = self._sessionmaker()

        if is_new_database:
            self._create_tables()

        if self.debug:
            @event.listens_for(Engine, "before_cursor_execute")
            def count_queries(conn, cursor, statement, parameters, context, executemany):
                self._total_queries += 1

        if check_version:
            self._check_database_version(self.__VERSION__)

    def _check_database_version(self, version: str) -> None:
        current_version = self.config().get('db_version')
        if not current_version:
            self.config().set('db_version', version)
        elif current_version != version:
            raise DatabaseVersionMismatch(f"Code Database version {version} does not match existing database version {current_version}")

    def _create_tables(self) -> None:
        Base.metadata.create_all(self._engine)

    def orgs(self) -> DBOrg:
        if not self._orgs:
            self._orgs = DBOrg(self.session, self.auto_commit)
        return self._orgs

    def repos(self) -> DBRepo:
        if not self._repos:
            self._repos = DBRepo(self.session, self.auto_commit)
        return self._repos

    def workflows(self) -> DBWorkflow:
        if not self._workflows:
            self._workflows = DBWorkflow(self.session, self.auto_commit)
        return self._workflows

    def jobs(self) -> DBJob:
        if not self._jobs:
            self._jobs = DBJob(self.session, self.auto_commit)
        return self._jobs

    def steps(self) -> DBStep:
        if not self._steps:
            self._steps = DBStep(self.session, self.auto_commit)
        return self._steps

    def vars(self) -> DBVars:
        if not self._vars:
            self._vars = DBVars(self.session, self.auto_commit)
        return self._vars

    def config(self) -> DBConfig:
        if not self._config:
            self._config = DBConfig(self.session, self.auto_commit)
        return self._config

    def commit(self) -> None:
        self.session.commit()

    def refresh_record(self, record: any) -> None:
        self.session.refresh(record)

    def select(self, sql: str, params: dict = None) -> list:
        result = self.session.execute(text(sql), params)
        rows = result.fetchall()
        if len(rows) == 0:
            return []

        return [dict(zip(result.keys(), row)) for row in rows]

    def execute(self, sql: str, params: dict = None) -> None:
        self.session.execute(text(sql), params)
        self.session.flush()

    def get_tables(self) -> list:
        metadata = MetaData()
        metadata.reflect(bind=self._engine)
        table_names = metadata.tables.keys()
        return list(table_names)
