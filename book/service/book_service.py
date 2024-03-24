import math
import random

from utils.db_operation import MongodbOperation


class BookService:
    def __init__(self):
        self.db = MongodbOperation("readingforum", "book")

    def create_book(self, **kwargs):
        """
        新增书籍
        :param kwargs: 书籍信息
        :return: 是否插入成功
        """
        res = self.db.book_insert_one(kwargs)
        return res.acknowledged
