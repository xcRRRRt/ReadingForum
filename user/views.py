from django.shortcuts import render, redirect
from django.urls import reverse

from user.forms import LoginForm, RegisterForm
from user.service.userinfoservice import *
from utils.decorator import login_required


# Create your views here.

def userinfo(request):
    return render(request, 'user/userinfo.html')


def login(request):
    """登录"""
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'user/login.html', {'form': form})

    form = LoginForm(request.POST)
    if form.is_valid():
        request.session['username'] = form.cleaned_data['username']
        return render(request, "forum/home.html")
    return render(request, 'user/login.html', {'form': form})


def register(request):
    """注册"""
    if request.method == 'GET':
        form = RegisterForm()
        print(form)
        return render(request, 'user/register.html', {"form": form})

    form = RegisterForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        create_user(username, password)
        request.session['username'] = form.cleaned_data['username']
        return render(request, "forum/home.html")
    return render(request, "user/register.html", {"form": form})


@login_required
def logout(request):
    """注销"""
    request.session.clear()  # 删除session数据
    return redirect(reverse("home"))
