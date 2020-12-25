import time
import tracemalloc

from fastapi import APIRouter
from starlette.responses import PlainTextResponse

from app.core.core import Core
from app.core.services.system_service import UpdateBotParams


def init(core: Core) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def system_stats():
        return core.system_service.get_stats()

    @router.get("/bot")
    def get_bot():
        return core.system_service.get_bot()

    @router.put("/bot")
    def update_bot(params: UpdateBotParams):
        return core.system_service.update_bot(params)

    @router.post("/bot/start")
    def start_bot():
        return core.system_service.start_bot()

    @router.post("/stop")
    def stop_bot():
        return core.system_service.stop_bot()

    @router.get("/log", response_class=PlainTextResponse)
    def view_logfile():
        return core.system_service.read_logfile()

    @router.delete("/log")
    def clean_logfile():
        core.system_service.clean_logfile()
        return True

    @router.post("/tracemalloc/start")
    def start_tracemalloc():
        tracemalloc.start()
        return {"message": "tracemalloc was started"}

    @router.post("/tracemalloc/stop")
    def stop_tracemalloc():
        tracemalloc.stop()
        return {"message": "tracemalloc was stopped"}

    @router.get("/tracemalloc/snapshot", response_class=PlainTextResponse)
    def snapshot_tracemalloc():
        return core.system_service.tracemalloc_snapshot()

    @router.get("/test")
    def test():
        time.sleep(10)
        return 777

    return router
