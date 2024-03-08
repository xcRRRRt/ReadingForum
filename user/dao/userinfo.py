from utils.dbconnect import get_db_handle

COLLECTION_NAME = "userinfo"


def find_user_by_username(username):
    """
    使用唯一的用户名查询一个用户

    :param username: 用户名
    :return 用户文档
    """
    db_handle = get_db_handle(COLLECTION_NAME)
    doc = db_handle.find_one({"username": username})
    return doc


def insert_one_user_info(**kwargs) -> bool:
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
