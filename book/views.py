from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django import views

from book.service.book_service import BookService
from user.service.userinfo_service import UserInfoService
from utils.paginator import Paginator, PaginatorFromFunction

# Create your views here.

book_service = BookService()
userinfo_service = UserInfoService()


class BookListView(views.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'book/book_list.html')

    def post(self, request, *args, **kwargs):
        pass


class BookDetailView(views.View):
    """图书详情"""
    comments_num = 7
    comments_asc = False
    post_num = 5

    def get(self, request, book_id):
        book = book_service.find_book_by_id(book_id, 'isbn', 'title', 'cover', 'label', 'comments', 'introduction',
                                            'book_data', 'price', 'status', 'stock', map_fields=True)
        comments = []
        if book.get("comments"):
            _comments = book.get("comments") if self.comments_asc else list(reversed(book.get("comments")))
            for _comment in _comments[: self.comments_num]:
                user_id = _comment["user_id"]
                user = userinfo_service.find_userinfo_by_id(user_id, "username", "avatar_url")
                comment = {"username": user.get("username"), "avatar_url": user.get("avatar_url"), "user_id": user_id,
                           "comment": _comment.get("comment"), "time": _comment.get("time")}
                comments.append(comment)

        return render(request, 'book/book_detail.html', {"book": book, "comments": comments,
                                                         "test": "这部作品的悬疑成分没有之前读的几部作品那么浓烈，但是，留给读者回味的空间依然很足。本来，个人以为作者会在这个设定的基础上，通过身份的变与不变，来一场刺激的本格推理之旅。谜底揭晓时，不免有一丝惆怅，期待中的罪案，变成一系列琐碎但耐人寻味的小故事。其实，从书中的设定来看，这些小故事虽然违反规定，但有些很难上升到犯罪的角度。但正是这些灰色地带，却凸显了人类在面对问题时的种种弱点。"})

    def post(self, request, book_id):
        pass


def book_comment(request, book_id):
    """
    书本详情页评论
    """
    comment = request.POST.get('comment')
    # TODO 屏蔽词
    user_id = request.session.get('user_id')
    if book_service.push_comment(book_id, user_id, comment).acknowledged:
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


class Comments(views.View):
    """全部评论"""
    per_page = 10
    paginator = PaginatorFromFunction(book_service.find_book_comments, per_page=per_page)
    paginator.sort_by = {"time": -1}

    def get(self, request, book_id):
        """
        request接受参数: limit: int, page: int, time: int {-1, 1}
        """
        limit = int(request.GET.get('limit', self.paginator.per_page))
        page = int(request.GET.get('page', self.paginator.page))
        time_sort = int(request.GET.get('time', self.paginator.sort_by.get('time')))
        self.paginator.page = page
        self.paginator.per_page = limit
        self.paginator.sort_by = {"time": time_sort}
        comments = self.paginator.from_function(book_id=book_id)
        book = book_service.find_book_by_id(book_id, 'isbn', 'title', 'cover', 'label', 'price', 'book_data', 'label')
        return render(request, 'book/comments.html', {"book": book, "comments": comments, 'paginator': self.paginator})

    def post(self, request, book_id):
        pass
