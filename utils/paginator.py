import math

# 这可能是我写过的最棒的代码，值得和磊一起放在我的β里，靴靴
class Paginator:
    def __init__(self, collection_service,
                 per_page: int = 10,
                 page_range_size: int = 5):
        """
        自定义分页

        类似于 `Django Paginator <https://docs.djangoproject.com/zh-hans/5.0/ref/paginator/#django.core.paginator.Paginator>`_

        :param collection_service: service对象
        :param per_page: 每页有多少个
        :param page_range_size: 显示在页面上的页码应该有多少个

        使用:
        ::::::::
        创建Paginator对象:\n
        >>> from book.service.book_service import BookService
        >>> book_service = BookService()
        >>> paginator = Paginator(book_service, 10, 5)

        设置当前页:\n
        >>> paginator.page = 7


        获取当前页、前一页、下一页:\n
        >>> paginator.page, paginator.previous, paginator.next
        (7, 6, 8)

        获取当前页的内容:\n
        >>> paginator.get_page()
        [{'_id': ObjectId('66000f102873ef7ac9095ff9'), 'isbn': '59', 'title': '图书59', 'price': 62.31},
        {'_id': ObjectId('66000f102873ef7ac9095ffa'), 'isbn': '60', 'title': '图书60', 'price': 27.05}, ...]

        获取邻居页码:\n
        >>> paginator.get_neighbor_page_list()
        [5, 6, 7, 8, 9]

        是否是首页/尾页:\n
        >>> paginator.page = 1
        >>> paginator.is_first_page(), paginator.is_last_page()
        (True, False)

        获取总页数:\n
        >>> paginator.get_page_num()
        11
        """
        self._collection_service = collection_service.db
        self._collection_name = collection_service.db.collection_name
        self._per_page = per_page
        self._page_range_size = page_range_size
        self._page = None
        self._next = None
        self._previous = None

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        """
        设置当前页

        **请不要忘记在创建Paginator对象后调用该方法**

        此外，调用该方法会同时设置上一页和下一页
        """
        self._page = value
        self._previous = self._page - 1
        self._next = self._page + 1

    @property
    def next(self):
        return self._next if self._page != self.get_page_num() else None  # 如果没有下一页则返回None

    @property
    def previous(self):
        return self._previous if self._page != 1 else None

    def get_page(self) -> list:
        """
        获取该页的内容列表
        :return: 改页的内容列表
        """
        skip = (self._page - 1) * self._per_page
        collection_find = getattr(self._collection_service, self._collection_name + "_find")
        objs = collection_find({}).skip(skip).limit(self._per_page)
        return list(objs)

    def _count_objs(self) -> int:
        """
        获取集合中的文档数量
        :return: 文档数量
        """
        count_documents = getattr(self._collection_service, self._collection_name + "_count_documents")
        return count_documents({})

    def get_page_num(self) -> int:
        """
        获取页数
        :return: 页数
        """
        return math.ceil(self._count_objs() / self._per_page)

    def is_first_page(self) -> bool:
        """
        是否是第一页
        :return: 是否是第一页
        """
        return self._page == 1

    def is_last_page(self) -> bool:
        """
        是否是最后一页
        :return: 是否为最后一页
        """
        return self._page == self.get_page_num()

    def get_neighbor_page_list(self) -> list[int]:
        """
        获取邻居页码列表
        :return: 邻居页码列表
        """
        page_num = self.get_page_num()
        half_num = math.floor(self._page_range_size / 2)
        if page_num <= self._page_range_size:  # 如果页数小于要显示的页码范围，则直接返回能访问的页码
            return list(range(1, page_num + 1))
        if self._page <= half_num:  # 1 2 3 4 5 6 7 如果当前页码<=3
            return list(range(1, self._page_range_size + 1))
        elif self._page >= page_num - half_num:  # 5 6 7 8 9 10 11 如果当前页码>=9
            return list(range(page_num - self._page_range_size + 1, page_num + 1))
        else:  # 页码在中间
            return list(range(self._page - half_num, self._page + half_num + 1)) \
                if self._page_range_size % 2 == 1 \
                else list(range(self._page - half_num + 1, self._page + half_num + 1))

# if __name__ == '__main__':
#     book_service = BookService()
#     paginator = Paginator(book_service, 10, 5)
#     for i in range(1, paginator.get_page_num() + 1):
#         paginator.page = i
#         print(paginator.get_page())
#         print(paginator.get_neighbor_page_list())
