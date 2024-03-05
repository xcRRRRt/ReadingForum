from datetime import datetime, date, time

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView

from user.service.userinfoservice import *


# Create your views here.

def userinfo(request):
    return render(request, 'user/userinfo.html')


def login(request):
    """登录"""
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        result = login_by_username_password(username, password)
        errors = {}
        if result == 1:
            errors['username_error'] = "未找到用户"
        elif result == 2:
            errors['password_error'] = "密码错误"

        if errors:
            print(errors)
            return JsonResponse(errors)
        else:
            print("correct")
            request.session['username'] = username
            return JsonResponse({'is_success': True})
    else:
        return render(request, 'user/login.html')


def register(request):
    """注册"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        errors = {}
        if not create_user(username=username, password=password):
            errors['username_error'] = "用户名已被使用"

        if errors:
            return JsonResponse(errors)
        else:
            request.session['username'] = username
            return JsonResponse({"is_success": True})
    else:
        return render(request, 'user/register.html')
