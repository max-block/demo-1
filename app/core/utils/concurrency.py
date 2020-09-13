import functools
from collections import Callable, defaultdict
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Lock
from typing import Any, Optional, Tuple


class ParallelTasks:
    @dataclass
    class Task:
        key: str
        func: Callable
        args: Tuple
        kwargs: dict

    def __init__(self, max_workers=5, timeout=None):
        self.max_workers = max_workers
        self.timeout = timeout
        self.tasks: list[ParallelTasks.Task] = []
        self.exceptions: dict[str, Exception] = {}
        self.error = False
        self.timeout_error = False
        self.result: dict[str, Any] = {}

    def add_task(self, key: str, func: Callable, args: Tuple = (), kwargs: Optional[dict] = None):
        if kwargs is None:
            kwargs = {}
        # noinspection PyCallByClass
        self.tasks.append(ParallelTasks.Task(key, func, args, kwargs))

    def execute(self) -> None:
        with ThreadPoolExecutor(self.max_workers) as executor:
            future_to_key = {executor.submit(task.func, *task.args, **task.kwargs): task.key for task in self.tasks}
            try:

                result_map = futures.as_completed(future_to_key, timeout=self.timeout)
                for future in result_map:
                    key = future_to_key[future]
                    try:
                        self.result[key] = future.result()
                    except Exception as e:
                        self.error = True
                        self.exceptions[key] = e
            except futures.TimeoutError:
                self.error = True
                self.timeout_error = True


def synchronized_parameter(lock_parameter_index=0):
    locks = defaultdict(Lock)

    def outer(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                with locks[args[lock_parameter_index]]:
                    return func(*args, **kwargs)
            finally:
                locks.pop(args[lock_parameter_index], None)

        return wrapper

    outer.locks = locks
    outer.locked_parameters = list(locks.keys())
    return outer
