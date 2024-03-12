import datetime

from django.contrib.auth.hashers import make_password, check_password

from user.dao.userinfo import *
from utils.datetime_util import get_datetime_by_objectId

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
    result = insert_one_userinfo(username=username, password=password, email=email)
    return result


def is_password_correct(username: str, password: str) -> bool:
    """
    判断密码是否正确
    :param username: 用户名
    :param password: 密码
    :return 密码是否正确
    """
    user = find_userinfo({"username": username})
    if check_password(password, user['password']):
        return True
    return False


def is_user_exist(username: str) -> bool:
    """
    判断用户是否存在
    :param username: 用户名
    :return 用户是否存在
    """
    if find_userinfo({"username": username}) is None:
        return False
    return True


def is_email_exist(email: str) -> bool:
    """
    判断邮箱是否已存在
    :param email: email
    :return bool: 邮箱是否已存在
    """
    if find_userinfo({"email": email}) is None:
        return False
    return True


def update_password(email: str, password: str):
    """
    更新密码
    :param email: 邮箱
    :param password: 新密码
    :return bool: 是否更新成功
    """
    if update_userinfo({"email": email}, password=make_password(password)):
        return True
    return False


def get_email(username: str) -> str:
    """
    获取邮箱
    :param username:
    :return 邮箱
    """
    return find_userinfo({"username": username})['email']


def get_register_time(username: str) -> str:
    """
    获取注册时间
    :param username: 用户名
    :return 注册时间
    """
    doc = find_userinfo({"username": username})
    _id = doc["_id"]  # 获取objectId
    return get_datetime_by_objectId(_id)


def update_avatar_url(username: str, avatar_url: str) -> bool:
    """
    更新用户头像
    :param username: 用户名
    :param avatar_url: 头像的url路径
    :return 是否更新成功
    """
    return update_userinfo({"username": username}, avatar_url=avatar_url)


def get_avatar_url(username: str) -> str:
    """
    获取用户头像的url路径
    :param username: 用户名
    :return 用户头像url路径
    """
    doc = find_userinfo({"username": username})
    return doc["avatar_url"]


def update_user_info(username: str, **kwargs) -> bool:
    """
    更新多个用户信息
    :param username: 用户名
    :param kwargs: 用户信息键值对
    :return 是否插入成功
    """
    to_save, to_delete = dict(), list()
    for key, value in kwargs.items():
        if value:
            if isinstance(value, datetime.date):
                value: datetime.date = datetime.datetime.combine(value, datetime.time())
            to_save[key] = value
        else:
            to_delete.append(key)
    res_update = update_userinfo({"username": username}, **to_save)
    res_delete = delete_field({"username": username}, to_delete)
    return res_update and res_delete


def get_userinfo_fields_values(username: str, fields: list) -> dict:
    """
    获取指定字段的值
    :param username: 用户名
    :param fields: 需要的字段
    """
    doc = find_userinfo({"username": username})
    data = {}
    for k, v in doc.items():
        if k in fields:
            if isinstance(v, datetime.datetime):
                v = v.date()
            data[k] = v
    return data


def get_addresses(username: str) -> list:
    return find_userinfo({"username": username})['addresses']

# if __name__ == '__main__':
#     # 如果要测试，请带上这几行
#     base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     sys.path.append(base_dir)
#     # 将配置文件的路径写到django_settings_module环境变量中
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "readingforum.settings")
#     django.setup()
#
#     print(get_register_time("testuser1"))
