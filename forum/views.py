from django import views
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from bs4 import BeautifulSoup

from book.service.book_service import BookService
from forum.forms import PostForm
from forum.service.post_service import *
from user.service.userinfo_service import UserInfoService
from user.service.verification_service import VerificationService
from utils.datetime_util import get_datetime_by_objectId
from utils.paginator import PaginatorFromFunction

# Create your views here.
userinfo_service = UserInfoService()
verification_service = VerificationService()
post_service = PostService()
book_service = BookService()


def homepage(request):
    return render(request, "forum/home.html")


class EditorView(views.View):
    def get(self, request):
        form = PostForm()
        bound_book = None
        if request.GET.get('bind'):
            bound_book_id = request.GET.get('bind')
            print(bound_book_id)
            bound_book = book_service.find_book_by_id(bound_book_id, 'title', 'isbn', 'cover')
            print(bound_book)
        return render(request, "forum/editor.html", {"form": form, "bound_book": bound_book})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post_service.launch_post(content=form.cleaned_data.get("content"),
                                     title=form.cleaned_data.get("title"),
                                     labels=form.cleaned_data.get("labels"),
                                     author=request.session.get("user_id"),
                                     bound_book=form.cleaned_data.get("bound_book")
                                     )
            return JsonResponse({"success": True})
        return JsonResponse({"errors": form.errors, "content_with_hint": form.cleaned_data.get("content")}, safe=False)


class PostDetailView(views.View):
    def get(self, request, post_id):
        # 获取需要的数据
        post = post_service.find_post_by_id(post_id, 'author', 'content', 'labels', 'title', '_id')
        author = post.get("author")
        userinfo = userinfo_service.find_userinfo_by_id(author, 'avatar_url', 'username')
        print(userinfo.get('username'))
        context = {
            "post": post,
            "post_author_avatar_url": userinfo.get('avatar_url'),
            "author": userinfo.get('username'),
            "time": get_datetime_by_objectId(post.get("_id"))
        }
        post_likes_count = post_service.get_post_likes(post_id)  # 获取点赞数量
        user_post_like = post_service.have_user_liked_post(post_id, request.session.get("username"))  # 获取用户是否点赞过该帖子
        context = {**context, **post_likes_count, **user_post_like}
        print(context)
        return render(request, "forum/detail_post.html", context=context)

    def post(self, request, post_id):
        def convert_to_boolean(value):
            return value.lower() == 'true'

        if "is_post_like" in request.POST:
            if request.POST.get("is_post_like"):
                post_service.update_post_likes(
                    post_id=post_id,
                    username=request.session.get("username"),
                    click_like=convert_to_boolean(request.POST.get("click_like")),
                    like_act=convert_to_boolean(request.POST.get("like_act")),
                    unlike_act=convert_to_boolean(request.POST.get("unlike_act"))
                )
            else:
                pass
        return HttpResponse()


def search_book(request):
    query = request.GET.get("q")
    books = book_service.find_book_by_isbn_or_title(query, 'cover', 'title', 'isbn', skip=0, limit=3)
    return JsonResponse({"books": books})


class SearchResultView(views.View):
    paginator_user = PaginatorFromFunction(userinfo_service.find_userinfos_by_username, per_page=12)
    paginator_book = PaginatorFromFunction(book_service.find_book_by_isbn_or_title, per_page=8)
    paginator_post = PaginatorFromFunction(post_service.text_search_posts, per_page=5)

    def get(self, request):
        query: str = request.GET.get("q")
        if query:
            queries = query.split(" ")
        else:
            return HttpResponse()

        show_part: str = request.GET.get("sp", "all")
        if show_part not in ['user', 'book', 'post', 'all']:
            show_part = 'all'

        if show_part == 'user':
            page = int(request.GET.get("page", self.paginator_user.page))
            limit = int(request.GET.get('limit', self.paginator_user.per_page))
            self.paginator_user.page = page
            self.paginator_user.per_page = limit
        elif show_part == 'book':
            page = int(request.GET.get("page", self.paginator_book.page))
            limit = int(request.GET.get('limit', self.paginator_book.per_page))
            self.paginator_book.page = page
            self.paginator_book.per_page = limit
        elif show_part == 'post':
            page = int(request.GET.get("page", self.paginator_post.page))
            limit = int(request.GET.get('limit', self.paginator_post.per_page))
            self.paginator_post.page = page
            self.paginator_post.per_page = limit
        elif show_part == 'all':
            self.paginator_user.page = 1
            self.paginator_book.page = 1
            self.paginator_post.page = 1
            self.paginator_user.per_page = 4
            self.paginator_book.per_page = 4
            self.paginator_post.per_page = 5

        users = self.paginator_user.from_function(username="".join(queries))
        users = list(filter(lambda user: user['username'] != request.session.get("username"), users))

        books = self.paginator_book.from_function(isbn_or_title="".join(queries))

        posts = self.paginator_post.from_function(query=" ".join(queries))
        for post in posts:
            author_obj_id = post.get("author")
            author_info = userinfo_service.find_userinfo_by_id(author_obj_id, 'username', 'avatar_url')
            post["author_name"] = author_info.get("username")
            post["author_avatar_url"] = author_info.get("avatar_url")
            post['post_time'] = get_datetime_by_objectId(post["id"])

        labels = set()
        for book in books:
            if 'label' in book:
                label = book.get("label").split(",")
                book["label"] = label
                labels.update(label)
        for post in posts:
            if 'labels' in post:
                label = post.get("labels", '').split(",")
                post["labels"] = label
                labels.update(label)
            # 找出content中的第一张图片
            content = post.get("content")
            soup = BeautifulSoup(content, "html.parser")
            post['brief_content'] = soup.get_text()
            first_img = soup.find("img")
            if first_img:
                src = first_img.get("src")
                if src:
                    post["first_img_src"] = src

        labels.discard('')

        print(len(users))
        print(len(books))
        print(len(posts))
        print(len(labels))

        return render(request, "forum/search_result.html",
                      {"users": users, "books": books, "posts": posts, "labels": labels, "query": query,
                       'show_part': show_part})

    def post(self, request):
        pass
