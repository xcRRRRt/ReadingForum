from datetime import datetime, timezone

from utils.dbconnect import get_db_handle

COLLECTION_NAME = "verification"


def upsert_verification_code(email: str, verification_code: str) -> bool:
    """
    upsert一个验证码
    :param email: 邮箱
    :param verification_code: 验证码
    :return 是否成功
    """
    db_handler = get_db_handle(COLLECTION_NAME)
    res = db_handler.update_one(
        filter={"email": email},
        update={"$set": {
            "verification_code": verification_code,
            "timestamp": datetime.now(timezone.utc)
        }},
        upsert=True
    )
    return res.acknowledged


def find_verification_by_email(email: str):
    """
    使用email找到验证码
    :param email: 邮箱
    """
    db_handler = get_db_handle(COLLECTION_NAME)
    doc = db_handler.find_one({"email": email})
    return doc
