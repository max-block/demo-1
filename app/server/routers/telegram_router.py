from fastapi import APIRouter

from app.telegram import Telegram


def init(telegram: Telegram) -> APIRouter:
    router = APIRouter()

    @router.get("")
    def get_telegram_status():
        return telegram.is_started

    @router.post("/start")
    def start_telegram():
        return telegram.start()

    @router.post("/stop")
    def stop_telegram():
        return telegram.stop()

    return router
