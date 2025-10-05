from loguru import logger
from src.database.database import Database


class Service:
    database: Database = None
    log: logger = None

    def __init__(self, log: logger, database: Database):
        self.log = log
        self.database = database

    def run(self) -> bool:
        raise NotImplementedError("Service.run() not implemented")
