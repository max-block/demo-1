import faulthandler

from app.config import AppConfig
from app.core.core import Core
from app.server.server import Server

faulthandler.enable()

settings = AppConfig()
core = Core(settings)
app = Server(core).get_app()
