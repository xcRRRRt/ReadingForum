from typing import List, Mapping

from bson import ObjectId

from utils.dbconnect import get_db_handle
from pymongo.errors import PyMongoError

COLLECTION_NAME = "post"


def insert_post(**kwargs) -> bool:
    """
    插入一个帖子
    :param kwargs: 帖子数据
    """
    try:
        db_handle = get_db_handle(COLLECTION_NAME)
        res = db_handle.insert_one(kwargs)
        return res.acknowledged
    except PyMongoError as e:
        print(f"An error occurred while inserting post: {e}")
        return False


def find_post(_filter: dict):
    """
    通过唯一键查询post
    :param _filter: 过滤器，键必须是唯一键
    """
    try:
        db_handle = get_db_handle(COLLECTION_NAME)
        if "_id" in _filter:
            _filter["_id"] = ObjectId(_filter["_id"])
        doc = db_handle.find_one(_filter)
        return doc
    except PyMongoError as e:
        print(f"An error occurred while finding post: {e}")
        return None


# if "__main__" == __name__:
#     print(find_post({"_id": "65f2fd1196e5a9e324ade219"}))

# def find_posts(_filter: dict):
#     """
#     模糊查询post
#     :param _filter: 过滤器，支持模糊查询，{key, 模糊查询的内容}
#     """
#     db_handle = get_db_handle(COLLECTION_NAME)
#     query = {}
#     for k, v in _filter.items():
#         query[k] = {"$regex": v}
#     docs = db_handle.find(query)
