from mb_commons import mongo
from pymongo import IndexModel, MongoClient
from pymongo.collection import Collection


class DB:
    def __init__(self, db_url: str):
        self._client = MongoClient(db_url)
        self._database = self._client[mongo.get_database_name_from_url(db_url)]
        self.bot = mongo.init_collection(self._database, "bot")
        self.worker = mongo.init_collection(
            self._database,
            "worker",
            [
                IndexModel("name", unique=True),
                IndexModel("created_at"),
            ],
        )
        self.data = mongo.init_collection(
            self._database,
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
