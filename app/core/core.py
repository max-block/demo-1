import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from mb_commons import Scheduler

from app.config import AppConfig
from app.core.db import DB
from app.core.services.system_service import SystemService
from app.core.services.worker_service import WorkerService


class Core:
    def __init__(self, config: AppConfig):
        self.config = config
        self.log = logging.getLogger("app")
        self.init_logger()

        self.db: DB = DB(config.DATABASE_URL)
        self.system_service: SystemService = SystemService(config, self.log, self.db)
        self.worker_service: WorkerService = WorkerService(config, self.log, self.db, self.system_service)
        self.scheduler = self.init_scheduler()
        self.startup()
        self.log.info("app started")

    def init_scheduler(self) -> Scheduler:
        scheduler = Scheduler(self.log)
        scheduler.add_job(self.worker_service.process_workers, 2)

        scheduler.start()
        self.log.debug("scheduler started")
        return scheduler

    def init_logger(self):
        Path(self.config.DATA_DIR).mkdir(exist_ok=True)

        self.log.setLevel(logging.DEBUG if self.config.DEBUG else logging.INFO)
        self.log.propagate = False

        fmt = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(fmt)
        self.log.addHandler(console_handler)

        file_handler = RotatingFileHandler(f"{self.config.DATA_DIR}/app.log", maxBytes=10 * 1024 * 1024, backupCount=1)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(fmt)
        self.log.addHandler(file_handler)

    def startup(self):
        pass

    def shutdown(self):
        self.scheduler.stop()
        self.db.close()
        self.log.info("app stopped")
        # noinspection PyUnresolvedReferences,PyProtectedMember
        os._exit(0)
