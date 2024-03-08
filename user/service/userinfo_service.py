from django.contrib.auth.hashers import make_password, check_password

from user.dao.userinfo import *

COLLECTION_NAME = "userinfo"    # 集合


def create_user(username: str, password: str) -> bool:
    """
    创建一个新的用户
    :param username: 用户名
    :param password: 密码
    :return 是否创建成功
    """
    password = make_password(password)
    result = insert_one_user_info(username=username, password=password)
    return result


def is_user_exist(username: str) -> bool:
    """
    判断用户是否存在
    :param username: 用户名
    :return 用户是否存在
    """
    if find_user_by_username(username) is None:
        return False
    return True


def is_password_correct(username: str, password: str) -> bool:
    """
    判断密码是否正确
    :param username: 用户名
    :param password: 密码
    :return 密码是否正确
    """
    user = find_user_by_username(username)
    if check_password(user['password'], password):
        return False
    return True
