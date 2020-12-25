import threading
import tracemalloc
from logging import Logger

from pydantic import BaseModel
from wrapt import synchronized

from app.config import AppConfig
from app.core.db import DB
from app.core.models import Bot
from app.core.services import BaseService


class UpdateBotParams(BaseModel):
    timeout: int
    worker_limit: int


class SystemService(BaseService):
    def __init__(self, config: AppConfig, log: Logger, db: DB):
        super().__init__(config, log, db)
        self.logfile = self.config.DATA_DIR + "/app.log"
        self._bot: Bot = self._init_bot()

    @synchronized
    def update_bot(self, params: UpdateBotParams) -> Bot:
        self._update_bot(params.dict())
        return self.get_bot()

    def get_bot(self) -> Bot:
        return self._bot.copy()

    def start_bot(self) -> Bot:
        self._update_bot({"bot_started": True})
        return self.get_bot()

    def stop_bot(self) -> Bot:
        self._update_bot({"bot_started": False})
        return self.get_bot()

    @synchronized
    def _update_bot(self, updated: dict):
        self._bot = self._bot.copy(update=updated)
        self.db.bot.update_by_id(1, {"$set": updated})

    @synchronized
    def _init_bot(self) -> Bot:
        if not self.db.bot.get_or_none(1):
            bot = Bot()
            bot.id = 1
            self.db.bot.insert_one(bot)
        return self.db.bot.get(1)

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
