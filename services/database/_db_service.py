from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from os import environ


# TODO: Using raw book datas for now, will be modified later
class DatabaseServiceProvider:
    _client: MongoClient
    _db: Database
    col_users: Collection
    col_raw_book_datas: Collection

    def __init__(self):
        mongo_username = environ.get("MONGO_USERNAME")
        mongo_password = environ.get("MONGO_PASSWORD")

        # noinspection SpellCheckingInspection
        self._client = MongoClient(
            f"mongodb+srv://{mongo_username}:{mongo_password}@main.0efcq.mongodb.net/?retryWrites=true&w=majority&appName=Main")
        self._db = self._client["database"]

        self.col_users = self._db["users"]
        self.col_raw_book_datas = self._db["rawBookDatas"]
