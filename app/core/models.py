from datetime import datetime
from enum import Enum, unique
from typing import Any, List, Optional

from mb_commons import utc_now
from mb_commons.mongo import MongoModel, ObjectIdStr
from pydantic import BaseModel, Field, HttpUrl


# Bot
class Bot(MongoModel):
    id: Optional[int] = Field(None, alias="_id")
    timeout: int = 10  # in seconds
    worker_limit: int = 15  # how many workers can work at once
    bot_started: bool = False
    telegram_token: str = ""
    telegram_polling: bool = False  # Telegram commands will work
    telegram_channel: bool = False  # system_service.send_telegram_message will work
    telegram_channel_id: int = 0
    telegram_admins: List[int] = []


class BotUpdate(BaseModel):
    telegram_token: str
    telegram_polling: bool
    telegram_channel: bool
    telegram_channel_id: int
    telegram_admins: List[int]
    timeout: int
    worker_limit: int


# Worker
class Worker(MongoModel):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    name: str
    source: HttpUrl
    interval: int  # in seconds
    started: bool = False
    last_work_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)


class WorkerCreate(BaseModel):
    name: str
    source: HttpUrl
    interval: int


# Data
@unique
class DataStatus(str, Enum):
    ok = "ok"
    timeout = "timeout"
    proxy_error = "proxy_error"
    json_error = "json_error"
    error = "error"


class Data(MongoModel):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    worker: str
    status: DataStatus
    data: Any
    created_at: datetime = Field(default_factory=utc_now)
