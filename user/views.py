from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from user.forms import *
from user.service.userinfo_service import *
from user.service.verification_service import *
from utils.decorator import login_required


# Create your views here.

@login_required
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
        return render(request, 'forum/home.html')
    return render(request, 'user/login.html', {'form': form})


def register(request):
    """注册"""
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "user/register.html", {"form": form})

    form = RegisterForm(request.POST)
    if form.is_valid():
        # 验证成功，往集合里插入用户数据：用户名，密码，邮箱
        create_user(form.cleaned_data['username'], form.cleaned_data['password'], form.cleaned_data['email'])
        # 删除数据库存储的验证码
        delete_verification_code(form.cleaned_data['email'])
        # 设置session
        request.session['username'] = form.cleaned_data['username']
        return render(request, 'forum/home.html')
    return render(request, "user/register.html", {"form": form})


def verify(request):
    """
    获取邮箱验证码
    使用ajax将邮箱post到这里，见 user/static/js/register.js
    """
    email_address = request.POST.get("email")  # 邮箱地址
    email_form = EmailForm(data={'email': email_address, 'page': request.POST.get("page")})  # 以键值对的形式直接建立email表单
    if email_form.is_valid():
        email_address = email_form.cleaned_data['email']  # 验证
        send_verification_email(email_address)
        request.session['email'] = email_address
    return JsonResponse(data={"errors": email_form.errors})  # 直接把错误信息到ajax的success函数


@login_required
def logout(request: WSGIRequest):
    """注销"""
    request.session.clear()  # 删除session数据
    return render(request, "forum/home.html")


def reset_password_verify(request):
    """重置密码的验证"""
    if request.method == 'GET':
        form = VerifyForm()
        return render(request, "user/reset_password_verify.html", {"form": form})

    form = VerifyForm(request.POST)
    if form.is_valid():
        # 删除数据库存储的验证码
        delete_verification_code(form.cleaned_data['email'])
        return redirect(reverse("reset"))
    return render(request, "user/reset_password_verify.html", {"form": form})


def reset_password(request):
    """重置密码"""
    if request.method == 'GET':
        form = PasswordForm()
        return render(request, "user/reset_password.html", {"form": form})

    form = PasswordForm(request.POST)
    if form.is_valid():
        update_password(request.session.get("email"), form.cleaned_data.get("password"))
        request.session.clear()
        return redirect(reverse("login"))
    return render(request, "user/reset_password.html", {"form": form})


def profile(request):
    """编辑用户信息"""
    return render(request, 'user/userinfo_edit.html')
