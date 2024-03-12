from django import forms
from django.core import validators

from user.service.userinfo_service import *
from user.service.verification_service import *


class BootStrapForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class LoginForm(BootStrapForm):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"id": "username"}),
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={"id": "password"}),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not is_user_exist(username):
            raise forms.ValidationError("未找到用户")
        return username

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if username and password:
            if not is_password_correct(username, password):
                raise forms.ValidationError("密码错误")
        return cleaned_data


class EmailForm(BootStrapForm):
    email = forms.EmailField(
        label="邮箱",
        validators=[validators.validate_email],
    )

    page = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        page = cleaned_data.get("page")
        if not page:
            cleaned_data.setdefault("page", "/user/reset_verify")
        if email and page:
            if "register" in page:  # 如果是注册页面的话
                if is_email_exist(email):
                    self.add_error("email", "邮箱已被使用")
            else:
                if not is_email_exist(email):
                    self.add_error("email", "邮箱不在数据库中，请确认使用了正确的邮箱")
        return cleaned_data


class VerifyForm(EmailForm):
    verification_code = forms.CharField(
        label="验证码",
        widget=forms.TextInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        email_address = cleaned_data.get("email")
        verification_code = cleaned_data.get("verification_code")
        if email_address and verification_code:
            if not verify_verification_code(email_address, verification_code):
                self.add_error("verification_code", "验证码错误")
        for key, field in self.fields.items():
            if key in cleaned_data and key not in ["password", "password_ensure"]:
                field.widget.attrs = {"class": "form-control is-valid"}
            else:
                field.widget.attrs = {"class": "form-control is-invalid"}
        return cleaned_data


class PasswordForm(BootStrapForm):
    password = forms.CharField(
        label="密码",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput()
    )
    password_ensure = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_ensure = cleaned_data.get("password_ensure")
        if password and password_ensure:
            if password != password_ensure:
                self.add_error("password_ensure", "两次密码不一致")
        for key, field in self.fields.items():
            if key in cleaned_data and key not in ["password", "password_ensure"]:
                field.widget.attrs = {"class": "form-control is-valid"}
            else:
                field.widget.attrs = {"class": "form-control is-invalid"}
        return cleaned_data


class RegisterForm(PasswordForm, VerifyForm):
    username = forms.CharField(
        label="用户名",
        min_length=5,
        max_length=20,
        widget=forms.TextInput(),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if is_user_exist(username):
            raise forms.ValidationError("用户名重复")
        return username

    def clean(self):
        cleaned_data = super().clean()
        for key, field in self.fields.items():
            if key in cleaned_data and key not in ["password", "password_ensure"]:
                field.widget.attrs = {"class": "form-control is-valid"}
            else:
                field.widget.attrs = {"class": "form-control is-invalid"}
        return cleaned_data


class AvatarUploadForm(forms.Form):
    avatar = forms.ImageField(
        label="选择头像",
        validators=[validators.validate_image_file_extension],
    )


class UserInfoForm(forms.Form):
    full_name = forms.CharField(
        required=False,
        label="全名",
        max_length=20
    )
    birthday = forms.DateField(
        required=False,
        label="生日",
        widget=forms.TextInput(attrs={'type': 'date'})
    )
    introduction = forms.CharField(
        required=False,
        label="个人简介",
        max_length=500,
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 20})
    )
