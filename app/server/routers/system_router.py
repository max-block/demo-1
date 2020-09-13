import time
import tracemalloc

from fastapi import APIRouter
from starlette.responses import PlainTextResponse

from app.core.core import Core


def init(core: Core) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def system_stats():
        return core.system_service.get_stats()

    @router.get("/log", response_class=PlainTextResponse)
    def view_logfile():
        return core.system_service.read_logfile()

    @router.delete("/log")
    def clean_logfile():
        core.system_service.clean_logfile()
        return True

    @router.post("/start_tracemalloc")
    def start_tracemalloc():
        tracemalloc.start()
        return {"message": "tracemalloc was started"}

    @router.post("/stop_tracemalloc")
    def stop_tracemalloc():
        tracemalloc.stop()
        return {"message": "tracemalloc was stopped"}

    @router.get("/tracemalloc_snapshot", response_class=PlainTextResponse)
    def tracemalloc_snapshot():
        return core.system_service.tracemalloc_snapshot()

    @router.get("/test")
    def test():
        time.sleep(10)
        return 777

    return router
