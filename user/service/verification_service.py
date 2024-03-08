import random

from django.core.mail import send_mail

from user.dao.verification import *


def send_verification_email(email: str) -> bool:
    """
    发送验证邮件
    :param email: 邮箱
    :return 发送成功
    """
    verification_code = str(random.randint(100000, 999999))
    is_success = upsert_verification_code(email, verification_code)
    if is_success and send_mail(subject="ReadingForum验证码测试",
                                message="验证码" + verification_code,
                                from_email="479250392@qq.com",
                                recipient_list=[email]):
        return True
    return False


def verify_verification_code(email: str, verification_code: str) -> bool:
    """
    验证验证码是否正确
    :param email: 邮箱
    :param verification_code: 用户输入的验证码
    :return 验证码是否正确
    """
    if verification_code != find_verification_by_email(email)["verification_code"]:
        return False
    return True
