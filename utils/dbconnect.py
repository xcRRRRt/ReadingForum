from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

DATABASE_NAME = "readingforum"


def get_db_handle(collection_name: str) -> Collection:
    try:
        client = MongoClient(host="mongodb://localhost", port=27017)
        col = client[DATABASE_NAME][collection_name]
        return col
    except PyMongoError as e:
        print(f"Error connecting to {DATABASE_NAME} {collection_name}: {e}")
