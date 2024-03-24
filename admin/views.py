from django import views
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render
from django.core import serializers

from book.service.book_service import BookService
from utils.file_utils import save_file
from utils.view_decorator import AuthRequired
from utils.paginator import Paginator

# Create your views here.
book_service = BookService()


@AuthRequired.admin_required
class AdminIndexView(views.View):

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_base.html')

    def post(self, request, *args, **kwargs):
        pass


@AuthRequired.admin_required
class AdminBookView(views.View):
    def get(self, request, *args, **kwargs):
        page = int(request.GET.get('page', 1))
        paginator = Paginator(book_service, 10, 5)
        paginator.page = page
        return render(request, 'admin/admin_book.html', {"paginator": paginator})

    def post(self, request, *args, **kwargs):
        pass


@AuthRequired.admin_required
def admin_book_list(request, *args, **kwargs):
    LIMIT = 10
    page = request.GET.get('page', 1)
    if page == "first":  # 第一页
        pass
    elif page == "last":  # 最后一页
        pass
    else:
        page = int(page)
    books = book_service.find_books(page, LIMIT, 'isbn', 'title', 'label', 'price')
    return JsonResponse({'books': books})


@AuthRequired.admin_required
class AdminBookAddView(views.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'admin/admin_book_add.html')

    def post(self, request: WSGIRequest, *args, **kwargs):
        cover = request.FILES.get("cover")  # 获取封面文件
        book_data = {}
        if cover:  # 处理封面文件
            url_path = save_file(cover, "book/cover", request.POST.get("title"))
            book_data['cover'] = url_path

        for k, v in request.POST.items():
            book_data[k] = v

        if 'label' in book_data:
            label: str = book_data['label']
            labels = list(set(filter(lambda string: len(string) > 0, label.strip().split(" "))))
            book_data['label'] = labels

        book_service.create_book(**book_data)
        return JsonResponse({})
