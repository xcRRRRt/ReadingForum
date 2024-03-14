import os.path

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from readingforum.settings import MEDIA_ROOT, MEDIA_URL
from user.forms import *
from user.service.userinfo_service import *
from user.service.verification_service import *
from utils.decorator import login_required


# Create your views here.

def login(request):
    """登录"""
    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'user/login.html', {'form': form})

    form = LoginForm(request.POST)
    if form.is_valid():
        request.session['username'] = form.cleaned_data['username']
        request.session['avatar_url'] = get_avatar_url(form.cleaned_data['username'])
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


@login_required
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


@login_required
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


@login_required
def userinfo(request):
    """用户个人中心"""
    email = get_email(request.session['username'])
    register_time = get_register_time(request.session['username'])
    data = {"email": email, "register_time": register_time}
    return render(request, 'user/userinfo.html', data)


@login_required
def profile(request):
    """编辑用户信息，GET方法，下面的两个函数都是用来验证的，都是POST"""
    edit_avatar_form = AvatarUploadForm()  # 上传头像表单

    userinfo_form = UserInfoForm()  # 用户信息表单
    fields_name = list(userinfo_form.fields.keys())  # 获取表单字段名
    # 设置表单初始值
    userinfo_form.initial = get_userinfo_fields_values(request.session.get("username"), fields=fields_name)
    addresses = get_addresses(request.session.get("username"))
    return render(request, 'user/userinfo_edit.html',
                  {"edit_avatar_form": edit_avatar_form, "userinfo_form": userinfo_form, "addresses": addresses})


@login_required
def edit_avatar(request):
    """编辑头像"""
    form = AvatarUploadForm(request.POST, request.FILES)
    if form.is_valid():
        avatar = form.cleaned_data['avatar']
        ext = os.path.splitext(avatar.name)[-1]  # 文件扩展名

        save_dir = "%s/userinfo/avatar" % MEDIA_ROOT  # 保存的目录的相对路径
        # 如果目录不存在，创建
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        relative_path = "userinfo/avatar/%s" % (request.session.get("username") + ext)  # 相对路径
        save_path = os.path.join(MEDIA_ROOT, relative_path)  # 保存到本地的绝对路径
        url_path = str(os.path.join(MEDIA_URL, relative_path))  # 保存到数据库的url路径

        # 保存
        with open(save_path, 'wb') as f:
            # pic.chunks()为图片的一系列数据，它是一一段段的，所以要用for逐个读取
            for content in avatar.chunks():
                f.write(content)
        update_avatar_url(request.session.get("username"), url_path)  # 保存url路径

        # 设置session
        request.session['avatar_url'] = get_avatar_url(request.session.get("username"))

    # userinfo表单
    userinfo_form = UserInfoForm()
    fields_name = list(userinfo_form.fields.keys())
    userinfo_form = UserInfoForm(
        initial=get_userinfo_fields_values(request.session.get("username"), fields=fields_name))

    # 地址
    addresses = get_addresses(request.session.get("username"))
    return render(request, "user/userinfo_edit.html",
                  {"edit_avatar_form": form, "userinfo_form": userinfo_form, "addresses": addresses})


@login_required
def edit_userinfo(request):
    """编辑用户信息"""
    data = request.POST
    form = UserInfoForm(data)
    if form.is_valid():
        update_user_info(request.session.get("username"), **form.cleaned_data)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "errors": form.errors})


@login_required
def save_addresses(request):
    """保存地址"""
    addresses = request.POST.getlist("addresses[]")
    if update_user_info(request.session.get("username"), addresses=addresses):
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})
