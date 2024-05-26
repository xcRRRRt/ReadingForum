from django import views
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from book.service.book_service import BookService
from forum.forms import PostForm
from forum.service.post_service import *
from user.service.userinfo_service import UserInfoService
from user.service.verification_service import VerificationService
from utils.datetime_util import get_datetime_by_objectId

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
        return render(request, "forum/editor.html", {"form": form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post_service.launch_post(content=form.cleaned_data.get("content"),
                                     title=form.cleaned_data.get("title"),
                                     labels=form.cleaned_data.get("labels"),
                                     author=request.session.get("username"),
                                     bound_book=form.cleaned_data.get("bound_book")
                                     )
            return JsonResponse({"success": True})
        print(form.errors)
        return JsonResponse({"errors": form.errors, "content_with_hint": form.cleaned_data.get("content")}, safe=False)


class PostDetailView(views.View):
    def get(self, request, post_id):
        # 获取需要的数据
        post = post_service.find_post_by_id(post_id, 'author', 'content', 'labels', 'title', '_id')
        author = post.get("author")
        avatar_url = userinfo_service.find_userinfo_by_username(
            author,
            'avatar_url'
        ).get('avatar_url')
        context = {
            "post": post,
            "post_author_avatar_url": avatar_url,
            "time": get_datetime_by_objectId(post.get("_id"))
        }
        post_likes_count = post_service.get_post_likes(post_id)  # 获取点赞数量
        user_post_like = post_service.have_user_liked_post(post_id, request.session.get("username"))  # 获取用户是否点赞过该帖子
        context = {**context, **post_likes_count, **user_post_like}
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
    books = book_service.find_book_by_isbn_or_title(query, 3, 'cover', 'title', 'isbn')
    return JsonResponse({"books": books})
