from django.shortcuts import render
from django import views


# Create your views here.

class BookListView(views.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'book_list.html')

    def post(self, request, *args, **kwargs):
        pass


class BookDetailView(views.View):
    def get(self, request, book_id):
        pass

    def post(self, request, book_id):
        pass
