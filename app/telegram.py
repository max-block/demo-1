import functools
from threading import Thread
from typing import List, Optional

from telebot import TeleBot
from telebot.types import Message
from telebot.util import split_string

from app.core.core import Core


def auth(*, admins: List[int], bot: TeleBot):
    def outer(func):
        @functools.wraps(func)
        def wrapper(message: Message):
            if message.chat.id in admins:
                return func(message)
            else:
                bot.send_message(message.chat.id, "Who are you?")

        return wrapper

    return outer


class Telegram:
    """Telegram is an alternative UI to the web API for the project. It works via telegram commands.
    If you need just to send a message to the project channel / group, use system_service.send_telegram_message()"""

    def __init__(self, core: Core):
        self.core = core
        self.bot: Optional[TeleBot] = None
        self.is_started = False

    def start(self):
        """
        Telegram bot can be started only if these bot settings are set:
        - telegram_token
        - telegram_admins
        - telegram_polling
        """
        app_bot = self.core.system_service.get_bot()
        if app_bot.telegram_token and app_bot.telegram_admins and app_bot.telegram_polling:
            Thread(target=self._start).start()
            return True

    def _start(self):
        try:
            self.bot = TeleBot(self.core.system_service.get_bot().telegram_token, skip_pending=True)
            self._init_commands()
            self.is_started = True
            self.core.log.debug("telegram started")
            self.bot.polling(none_stop=True)
        except Exception as e:
            self.is_started = False
            self.core.log.error(f"telegram polling: {str(e)}")

    def stop(self):
        self.is_started = False
        self.bot.stop_bot()
        self.core.log.debug("telegram stopped")

    def _init_commands(self):
        @self.bot.message_handler(commands=["start", "help"])
        @auth(admins=self.core.system_service.get_bot().telegram_admins, bot=self.bot)
        def help_handler(message: Message):
            result = """
/workers - List all workers
/start_worker ${worker_name} - Start the worker
/stop_worker ${worker_name} - Start the worker
            """
            self._send_message(message.chat.id, result)

        @self.bot.message_handler(commands=["ping"])
        @auth(admins=self.core.system_service.get_bot().telegram_admins, bot=self.bot)
        def ping_handler(message: Message):
            text = message.text.replace("/ping", "").strip()
            self._send_message(message.chat.id, f"pong {text}")

        @self.bot.message_handler(commands=["workers"])
        @auth(admins=self.core.system_service.get_bot().telegram_admins, bot=self.bot)
        def workers_handler(message: Message):
            result = ""
            for w in self.core.db.worker.find({}, "name"):
                result += f"{w.name}, source={w.source}, started={w.started}\n"
            self._send_message(message.chat.id, result)

        @self.bot.message_handler(commands=["start_worker"])
        @auth(admins=self.core.system_service.get_bot().telegram_admins, bot=self.bot)
        def start_handler(message: Message):
            chat_id = message.chat.id
            worker_name = message.text.replace("/start_worker", "").strip()
            if not worker_name:
                return self._send_message(chat_id, "usage: /start_worker ${worker_name}")

            worker = self.core.db.worker.find_one({"name": worker_name})
            if worker:
                self.core.worker_service.start_worker(worker.id)
                return self._send_message(chat_id, "worker was started")
            else:
                self._send_message(message.chat.id, "worker was not found")

        @self.bot.message_handler(commands=["stop_worker"])
        @auth(admins=self.core.system_service.get_bot().telegram_admins, bot=self.bot)
        def stop_handler(message: Message):
            chat_id = message.chat.id
            worker_name = message.text.replace("/stop_worker", "").strip()
            if not worker_name:
                return self._send_message(chat_id, "usage: /stop_worker ${worker_name}")

            worker = self.core.db.worker.find_one({"name": worker_name})
            if worker:
                self.core.worker_service.stop_worker(worker.id)
                return self._send_message(chat_id, "worker was stopped")
            else:
                return self._send_message(chat_id, "worker was not found")

    def _send_message(self, chat_id: int, message: str):
        for text in split_string(message, 4096):
            self.bot.send_message(chat_id, text)  # type:ignore
