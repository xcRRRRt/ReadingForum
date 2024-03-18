# 创建数据库和集合，需要单独运行这个文件

from pymongo import MongoClient

if __name__ == "__main__":
    # 连接 MongoDB 数据库
    client = MongoClient(host="mongodb://localhost", port=27017)
    db = client['readingforum']

    # 验证码collection
    collection_name = 'verification'
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)
        # 为timestamp列创建降序索引，timestamp的时间离现在越近，被访问的概率越大（因为是验证码，离现在越近的时间被访问的概率越大）
        # 并设置过期时间
        res = collection.create_index([('timestamp', -1)], expireAfterSeconds=1800)
        print(f"{collection_name}的索引\n{res}")

    print()
    # 用户信息collection
    collection_name = "userinfo"
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)
        # 为username和email创建唯一索引
        res = collection.create_index([("username", 1), ("email", 1)], unique=True)
        print(f"{collection_name}的索引\n{res}")

    # Post帖子collection
    collection_name = "post"
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)

    print()
    # 书籍collection
    collection_name = "book"
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)

    print()
