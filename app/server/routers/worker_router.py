from typing import List, Optional

from fastapi import APIRouter
from mb_commons.mongo import make_query

from app.core.core import Core
from app.core.models import Worker
from app.core.services.worker_service import CreateWorkerParams


def init(core: Core) -> APIRouter:
    router = APIRouter()

    @router.get("", response_model=List[Worker])
    def get_workers(started: Optional[bool] = None, limit: int = 100):
        return core.db.worker.find(make_query(started=started), "-created_at", limit)

    @router.post("", response_model=Worker)
    def create_worker(worker: CreateWorkerParams):
        return core.worker_service.create(worker)

    @router.get("/{pk}", response_model=Optional[Worker])
    def get_worker(pk):
        return core.db.worker.get_or_none(pk)

    @router.delete("/{pk}")
    def delete_worker(pk):
        return core.db.worker.delete_by_id(pk)

    @router.post("/{pk}/start")
    def start_worker(pk):
        return core.worker_service.start_worker(pk)

    @router.post("/{pk}/stop")
    def stop_worker(pk):
        return core.worker_service.stop_worker(pk)

    @router.post("/{pk}/work")
    def process_worker_work(pk):
        return core.worker_service.work(pk)

    return router
