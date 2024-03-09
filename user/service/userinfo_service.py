import os
import sys

import django
from django.contrib.auth.hashers import make_password, check_password

from user.dao.userinfo import *

COLLECTION_NAME = "userinfo"  # 集合


def create_user(username: str, password: str, email: str) -> bool:
    """
    创建一个新的用户
    :param username: 用户名
    :param password: 密码
    :param email: 邮箱
    :return 是否创建成功
    """
    password = make_password(password)
    result = insert_one_user_info(username=username, password=password, email=email)
    return result


def is_password_correct(username: str, password: str) -> bool:
    """
    判断密码是否正确
    :param username: 用户名
    :param password: 密码
    :return 密码是否正确
    """
    user = find_user_by_username(username)
    if check_password(password, user['password']):
        return True
    return False


def is_user_exist(username: str) -> bool:
    """
    判断用户是否存在
    :param username: 用户名
    :return 用户是否存在
    """
    if find_user_by_username(username) is None:
        return False
    return True


def is_email_exist(email: str) -> bool:
    """
    判断邮箱是否已存在
    :param email: email
    :return bool: 邮箱是否已存在
    """
    if find_user_by_email(email) is None:
        return False
    return True


def update_password(email: str, password: str):
    """
    更新密码
    :param email: 邮箱
    :param password: 新密码
    :return bool: 是否更新成功
    """
    if update_user(_email=email, password=make_password(password)):
        return True
    return False


def get_email(username: str) -> str:
    """
    获取邮箱
    :param username:
    :return 邮箱
    """
    return find_user_by_username(username)['email']

# if __name__ == '__main__':
#     # 如果要测试，请带上这几行
#     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     sys.path.append(base_dir)
#     # 将配置文件的路径写到django_settings_module环境变量中
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "readingforum.settings")
#     django.setup()
#
#     print(update_password("test@xx.com", "123456789"))
