from typing import Optional

from fastapi import APIRouter
from mb_commons.mongo import make_query

from app.core.core import Core
from app.core.models import DataStatus


def init(core: Core) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def data_data(worker: Optional[str] = None, status: Optional[DataStatus] = None, limit: int = 100):
        return core.db.data.find(make_query(worker=worker, status=status), "-created_at", limit)

    return router
