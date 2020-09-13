import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from logging import Logger
from threading import Thread
from typing import Callable

from app.core.utils.time import utc_now


class Scheduler:
    @dataclass
    class Job:
        func: Callable
        interval: int
        is_running: bool = False
        last_at: datetime = field(default_factory=utc_now)

    def __init__(self, log: Logger):
        self.log = log
        self.stopped = False
        self.jobs: list[Scheduler.Job] = []

    def add_job(self, func: Callable, interval: int):
        self.jobs.append(Scheduler.Job(func, interval))

    def start(self):
        Thread(target=self._start).start()

    def stop(self):
        self.stopped = True

    def _start(self):
        while not self.stopped:
            for j in self.jobs:
                if not j.is_running and j.last_at < utc_now() - timedelta(seconds=j.interval):
                    j.is_running = True
                    j.last_at = utc_now()
                    Thread(target=self._run_job, args=(j,)).start()
            time.sleep(0.5)

    def _run_job(self, job: Job):
        if self.stopped:
            return
        try:
            job.func()
        except Exception as err:
            self.log.error("scheduler error:", exc_info=err)
        finally:
            job.is_running = False
