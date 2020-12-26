import faulthandler

from app.config import AppConfig
from app.core.core import Core
from app.server.server import Server
from app.telegram import Telegram

faulthandler.enable()

settings = AppConfig()
core = Core(settings)
telegram = Telegram(core)
app = Server(core, telegram).get_app()
