from django import views
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from book.service.book_service import BookService
from user.service.userinfo_service import UserInfoService
from utils.file_utils import save_file
from utils.paginator import Paginator
from utils.view_decorator import AuthRequired

# Create your views here.
book_service = BookService()
user_service = UserInfoService()


@AuthRequired.admin_required
class AdminIndexView(views.View):

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_base.html')

    def post(self, request, *args, **kwargs):
        pass


@AuthRequired.admin_required
class AdminUserView(views.View):
    """
    管理员用户列表
    """
    per_page = 10
    page_range_size = 5
    required_fields = {"username": "用户名", "email": "邮箱", "admin": "管理员"}
    can_sort = ["username"]
    paginator = Paginator(user_service, required_fields, can_sort=can_sort, per_page=per_page,
                          page_range_size=page_range_size)

    def get(self, request, *args, **kwargs):
        page = int(request.GET.get('page', 1))
        self.paginator.page = page
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # 如果是ajax
            print("ajax")
            # 搜索
            to_search = request.GET.get('to_search')
            print(to_search)
            if to_search:  # 设置过滤器
                ...
                # self.paginator.filter.update({
                #     "$or": [
                #         {"isbn": {"$regex": to_search}},
                #         {"title": {"$regex": to_search}},
                #     ]
                # })
            elif to_search == "":  # 清除过滤器(手动清空输入框)
                self.paginator.filter = {}

            # 排序字段、下一个排序依据（升序/降序/默认）
            to_sort_field, next_sort_state = request.GET.get('field'), request.GET.get('next_state')
            if to_sort_field and next_sort_state is not None:
                self.paginator.sort_by = {to_sort_field: int(next_sort_state)}

            return JsonResponse(self.paginator.ajax_page())

        # 不是ajax则刷新Paginator状态
        print("not ajax")
        self.paginator = Paginator(book_service, self.required_fields, self.can_sort, per_page=self.per_page,
                                   page_range_size=self.page_range_size)
        return render(request, 'admin/admin_list.html')

    def post(self, request, *args, **kwargs):
        pass


@AuthRequired.admin_required
class AdminBookView(views.View):
    """
    管理员书籍列表
    """
    per_page = 10  # 每页文档条数
    page_range_size = 5  # 页码范围
    required_fields = {'isbn': "ISBN", 'title': "书名", 'label': "标签"}  # 需要的字段
    can_sort = ['isbn', 'title']  # 可以排序的字段
    can_search = ['isbn', 'title']  # 可以被搜索的字段
    can_choose = ['status']  # 可以被选择的字段
    paginator = Paginator(book_service, required_fields, can_sort, can_search, can_choose, per_page, page_range_size)

    def get(self, request, *args, **kwargs):
        """
        request接受参数: page:int, to_search:str, field: str, next_state:int
        """
        # 修改页码
        page = int(request.GET.get('page', 1))
        self.paginator.page = page
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # 如果是ajax
            print("ajax")
            # 搜索
            to_search = request.GET.get('to_search')
            print(to_search)
            if to_search:  # 设置过滤器
                self.paginator.filter.update({
                    "$or": [
                        {"isbn": {"$regex": to_search}},
                        {"title": {"$regex": to_search}},
                    ]
                })
            elif to_search == "":  # 清除过滤器(手动清空输入框)
                self.paginator.filter = {}

            # 排序字段、下一个排序依据（升序/降序/默认）
            to_sort_field, next_sort_state = request.GET.get('field'), request.GET.get('next_state')
            if to_sort_field and next_sort_state is not None:
                self.paginator.sort_by = {to_sort_field: int(next_sort_state)}

            return JsonResponse(self.paginator.ajax_page())

        # 不是ajax则刷新Paginator状态
        print("not ajax")
        self.paginator = Paginator(book_service, self.required_fields, self.can_sort, self.can_search, self.can_choose,
                                   self.per_page, self.page_range_size)
        return render(request, 'admin/admin_list.html')

    def post(self, request, *args, **kwargs):
        pass


@AuthRequired.admin_required
class AdminBookAddView(views.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'admin/admin_book_edit.html')

    def post(self, request: WSGIRequest, *args, **kwargs):
        cover = request.FILES.get("cover")  # 获取封面文件

        title = request.POST.get("title")
        isbn = request.POST.get("isbn")
        # price = float(request.POST.get("price"))
        # stock = int(request.POST.get("stock"))
        label = request.POST.get("label")
        # status = int(request.POST.get("status"))
        introduction = request.POST.get("introduction")

        labels = None

        if label:
            labels = list(set(filter(lambda string: len(string) > 0, label.strip().split(" "))))

        # if stock == 0:
        #     status = 2

        book_data = {}
        for k, v in request.POST.items():
            if k not in ["title", "isbn", "price", "stock", "status", "cover", "introduction", "label"]:
                book_data[k] = v

        success, insert_id = book_service.create_book(title=title, isbn=isbn,
                                                      # price=price, stock=stock, status=status,
                                                      label=labels, introduction=introduction, book_data=book_data)

        if cover:  # 处理封面文件
            cover_url = save_file(cover, "book/cover", str(insert_id))
            book_service.update_book_by_id(insert_id, cover=cover_url)
        return JsonResponse({})


@AuthRequired.admin_required
class AdminBookUpdateView(views.View):
    def get(self, request, _id):
        book = dict(book_service.find_book_by_id(_id))
        book['id'] = str(book['_id'])
        return render(request, "admin/admin_book_edit.html", {"book": book})

    def post(self, request, _id):
        cover = request.FILES.get("cover")  # 获取封面文件

        title = request.POST.get("title")
        isbn = request.POST.get("isbn")
        # price = float(request.POST.get("price"))
        # stock = int(request.POST.get("stock"))
        label = request.POST.get("label")
        # status = int(request.POST.get("status"))
        introduction = request.POST.get("introduction")

        labels = None
        cover_url = None

        if label:
            labels = list(set(filter(lambda string: len(string) > 0, label.strip().split(" "))))

        # if stock == 0:
        #     status = 2

        book_data = {}
        for k, v in request.POST.items():
            if k not in ["title", "isbn", "price", "stock", "status", "cover", "introduction", "label"]:
                book_data[k] = v

        if cover:
            cover_url = save_file(cover, "book/cover", _id)

        book_service.update_book_by_id(_id, title=title, isbn=isbn, cover_url=cover_url, label=labels,
                                       # price=price, stock=stock, status=status,
                                       introduction=introduction, book_data=book_data)

        return render(request, "admin/admin_list.html")


@AuthRequired.admin_required()
class AdminBookDeleteView(View):
    def get(self, request, _id):
        print(_id)
        if book_service.delete_book(_id).acknowledged:
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "fail"})

    def post(self, request, _id):
        pass
