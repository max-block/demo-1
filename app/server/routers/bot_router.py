from fastapi import APIRouter

from app.core.core import Core
from app.core.services.bot_service import UpdateBotParams


def init(core: Core) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def get_bot():
        return core.bot_service.get()

    @router.put("")
    def update_bot(params: UpdateBotParams):
        return core.bot_service.update(params)

    @router.post("/start")
    def start_bot():
        return core.bot_service.start()

    @router.post("/stop")
    def stop_bot():
        return core.bot_service.stop()

    return router
