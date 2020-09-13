import faulthandler
import signal

from app.config import AppConfig
from app.core.core import Core
from app.server.server import Server

faulthandler.enable()

settings = AppConfig()
core = Core(settings)
app = Server(core).get_app()

for s in [signal.SIGTERM, signal.SIGINT, signal.SIGQUIT, signal.SIGHUP]:
    signal.signal(s, core.shutdown)  # type: ignore
