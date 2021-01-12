from logging import Logger
from typing import Any, Dict, List, Optional

from mb_commons import ParallelTasks, hrequest, synchronized_parameter, utc_now
from wrapt import synchronized

from app.config import AppConfig
from app.core.db import DB
from app.core.models import Data, DataStatus, Worker, WorkerCreate
from app.core.services import BaseService
from app.core.services.system_service import SystemService


class WorkerService(BaseService):
    def __init__(self, config: AppConfig, log: Logger, db: DB, system_service: SystemService):
        super().__init__(config, log, db)
        self.system_service = system_service

    @synchronized
    def create(self, worker: WorkerCreate) -> Worker:
        if self.db.worker.count({"name": worker.name}) > 0:
            raise ValueError(f"a worker with the name '{worker.name}' exists already")

        new_id = self.db.worker.insert_one(Worker(**worker.dict())).inserted_id
        return self.db.worker.get(new_id)

    def find_for_work(self) -> List[Worker]:
        workers = self.db.worker.collection.aggregate(
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
                {"$limit": self.system_service.get_bot().worker_limit},
            ],
        )
        return [Worker(**w) for w in workers]

    def start_worker(self, pk) -> Optional[Worker]:
        return self.db.worker.find_by_id_and_update(pk, {"$set": {"started": True}})

    def stop_worker(self, pk) -> Optional[Worker]:
        return self.db.worker.find_by_id_and_update(pk, {"$set": {"started": False}})

    @synchronized_parameter(arg_index=1)
    def work(self, pk):
        self.log.debug("work(%s)", pk)
        worker = self.db.worker.get_or_none(pk)
        if not worker or not worker.started:
            return False

        r = hrequest(worker.source, timeout=self.system_service.get_bot().timeout)
        worker_updated = {"last_work_at": utc_now()}
        data: Dict[str, Any] = {"worker": worker.name}
        if r.is_timeout_error():
            data["status"] = DataStatus.timeout
        elif not r.is_error():
            if r.json_parse_error:
                data["status"] = DataStatus.json_error
            else:
                data["status"] = DataStatus.ok
                data["data"] = r.json
        else:
            data["status"] = DataStatus.error

        self.db.data.insert_one(Data(**data))
        self.db.worker.update_by_id(pk, {"$set": worker_updated})
        return True

    @synchronized
    def process_workers(self):
        self.log.debug("WorkerService.process_workers()")
        workers = self.find_for_work()
        if not workers:
            return

        tasks = ParallelTasks(max_workers=self.system_service.get_bot().worker_limit)
        for w in workers:
            tasks.add_task(f"work_{w.name}", self.work, args=(w.id,))
        tasks.execute()
