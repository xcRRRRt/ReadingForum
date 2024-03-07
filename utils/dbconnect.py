from pymongo import MongoClient
from pymongo.collection import Collection

DATABASE_NAME = "readinigforum"


def get_db_handle(collection_name: str) -> Collection:
    client = MongoClient(host="mongodb://localhost", port=27017)
    col = client[DATABASE_NAME][collection_name]
    return col
