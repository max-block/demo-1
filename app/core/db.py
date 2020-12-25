from mb_commons.mongo import MongoCollection, MongoConnection
from pymongo import IndexModel

from app.core.models import Bot, Data, Worker


class DB:
    def __init__(self, db_url: str):
        conn = MongoConnection.connect(db_url)
        self._client = conn.client
        self._database = conn.database
        self.bot: MongoCollection[Bot] = MongoCollection(Bot, conn.database, "bot")
        self.worker: MongoCollection[Worker] = MongoCollection(
            Worker,
            conn.database,
            "worker",
            [IndexModel("name", unique=True), IndexModel("created_at")],
        )
        self.data: MongoCollection[Data] = MongoCollection(
            Data,
            conn.database,
            "data",
            [
                IndexModel("worker"),
                IndexModel("status"),
                IndexModel("created_at"),
            ],
        )

    def close(self):
        self._client.close()

    def get_stats(self):
        db_stats = {}
        for col in self._database.list_collection_names():
            db_stats[col] = self._database[col].count_documents({})
        return db_stats
