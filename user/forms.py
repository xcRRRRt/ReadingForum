from django import forms

from user.service.userinfoservice import *


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


class RegisterForm(BootStrapForm):
    username = forms.CharField(
        label="用户名",
        min_length=5,
        max_length=20,
        widget=forms.TextInput(attrs={"id": "username", "placeholder": "5-20位字符"})
    )
    password = forms.CharField(
        label="密码",
        min_length=8,
        max_length=20,
        widget=forms.PasswordInput(attrs={"id": "password"})
    )
    password_ensure = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(attrs={"id": "password_ensure"})
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if is_user_exist(username):
            raise forms.ValidationError("用户名重复")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_ensure = cleaned_data.get("password_ensure")
        if password and password_ensure:
            if password != password_ensure:
                raise forms.ValidationError("两次密码不一致")
        return cleaned_data
