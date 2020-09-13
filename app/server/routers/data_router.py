from typing import Optional

from fastapi import APIRouter

from app.core.core import Core
from app.core.models import DataStatus


def init(core: Core) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def data_data(worker: Optional[str] = None, status: Optional[DataStatus] = None, limit: int = 100):
        return core.data_service.find(worker, status, limit)

    return router
