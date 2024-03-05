from user.dao.userinfo import *

COLLECTION_NAME = "userinfo"


def create_user(username: str, password: str) -> bool:
    """
    创建一个新的用户

    :param username: 用户名
    :param password: 密码
    :return 是否创建成功
    """
    user = get_one_user_by_username(username)
    if user:
        return False
    result = insert_one_user_info(username=username, password=password)
    return result


def login_by_username_password(username: str, password: str) -> int:
    """
    登录

    :param username: 用户名
    :param password: 密码
    :return 未找到用户1，密码错误2, 成功0
    """
    user = get_one_user_by_username(username)
    if not user:
        return 1
    if user['password'] != password:
        return 2
    return 0
