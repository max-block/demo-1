import threading
import tracemalloc
from logging import Logger

from app.config import AppConfig
from app.core.db import DB
from app.core.services import BaseService


class SystemService(BaseService):
    def __init__(self, config: AppConfig, log: Logger, db: DB):
        super().__init__(config, log, db)
        self.logfile = self.config.DATA_DIR + "/app.log"

    def read_logfile(self) -> str:
        with open(self.logfile) as f:
            return f.read()

    def clean_logfile(self):
        with open(self.logfile, "w") as f:
            f.write("")
        self.log.info("logfile was cleaned")

    def get_stats(self):
        return {"db": self.db.get_stats(), "threads": len(threading.enumerate())}

    @staticmethod
    def tracemalloc_snapshot(key_type="lineno", limit=30) -> str:
        result = ""
        snapshot = tracemalloc.take_snapshot()
        for stat in snapshot.statistics(key_type)[:limit]:
            result += str(stat) + "\n"
        return result
