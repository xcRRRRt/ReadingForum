import datetime
from typing import Mapping, Any

from bson import ObjectId
from django.contrib.auth.hashers import make_password, check_password

from utils.datetime_util import get_datetime_by_objectId
from utils.db_operation import MongodbOperation

COLLECTION_NAME = "userinfo"  # 集合


class UserInfoService:
    def __init__(self):
        self.db = MongodbOperation('readingforum', 'userinfo')

    def create_user(self, username: str, password: str, email: str) -> bool:
        """
        创建一个新的用户
        :param username: 用户名
        :param password: 密码
        :param email: 邮箱
        :return: 是否创建成功
        """
        password = make_password(password)
        res = self.db.userinfo_insert_one(
            {'username': username, 'password': password, 'email': email}
        )
        return res.acknowledged

    def is_password_correct(self, username: str, password: str) -> bool:
        """
        判断密码是否正确
        :param username: 用户名
        :param password: 密码
        :return: 密码是否正确
        """
        userinfo = self.db.userinfo_find_one({'username': username})
        return check_password(password, userinfo['password'])

    def is_user_exist(self, username: str) -> bool:
        """
        判断用户是否存在
        :param username: 用户名
        :return: 用户是否存在
        """
        if self.db.userinfo_find_one({'username': username}) is None:
            return False
        return True

    def is_email_exist(self, email: str) -> bool:
        """
        判断邮箱是否已存在
        :param email: email
        :return: 邮箱是否已存在
        """
        if self.db.userinfo_find_one({"email": email}) is None:
            return False
        return True

    def update_password(self, email: str, password: str) -> bool:
        """
        更新密码
        :param email: 邮箱
        :param password: 新密码
        :return: 是否更新成功
        """
        res = self.db.userinfo_update_one({'email': email}, {'$set': {'password': make_password(password)}})
        return res.acknowledged

    def get_email(self, username: str) -> str:
        """
        获取邮箱
        :param username: 用户名
        :return: 邮箱
        """
        return self.db.userinfo_find_one({"username": username})['email']

    def get_register_time(self, username: str) -> str:
        """
        获取注册时间
        :param username: 用户名
        :return: 注册时间
        """
        userinfo = self.db.userinfo_find_one({'username': username})
        _id = userinfo["_id"]  # 获取objectId
        return get_datetime_by_objectId(_id)

    def update_avatar_url(self, username: str, avatar_url: str) -> bool:
        """
        更新用户头像
        :param username: 用户名
        :param avatar_url: 头像的url路径
        :return: 是否更新成功
        """
        res = self.db.userinfo_update_one({'username': username}, {'$set': {'avatar_url': avatar_url}})
        return res.acknowledged

    def update_user_info(self, username: str, **kwargs) -> bool:
        """
        更新多个用户信息
        :param username: 用户名
        :param kwargs: 用户信息键值对
        :return 是否插入成功
        """
        to_save, to_delete = dict(), dict()
        for key, value in kwargs.items():
            if value:
                if isinstance(value, datetime.date):
                    value: datetime.date = datetime.datetime.combine(value, datetime.time())
                to_save[key] = value
            else:
                to_delete[key] = 1
        res_update = self.db.userinfo_update_one({'username': username}, {'$set': to_save})
        res_delete = self.db.userinfo_update_one({'username': username}, {'$unset': to_delete})
        return res_update.acknowledged and res_delete.acknowledged

    def find_userinfo_by_username(self, username: str, *required_fields) -> Mapping[str, Any] | None:
        """
        获取指定字段的值
        :param username: 用户名
        :param required_fields: 需要的字段
        :return: 用户信息
        """
        projection = {field: 1 for field in required_fields}  # 创建投影，仅包含需要的字段
        userinfo = self.db.userinfo_find_one({'username': username}, projection=projection)
        for k, v in userinfo.items():
            if isinstance(v, datetime.datetime):
                userinfo[k] = v.date()
        return userinfo

    def add_post(self, username: str, post_id: ObjectId) -> bool:
        """
        用户发布帖子，存储帖子id
        :param username: 用户名
        :param post_id: 帖子Id
        :return: 是否存储成功
        """
        res = self.db.userinfo_update_one({'username': username}, {'$push': {'posts': post_id}})
        return res.acknowledged
