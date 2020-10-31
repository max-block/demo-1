from datetime import datetime
from enum import Enum, unique
from typing import Any, Optional

from mb_commons import utc_now
from pydantic import BaseModel, Field, HttpUrl


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        return str(v)


class MongoModel(BaseModel):
    def to_doc(self) -> dict:
        doc = self.dict()
        if doc["id"] is not None:
            doc["_id"] = doc["id"]
        del doc["id"]
        return doc


class Bot(MongoModel):
    id: Optional[int] = Field(None, alias="_id")
    timeout: int = 10  # in seconds
    worker_limit: int = 15  # how many workers can work at once
    bot_started: bool = False


class Worker(MongoModel):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    name: str
    source: HttpUrl
    interval: int  # in seconds
    started: bool = False
    last_work_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)


@unique
class DataStatus(str, Enum):
    OK = "OK"
    TIMEOUT = "TIMEOUT"
    PROXY_ERROR = "PROXY_ERROR"
    JSON_ERROR = "JSON_ERROR"
    ERROR = "ERROR"


class Data(MongoModel):
    id: Optional[ObjectIdStr] = Field(None, alias="_id")
    worker: str
    status: DataStatus
    data: Any
    created_at: datetime = Field(default_factory=utc_now)
