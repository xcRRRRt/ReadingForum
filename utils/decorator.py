# 装饰器

from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render


def login_required(func, login_template="user/login.html"):
    """
    登录验证

    :param func: 函数
    :param login_template: 登录页面
    """

    def wrapper(request: WSGIRequest, *args, **kwargs):
        if request.session.get("username", None) is None:
            return render(request, login_template)
        return func(request, *args, **kwargs)

    return wrapper
