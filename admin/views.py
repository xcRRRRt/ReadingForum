from django import views
from django.shortcuts import render

from utils.file_utils import save_file
from utils.view_decorator import AuthRequired


# Create your views here.

@AuthRequired.admin_required
class AdminIndexView(views.View):

    def get(self, request, *args, **kwargs):
        return render(request, 'admin_base.html')

    def post(self, request, *args, **kwargs):
        pass


@AuthRequired.admin_required
class AdminBookView(views.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'admin/admin_book.html')

    def post(self, request, *args, **kwargs):
        pass


class AdminBookAddView(views.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'admin/admin_book_add.html')

    def post(self, request, *args, **kwargs):
        cover = request.FILES.get("cover")
        book_data = request.POST
        url_path = save_file(cover, "book/cover", book_data.get("title"))
        print(url_path)
        # TODO 保存到数据库
        return render(request, "admin/admin_book.html")
