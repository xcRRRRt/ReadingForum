import random

from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.mail import send_mail

from user.dao.verification import upsert_verification_code
from user.forms import LoginForm, RegisterForm, EmailForm
from user.service.userinfo_service import *
from user.service.verification_service import send_verification_email
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
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "user/register.html", {"form": form})

    form = RegisterForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        create_user(username, password)
        request.session['username'] = username
        return render(request, "forum/home.html")
    return render(request, "user/register.html", {"form": form})


def verify(request):
    """
    获取邮箱验证码
    使用ajax将邮箱post到这里，见 user/static/js/register.js
    """
    email_address = request.POST.get("email")  # 邮箱地址
    email_form = EmailForm(data={'email': email_address})  # 以键值对的形式直接建立email表单
    if email_form.is_valid():
        email_address = email_form.cleaned_data['email']
        send_verification_email(email_address)  # 发送验证码
    print(email_form.errors)
    return JsonResponse(data={"errors": email_form.errors})  # 直接把错误信息到ajax的success函数


@login_required
def logout(request):
    """注销"""
    request.session.clear()  # 删除session数据
    return redirect(reverse("home"))
