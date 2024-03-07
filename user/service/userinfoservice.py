from user.dao.userinfo import *

COLLECTION_NAME = "userinfo"


def create_user(username: str, password: str) -> bool:
    """
    创建一个新的用户
    :param username: 用户名
    :param password: 密码
    :return 是否创建成功
    """
    result = insert_one_user_info(username=username, password=password)
    return result


def is_user_exist(username: str) -> bool:
    """
    判断用户是否存在
    :param username: 用户名
    :return 用户是否存在
    """
    if get_one_user_by_username(username) is None:
        return False
    return True


def is_password_correct(username: str, password: str) -> bool:
    """
    判断密码是否正确
    :param username: 用户名
    :param password: 密码
    :return 密码是否正确
    """
    user = get_one_user_by_username(username)
    if user['password'] != password:
        return False
    return True


