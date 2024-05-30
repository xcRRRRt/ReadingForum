import time
from datetime import datetime

from bson import ObjectId


def get_datetime_by_objectId(objectId: ObjectId | str) -> str:
    """
    通过objectId获取日期时间
    :param objectId: 文档的objectId
    :return 日期时间
    """
    timestamp = time.mktime(ObjectId(objectId).generation_time.timetuple())  # 获取时间戳
    # 转为日期
    datetime_object = datetime.fromtimestamp(timestamp)
    formatted_time = datetime_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time
