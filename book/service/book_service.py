import datetime
import math
import pprint
import random
from typing import *
from typing import Tuple, Any

from bson import ObjectId
from pymongo.results import UpdateResult, InsertOneResult
from utils.datetime_util import get_datetime_by_objectId

from utils.db_operation import MongodbOperation
from user.service.userinfo_service import UserInfoService

userinfo_service = UserInfoService()


class BookService:
    def __init__(self):
        self.db = MongodbOperation("readingforum", "book")
        self.map_fields = {"status": {1: "在售", 2: "售空", 3: "下架"}}

    def create_book(self, **kwargs):
        """
        新增书籍
        :param kwargs: 书籍信息
        :return: 是否插入成功
        """
        data = {k: v for k, v in kwargs.items() if v is not None}
        res = self.db.book_insert_one(data)
        return res.acknowledged, str(res.inserted_id)

    def find_book_by_id(self, book_id: str, *required_fields, map_fields: bool = False) -> dict[str, Any] | None:
        """
        按照ObjectId查询图书
        :param book_id: ObjectId
        :param required_fields: 需要的字段
        :param map_fields: 是否映射字段
        :return: 图书
        """
        projection = {field: 1 for field in required_fields}
        book = self.db.book_find_one({"_id": ObjectId(book_id)}, projection=projection)
        if map_fields:
            for field, field_map_dict in self.map_fields.items():
                if field in book:
                    book[field + "_mapped"] = field_map_dict[book[field]]
        book["id"] = str(book["_id"])
        return book

    def update_book_by_id(self, book_id: str, **kwargs) -> bool:
        """
        按照ObjectId更新图书
        :param book_id: ObjectId
        :param kwargs: 其他数据
        """
        to_save, to_delete = dict(), dict()
        for key, value in kwargs.items():
            if value is not None:
                if isinstance(value, datetime.date):
                    value: datetime.date = datetime.datetime.combine(value, datetime.time())
                to_save[key] = value
            else:
                to_delete[key] = 1
        res_update = self.db.book_update_one({'_id': ObjectId(book_id)}, {'$set': to_save})
        res_delete = self.db.book_update_one({'_id': ObjectId(book_id)}, {'$unset': to_delete})
        return res_update.acknowledged and res_delete.acknowledged

    def push_comment(self, book_id: str, user_id: str | ObjectId, comment: str) -> UpdateResult:
        doc = {
            "id": ObjectId(),
            "user_id": ObjectId(user_id),
            "comment": comment,
        }
        res = self.db.book_update_one({'_id': ObjectId(book_id)},
                                      {'$push': {'comments': doc}})
        userinfo_service.add_comments(user_id, book_id, doc['id'])
        return res

    def push_post(self, book_id: str | ObjectId, post_id: str | ObjectId) -> UpdateResult:
        res = self.db.book_update_one(
            {'_id': ObjectId(book_id)},
            {'$push': {'posts': ObjectId(post_id)}}
        )
        return res

    def find_book_comments(self, book_id: str, skip: int, limit: int, sort_by: dict[str, int]) -> List[Mapping[str, Any]]:
        sort = dict()
        for k, v in sort_by.items():
            if k == 'time':
                sort['id'] = v
        pipeline = [
            {'$match': {'_id': ObjectId(book_id)}},
            {'$unwind': '$comments'},
            {'$replaceRoot': {'newRoot': '$comments'}},
            {'$sort': sort},
            {'$skip': skip},
            {'$limit': limit},
        ]

        comments = list(self.db.book_aggregate(pipeline))
        formatted_comments = []

        for comment in comments:
            comment['time'] = get_datetime_by_objectId(comment.get("id"))
            user_info = userinfo_service.find_userinfo_by_id(comment['user_id'], "avatar_url", "username")
            comment.update(user_info)
            formatted_comments.append(comment)
        return formatted_comments

    def find_book_by_isbn_or_title(self, isbn_or_title: str, *required_fields, skip: int, limit: int, sort_by=None) -> List[dict[str, Any]]:
        filter_ = {
            "$or": [
                {"isbn": {"$regex": isbn_or_title}},
                {"title": {"$regex": isbn_or_title}},
            ]
        }
        projection = {field: 1 for field in required_fields}
        cursor = self.db.book_find(filter_, projection)
        if sort_by:
            cursor = cursor.sort(sort_by)
        cursor = cursor.skip(skip).limit(limit)
        books = list(cursor)
        for book in books:
            book["id"] = str(book["_id"])
            del book["_id"]
        return books

    def find_book_by_labels(self, labels: list[str], skip: int, limit: int, sort_by: dict[str, int]) -> List[Mapping[str, Any]]:
        pipeline = [
            {"$match": {"label": {"$in": labels}}},
            {
                "$addFields": {
                    "match_label_count": {
                        "$size": {
                            "$setIntersection": ["$label", labels]
                        }
                    }
                }
            },
            {"$sort": {"match_label_count": -1}},
            {"$skip": skip},
            {"$limit": limit}
        ]
        books = list(self.db.book_aggregate(pipeline))
        for book in books:
            book["id"] = str(book["_id"])
            del book["_id"]
        return books

    def find_new_books(self, skip: int, limit: int, sort_by=None) -> List[Dict[str, Any]]:
        """

        :param skip:
        :param limit:
        :param sort_by:
        :return:
        """
        if sort_by is None:
            sort_by = {"_id": -1}
        cursor = self.db.book_find({}, projection={'title': 1,
                                                   'isbn': 1,
                                                   'cover': 1,
                                                   'introduction': 1,
                                                   'label': 1,
                                                   'comment_count': 1,
                                                   'post_count': 1, })
        if sort_by:
            cursor = cursor.sort(sort_by)
        books = list(cursor.skip(skip).limit(limit))
        for book in books:
            book["id"] = str(book["_id"])
            del book["_id"]
        return books

    def find_hottest_books(self, skip: int, limit: int, sort_by=None) -> List[Dict[str, Any]]:
        """

        :param skip:
        :param limit:
        :param sort_by:
        :return:
        """
        # if sort_by is None:
        #     sort_by = {}
        pipeline = [
            {
                "$set": {
                    "comment_count": {"$size": {"$ifNull": ["$comments", []]}},
                    "post_count": {"$size": {"$ifNull": ["$posts", []]}}
                }
            },
            {
                "$project": {
                    'title': 1,
                    'isbn': 1,
                    'cover': 1,
                    'introduction': 1,
                    'label': 1,
                    'comment_count': 1,
                    'post_count': 1,
                    'comment_post_count': {
                        "$add": ["$comment_count", "$post_count"]
                    }
                }
            },
            {
                "$sort": {"comment_post_count": -1}
            },
            {"$skip": skip},
            {"$limit": limit}
        ]
        books = list(self.db.book_aggregate(pipeline))
        # pprint.PrettyPrinter().pprint(books)
        for book in books:
            book["id"] = str(book["_id"])
            del book["_id"]
        return books


if __name__ == "__main__":
    book_service = BookService()
    # for i in range(1, 100):
    #     book_service.create_book(isbn=str(random.randint(100000, 999999)), title="图书" + str(i),
    #                              price=round(random.random() * 100, 2), stock=random.randint(1, 100))
    # print(book_service.find_book_comments("66367f4d787d221d08173540", 0, 10, {"time": 1}))
    # print(book_service.find_book_by_isbn_or_title("孙子", skip=0, limit=10, sort_by={}))
    pprint.PrettyPrinter().pprint(book_service.find_book_by_labels(['102', '96'], 0, 10, {}))
    # print(book_service.find_new_books(0, 5))
    # book_service.find_hottest_books(0, 4)
