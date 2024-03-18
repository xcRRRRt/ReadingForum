from pymongo import MongoClient, errors as PyMongoErrors

DATABASE = 'readingforum'


class MongodbOperation:
    def __init__(self, database_name, collection_name):
        self.database_name = database_name
        self.collection_name = collection_name
        try:
            self.db_connection = MongoClient('localhost', 27017)[self.database_name]
        except PyMongoErrors.PyMongoError as e:
            print(f"在连接数据库{self.database_name}时遇到了问题: {e}")
        collection = self.db_connection[collection_name]
        self._map_collection_methods(collection_name, collection)

    def _map_collection_methods(self, collection_name, collection):
        for method_name in dir(collection):
            if callable(getattr(collection, method_name)) and not method_name.startswith('_'):
                setattr(self, f"{collection_name}_{method_name}",
                        self._create_collection_method(collection_name, method_name))

    def _create_collection_method(self, collection_name, method_name):
        def collection_method(*args, **kwargs):
            try:
                collection = self.db_connection[collection_name]
                method = getattr(collection, method_name)
                return method(*args, **kwargs)
            except PyMongoErrors.PyMongoError as e:
                print(f"在{method_name}_{collection_name}时出现了错误: {e}")

        return collection_method
