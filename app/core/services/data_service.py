from logging import Logger
from typing import Any, Optional

from app.config import AppConfig
from app.core.db import DB
from app.core.models import Data, DataStatus
from app.core.services import BaseService


class DataService(BaseService):
    def __init__(self, config: AppConfig, log: Logger, db: DB):
        super().__init__(config, log, db)

    def create(self, data: Data):
        self.db.data.insert_one(data.to_doc())

    def find(self, worker: Optional[str], status: Optional[DataStatus], limit: int) -> list[Data]:
        q: dict[str, Any] = {}
        if worker:
            q["worker"] = worker
        if status:
            q["status"] = status
        return [Data(**d) for d in self.db.data.find(q, sort=[("created_at", -1)], limit=limit)]
