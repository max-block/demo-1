from typing import Optional

from fastapi import APIRouter

from app.core.core import Core
from app.core.models import Worker
from app.core.services.worker_service import CreateWorkerParams


def init(core: Core) -> APIRouter:
    router = APIRouter()

    @router.get("", response_model=list[Worker])
    def get_workers(started: Optional[bool] = None, limit: int = 100):
        return core.worker_service.find(started, limit)

    @router.post("", response_model=Worker)
    def create_worker(worker: CreateWorkerParams):
        return core.worker_service.create(worker)

    @router.get("/{pk}", response_model=Optional[Worker])
    def get_worker(pk):
        return core.worker_service.get(pk)

    @router.delete("/{pk}")
    def delete_worker(pk):
        return core.worker_service.delete(pk)

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
