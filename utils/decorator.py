# 装饰器

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect


def login_required(func, redirect_field_name='login', login_url='/user/login/'):
    """
    登录验证
    :param func: 函数
    :param redirect_field_name: 登录页面
    :param login_url: 登录页面
    """

    def wrapper(request: WSGIRequest, *args, **kwargs):
        if request.session.get("username", None) is None:
            return HttpResponseRedirect(login_url + '?next=' + request.get_full_path())
        return func(request, *args, **kwargs)

    return wrapper
