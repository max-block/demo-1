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


class BotService(BaseService):
    def __init__(self, config: AppConfig, log: Logger, db: DB):
        super().__init__(config, log, db)
        self._bot: Bot = self._init_bot()

    @synchronized
    def update(self, params: UpdateBotParams) -> Bot:
        self._update(params.dict())
        return self.get()

    def get(self) -> Bot:
        return self._bot.copy()

    def start(self) -> Bot:
        self._update({"bot_started": True})
        return self.get()

    def stop(self) -> Bot:
        self._update({"bot_started": False})
        return self.get()

    @synchronized
    def _update(self, updated: dict):
        self._bot = self._bot.copy(update=updated)
        self.db.bot.update_one({"_id": 1}, {"$set": updated})

    @synchronized
    def _init_bot(self) -> Bot:
        if not self.db.bot.find_one({"_id": 1}):
            bot = Bot()
            bot.id = 1
            self.db.bot.insert_one(bot.to_doc())
        res = self.db.bot.find_one({"_id": 1})
        if res:
            return Bot(**res)
        raise Exception("can't get bot from db")
