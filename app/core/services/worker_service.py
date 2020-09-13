from logging import Logger
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel
from pymongo.collection import ReturnDocument
from pymongo.results import DeleteResult
from wrapt import synchronized

from app.config import AppConfig
from app.core.db import DB
from app.core.models import Data, DataStatus, Worker
from app.core.services import BaseService
from app.core.services.bot_service import BotService
from app.core.services.data_service import DataService
from app.core.utils.concurrency import ParallelTasks, synchronized_parameter
from app.core.utils.hrequest import HResponseStatus, hrequest
from app.core.utils.time import utc_now


class CreateWorkerParams(BaseModel):
    name: str
    source: str
    interval: int


class WorkerService(BaseService):
    def __init__(self, config: AppConfig, log: Logger, db: DB, bot_service: BotService, data_service: DataService):
        super().__init__(config, log, db)
        self.bot_service = bot_service
        self.data_service = data_service

    @synchronized
    def create(self, worker: CreateWorkerParams) -> Worker:
        if self.db.worker.count_documents({"name": worker.name}) > 0:
            raise ValueError(f"a worker with the name '{worker.name}' exists already")

        new_doc = Worker(**worker.dict()).to_doc()
        new_id = self.db.worker.insert_one(new_doc).inserted_id
        return Worker(**self.db.worker.find_one({"_id": new_id}))

    def find(self, started: Optional[bool], limit: int) -> list[Worker]:
        q: dict[str, Any] = {}
        if started is not None:
            q["started"] = started
        return [Worker(**w) for w in self.db.worker.find(q, sort=[("created_at", -1)], limit=limit)]

    def find_for_work(self) -> list[Worker]:
        workers = self.db.worker.aggregate(
            [
                {
                    "$match": {
                        "started": True,
                        "$or": [
                            {"last_work_at": None},
                            {
                                "$expr": {
                                    "$lt": [
                                        "$checked_at",
                                        {
                                            "$subtract": [
                                                "$$NOW",
                                                {"$multiply": ["$interval", 1000]},
                                            ],
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                },
                {"$sort": {"last_work_at": 1}},
                {"$limit": self.bot_service.get().worker_limit},
            ],
        )
        return [Worker(**w) for w in workers]

    def get(self, pk) -> Optional[Worker]:
        res = self.db.worker.find_one({"_id": ObjectId(pk)})
        if res:
            return Worker(**res)

    def delete(self, pk) -> DeleteResult:
        return self.db.worker.delete_one({"_id": ObjectId(pk)}).raw_result

    def update(self, pk, updated: dict) -> Optional[Worker]:
        res = self.db.worker.find_one_and_update(
            {"_id": ObjectId(pk)},
            updated,
            return_document=ReturnDocument.AFTER,
        )
        if res:
            return Worker(**res)

    def start_worker(self, pk) -> Optional[Worker]:
        return self.update(pk, {"$set": {"started": True}})

    def stop_worker(self, pk) -> Optional[Worker]:
        return self.update(pk, {"$set": {"started": False}})

    @synchronized_parameter(lock_parameter_index=1)
    def work(self, pk):
        self.log.debug("work(%s)", pk)
        worker = self.get(pk)
        if not worker or not worker.started:
            return False

        r = hrequest(worker.source, timeout=self.bot_service.get().timeout)
        worker_updated = {"last_work_at": utc_now()}
        data = {"worker": worker.name}
        if r.status == HResponseStatus.TIMEOUT:
            data["status"] = DataStatus.TIMEOUT
        elif r.status == HResponseStatus.OK:
            if r.json_parse_error:
                data["status"] = DataStatus.JSON_ERROR
            else:
                data["status"] = DataStatus.OK
                data["data"] = r.json
        else:
            data["status"] = DataStatus.ERROR

        self.data_service.create(Data(**data))
        self.update(pk, {"$set": worker_updated})
        return True

    @synchronized
    def process_workers(self):
        self.log.debug("WorkerService.process_workers()")
        workers = self.find_for_work()
        if not workers:
            return

        tasks = ParallelTasks(max_workers=self.bot_service.get().worker_limit)
        for w in workers:
            tasks.add_task(f"work_{w.name}", self.work, args=(w.id,))
        tasks.execute()
