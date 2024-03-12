from utils.dbconnect import get_db_handle

COLLECTION_NAME = "userinfo"


def find_userinfo(_filter: dict):
    """
    查询用户
    :param _filter: 过滤器，例：{'username': 'xxx', 'email': 'xxx'}
    :return 用户文档
    """
    db_handle = get_db_handle(COLLECTION_NAME)
    doc = db_handle.find_one(filter=_filter)
    return doc


def insert_one_userinfo(**kwargs) -> bool:
    """
    插入一条记录，支持嵌套文档和数组
    请以键值对的方式传参
    例：
        insert_one_user_info(username="test1111", password="123456", address={"test_address": "test address", "city": "Shanghai"})
        insert_one_user_info(username="test2222", password="123456", address=["shanghai", "beijing"])

    :param kwargs: 键值对数据，值支持数组和字典
    :return 是否插入成功
    """
    db_handle = get_db_handle(COLLECTION_NAME)
    result = db_handle.insert_one(kwargs)
    return result.acknowledged


def update_userinfo(_filter: dict, **kwargs) -> bool:
    """
    更新用户信息，以用户名或者邮箱作为查询条件
    :param _filter: 过滤器，例：{'username': 'xxx', 'email': 'xxx'}
    :param kwargs: 需要更新的数据
    :return 是否成功
    """
    db_handle = get_db_handle(COLLECTION_NAME)
    res = db_handle.update_one(filter=_filter, update={"$set": kwargs})
    return res.acknowledged


def delete_field(_filter: dict, fields: list) -> bool:
    """
    删除字段
    :param _filter: 过滤器
    :param fields: 要删除的字段名
    :return bool: 是否成功
    """
    db_handle = get_db_handle(COLLECTION_NAME)
    unset_fields = {field: 1 for field in fields}
    res = db_handle.update_one(filter=_filter, update={"$unset": unset_fields})
    return res.acknowledged
