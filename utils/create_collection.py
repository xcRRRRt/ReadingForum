# 创建数据库和集合，需要单独运行这个文件

# 要鼠了，百度搜了一下说MongoDB支持中文文本索引
# 支持个屁，你妈的官方文档里什么时候说了支持中文索引 https://www.mongodb.com/docs/manual/reference/text-search-languages/
# 天天抄来抄去的发，你妈鼠了

from pymongo import MongoClient, TEXT
from pymongo.operations import SearchIndexModel, IndexModel

if __name__ == "__main__":
    # 连接 MongoDB 数据库
    client = MongoClient(host="mongodb://localhost", port=27017)
    db = client['readingforum']

    # 验证码collection
    collection_name = 'verification'
    print(collection_name)
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)
        # 为timestamp列创建降序索引，timestamp的时间离现在越近，被访问的概率越大（因为是验证码，离现在越近的时间被访问的概率越大）
        # 并设置过期时间
        res = collection.create_index([('timestamp', -1)], expireAfterSeconds=1800)
        collection.find()
        print(collection.index_information())

    # 用户信息collection
    collection_name = "userinfo"
    print(collection_name)
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)
        # 为username和email创建唯一索引
        username_index = IndexModel("username", unique=True)
        email_index = IndexModel("email", unique=True)
        res = collection.create_indexes([username_index, email_index])
        print(collection.index_information())

    # Post帖子collection
    collection_name = "post"
    print(collection_name)
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)
        res = collection.create_index([('title_tokenized', 'text'), ('content_tokenized', 'text')])
        res_ = collection.create_index([('labels', 1)])
        print(collection.index_information())

    # 书籍collection
    collection_name = "book"
    print(collection_name)
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)
        res = collection.create_index([('label', 1)])
        print(collection.index_information())
