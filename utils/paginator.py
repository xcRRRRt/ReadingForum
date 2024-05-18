import math

from typing import *
from typing import Dict, Any


# 这可能是我写过的最棒的代码，值得和磊一起放在我的β里，靴靴
class Paginator:
    def __init__(self, collection_service=None,
                 required_fields: dict[str, str] = None,
                 can_sort: list[str] = None,
                 can_search: list[str] = None,
                 can_choose: list[str] = None,
                 per_page: int = 10,
                 page_range_size: int = 5):
        """
        自定义分页

        类似于 `Django Paginator <https://docs.djangoproject.com/zh-hans/5.0/ref/paginator/#django.core.paginator.Paginator>`_

        :param collection_service: service对象
        :param required_fields: 需要的字段
        :param per_page: 每页有多少个
        :param page_range_size: 显示在页面上的页码应该有多少个

        使用:
        ::::::::
        创建Paginator对象:\n
        >>> from book.service.book_service import BookService
        >>> from utils.paginator import Paginator
        >>> required_fields = {'isbn': "ISBN", 'title': "书名", 'label': "标签", 'price': "价格", 'stock': '库存', 'status': '状态'}  # 需要的字段
        >>> can_sort = ['isbn', 'title', 'price', 'stock']
        >>> book_service = BookService()
        >>> paginator = Paginator(book_service, required_fields, can_sort, per_page=10, page_range_size=5)

        设置当前页:\n
        >>> paginator.page = 7


        获取当前页、前一页、下一页:\n
        >>> paginator.page, paginator.previous, paginator.next
        (7, 6, 8)

        获取当前页的内容:\n
        >>> paginator.get_page()
        [{'_id': ObjectId('66000f102873ef7ac9095ff9'), 'isbn': '59', 'title': '图书59', 'price': 62.31},
        {'_id': ObjectId('66000f102873ef7ac9095ffa'), 'isbn': '60', 'title': '图书60', 'price': 27.05}, ...]

        可以根据指定的字段排序
        >>> paginator.sort_by = {"stock": 1}    # 按照stock升序
        >>> paginator.get_page()

        可以按照条件过滤
        >>> paginator.filter = {"stock": {"$gt": 70}}    # 选择stock>70的
        >>> paginator.get_page()

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
        self._map_fields = getattr(collection_service, 'map_fields', {})
        self._collection_name: str = collection_service.db.collection_name
        self._per_page: int = per_page
        self._page_range_size: int = page_range_size
        self._required_fields: dict[str, int] = {field: 1 for field in required_fields.keys()}
        self._required_fields_map: dict[str, str] = required_fields
        self._page: int = 1
        self._next: int | None = None
        self._previous: int | None = None
        _field_sort_state = {field: 0 for field in can_sort}
        _field_sort_state["_id"] = -1
        self._sort_by: dict[str, int] = _field_sort_state  # 默认倒序
        self._filter: dict = {}
        self._can_search: list[str] = can_search
        self._can_choose: list[str] = can_choose

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        """
        设置当前页
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

    @property
    def sort_by(self):
        return self._sort_by

    @sort_by.setter
    def sort_by(self, _sort: dict[str, int]):
        if "_id" not in _sort:
            _sort['_id'] = -1
        k, v = list(_sort.items())[0]
        del self._sort_by[k]
        _sort.update(self._sort_by)
        self._sort_by = _sort

    @property
    def filter(self):
        return self._filter

    @filter.setter
    def filter(self, _filter: dict):
        self._filter = _filter

    def get_page(self) -> list:
        """
        获取该页的内容列表
        :return: 改页的内容列表
        """
        skip = (self._page - 1) * self._per_page
        _sort_by_real = {k: v for k, v in self.sort_by.items() if v != 0}
        _sort_by_real = list(_sort_by_real.items())
        collection_find = getattr(self._collection_service, self._collection_name + "_find")
        objs = list(
            collection_find(
                self._filter,  # 查询条件
                self._required_fields  # 需求字段
            ).
            skip(skip).  # 跳过多少
            limit(self._per_page).  # 每页多少个条目
            sort(_sort_by_real)  # 排序，默认为按照id降序排序
        )
        return self._clean_data(objs)

    def _count_objs(self) -> int:
        """
        获取集合中的文档数量
        :return: 文档数量
        """
        count_documents = getattr(self._collection_service, self._collection_name + "_count_documents")
        return count_documents(self._filter)

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

    def ajax_page(self) -> dict:
        sort_by = self.sort_by.copy()
        del sort_by['_id']
        return {"objs": self.get_page(),
                "field": list(self._required_fields_map.keys()),
                "field_name": list(self._required_fields_map.values()),
                "can_sort_fields": list(sort_by.keys()),
                "can_search_fields": self._can_search,
                "can_choose_fields": self._can_choose,
                "sort_state": list(sort_by.values()),
                "total_pages": self.get_page_num(),
                "page_now": self.page,
                "page_prev": self.previous,
                "page_next": self.next,
                "neighbor_pages": self.get_neighbor_page_list()}

    def _clean_data(self, data):
        """
        清理数据，防止有对象
        :param data: 数据
        :return: 无对象数据
        """
        if isinstance(data, dict):
            cleaned_data = {}
            for key, value in data.items():
                if key == "_id":
                    cleaned_data["id"] = str(value)
                    continue
                if key in self._map_fields:
                    cleaned_data[key] = self._map_fields[key][value]
                    continue
                cleaned_data[key] = self._clean_data(value)
            return cleaned_data
        elif isinstance(data, list):
            cleaned_data = []
            for item in data:
                cleaned_data.append(self._clean_data(item))
                # 检查是否是最后一层列表
            if all(isinstance(item, (str, int, float)) for item in cleaned_data):
                return ','.join(str(item) for item in cleaned_data)
            else:
                return cleaned_data
        elif isinstance(data, (str, int, float, bool)):
            return data
        else:
            # 如果数据类型不是列表、字典、字符串或数字，则将其转换为字符串
            return str(data)


class PaginatorFromFunction:
    def __init__(self, func: Callable, per_page: int = 10):
        self.func = func
        self._per_page = per_page
        self._page = 1
        self._skip = (self._page - 1) * self._per_page
        self._sort_by = {}

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = value
        self._skip = (self._page - 1) * self._per_page

    @property
    def sort_by(self) -> dict[Any, Any]:
        return self._sort_by

    @sort_by.setter
    def sort_by(self, value: dict[Any, Any]):
        for k, v in value.items():
            if v != 0:
                self._sort_by[k] = v

    @property
    def per_page(self):
        return self._per_page

    @per_page.setter
    def per_page(self, value):
        self._per_page = value
        self._skip = (self._page - 1) * self._per_page

    def __call__(self, **kwargs):
        objs = self.func(**kwargs, skip=self._skip, sort_by=self.sort_by, limit=self._per_page)
        return self._clean_data(objs)

    def _clean_data(self, data):
        """
        清理数据，防止有对象
        :param data: 数据
        :return: 无对象数据
        """
        if isinstance(data, dict):
            cleaned_data = {}
            for key, value in data.items():
                if key == "_id":
                    cleaned_data["id"] = str(value)
                    continue
                cleaned_data[key] = self._clean_data(value)
            return cleaned_data
        elif isinstance(data, list):
            cleaned_data = []
            for item in data:
                cleaned_data.append(self._clean_data(item))
                # 检查是否是最后一层列表
            if all(isinstance(item, (str, int, float)) for item in cleaned_data):
                return ','.join(str(item) for item in cleaned_data)
            else:
                return cleaned_data
        elif isinstance(data, (str, int, float, bool)):
            return data
        else:
            # 如果数据类型不是列表、字典、字符串或数字，则将其转换为字符串
            return str(data)

# if __name__ == '__main__':
#     book_service = BookService()
#     paginator = Paginator(book_service, 10, 5)
#     for i in range(1, paginator.get_page_num() + 1):
#         paginator.page = i
#         print(paginator.get_page())
#         print(paginator.get_neighbor_page_list())
