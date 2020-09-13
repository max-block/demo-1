from logging import Logger

from app.config import AppConfig
from app.core.db import DB


class BaseService:
    def __init__(self, config: AppConfig, log: Logger, db: DB):
        self.config = config
        self.log = log
        self.db = db
