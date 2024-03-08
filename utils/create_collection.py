from pymongo import MongoClient

if __name__ == "__main__":
    # 连接 MongoDB 数据库
    client = MongoClient(host="mongodb://localhost", port=27017)
    db = client['readinigforum']

    # 创建集合（如果不存在）
    collection_name = 'verification'
    if collection_name not in db.list_collection_names():
        collection = db.create_collection(collection_name)
        collection.create_index('timestamp', expireAfterSeconds=1800)

    # 确认集合是否创建成功
    if collection_name in db.list_collection_names():
        print(f'Collection "{collection_name}" has been created successfully.')
    else:
        print(f'Failed to create collection "{collection_name}".')
