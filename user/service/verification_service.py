import random
from datetime import datetime, timezone

from django.core.mail import send_mail

from utils.db_operation import MongodbOperation


class VerificationService:
    def __init__(self):
        self.db = MongodbOperation('readingforum', 'verification')

    def send_verification_email(self, email: str) -> bool:
        """
        发送验证邮件
        :param email: 邮箱
        :return: 是否发送成功
        """
        verification_code = str(random.randint(100000, 999999))
        res = self.db.verification_update_one(
            filter={'email': email},
            update={'$set': {'verification_code': verification_code, 'timestamp': datetime.now(timezone.utc)}},
            upsert=True
        )
        if res.acknowledged and send_mail(subject="ReadingForum验证码测试",
                                          message="验证码" + verification_code,
                                          from_email="479250392@qq.com",
                                          recipient_list=[email]):
            return True
        return False

    def verify_verification_code(self, email: str, verification_code: str) -> bool:
        """
        验证验证码是否正确
        :param email: 邮箱
        :param verification_code: 用户输入的验证码
        :return: 验证码是否正确
        """
        verification = self.db.verification_find_one({'email': email})
        return verification_code == verification['verification_code']

    def delete_verification_code(self, email: str) -> bool:
        """
        删除验证码
        :param email: 邮箱
        :return: 是否成功
        """
        res = self.db.verification_delete_one({'email': email})
        return res.acknowledged
