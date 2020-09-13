from decimal import Decimal
from typing import Optional
from urllib.parse import urlparse

from bson import CodecOptions, Decimal128
from bson.codec_options import TypeCodec, TypeRegistry
from pymongo import IndexModel, MongoClient
from pymongo.collection import Collection


class DecimalCodec(TypeCodec):
    python_type = Decimal
    bson_type = Decimal128

    def transform_python(self, value):
        return Decimal128(value)

    def transform_bson(self, value):
        return value.to_decimal()


class DB:
    def __init__(self, db_url: str):
        self._client = MongoClient(db_url)
        self._database = self._client[urlparse(db_url).path[1:]]
        self.bot = self._init_collection("bot")
        self.worker = self._init_collection(
            "worker",
            [
                IndexModel("name", unique=True),
                IndexModel("created_at"),
            ],
        )
        self.data = self._init_collection(
            "data",
            [
                IndexModel("worker"),
                IndexModel("status"),
                IndexModel("created_at"),
            ],
        )

    def close(self):
        self._client.close()

    def get_collection_names(self) -> list[str]:
        return self._database.list_collection_names()

    def get_collection(self, name: str) -> Collection:
        return self._database[name]

    def _init_collection(self, col_name: str, indexes: Optional[list[IndexModel]] = None) -> Collection:
        codecs = CodecOptions(type_registry=TypeRegistry([c() for c in [DecimalCodec]]))
        col = self._database.get_collection(col_name, codecs)
        if indexes:
            col.create_indexes(indexes)
        return col
