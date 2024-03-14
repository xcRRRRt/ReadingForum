from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from forum.forms import PostForm
from forum.service.post_service import *


# Create your views here.

def homepage(request):
    return render(request, "forum/home.html")


def editor(request):
    """发布帖子，进入ckeditor进行帖子编辑"""
    if request.method == "GET":
        form = PostForm()
        return render(request, "forum/editor.html", {"form": form})

    form = PostForm(request.POST)
    if form.is_valid():
        launch_post(content=form.cleaned_data.get("content"),
                    title=form.cleaned_data.get("title"),
                    labels=form.cleaned_data.get("labels"),
                    author=request.session.get("username"), )
        return redirect("/forum/")
    return render(request, "forum/editor.html", {"form": form})


# TODO 这是用于测试post详情的页面，用完后记得删咯
def test_post_detail(request):
    post = find_post_by_id("65f30fb98002a43ffc908078")
    return render(request, "forum/detail_post.html", {"post": post})
