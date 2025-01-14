from os import environ

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


# TODO: Using raw book datas for now, will be modified later
class DatabaseServiceProvider:
    _client: MongoClient
    _db: Database
    col_users: Collection
    col_raw_book_datas: Collection
    col_book_libraries: Collection
    col_book_tracking_statuses: Collection
    col_feed: Collection
    col_pools: Collection

    def __init__(self):
        mongo_url = environ.get("MONGO_URL")

        assert mongo_url is not None, "MONGO_URL env variable must be set"

        # noinspection SpellCheckingInspection
        self._client = MongoClient(mongo_url)
        self._db = self._client["database"]

        self.col_users = self._db["users"]
        self.col_raw_book_datas = self._db["rawBookDatas"]
        self.col_book_libraries = self._db["bookLibraries"]
        self.col_book_tracking_statuses = self._db["bookTrackingStatuses"]
        self.col_feed = self._db["feed"]
        self.col_pools = self._db["pools"]
