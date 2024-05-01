import datetime
import math
import random
from typing import Mapping, Any

from bson import ObjectId

from utils.db_operation import MongodbOperation


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

    def find_book_by_id(self, book_id: str) -> Mapping[str, Any] | None:
        """
        按照ObjectId查询图书
        :param book_id: ObjectId
        :return: 图书
        """
        book = self.db.book_find_one({"_id": ObjectId(book_id)})
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


if __name__ == "__main__":
    book_service = BookService()
    for i in range(1, 100):
        book_service.create_book(isbn=str(random.randint(100000, 999999)), title="图书" + str(i),
                                 price=round(random.random() * 100, 2), stock=random.randint(1, 100))
