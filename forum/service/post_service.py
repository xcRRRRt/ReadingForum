from datetime import datetime
from typing import *
import pprint
from typing import Tuple
from copy import deepcopy

from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.command_cursor import CommandCursor

from book.service.book_service import BookService
from user.service.userinfo_service import UserInfoService
from utils.db_operation import MongodbOperation
from utils.paginator import PaginatorFromFunction
from utils.tokenize import Tokenizer
from utils.datetime_util import get_datetime_by_objectId

userinfo_service = UserInfoService()
book_service = BookService()


class PostService:
    def __init__(self):
        self.db = MongodbOperation('readingforum', 'post')

    def launch_post(self, content: str, title: str, author: str | ObjectId, labels: Optional[list[str]] = None,
                    bound_book: Optional[str | ObjectId] = None) -> Tuple[InsertOneResult, UpdateResult, UpdateResult]:
        """
        发布帖子后，将帖子数据插入post集合中，并将其_id插入到user集合中的posts中
        :param content: 帖子内容
        :param title: 帖子标题
        :param author: 作者
        :param labels: 帖子标签
        :param bound_book: 绑定的书籍
        :return: post集合插入结果，user_info集合posts push结果，book集合posts push结果
        """
        title_tokenized = Tokenizer.tokenize(title)
        content_tokenized = Tokenizer.tokenize(content)

        data = {
            "title": title,
            "title_tokenized": title_tokenized,
            "content": content,
            "content_tokenized": content_tokenized,
            "author": ObjectId(author),
            "bound_book": ObjectId(bound_book) if bound_book else None,
            "labels": labels if labels else None
        }
        # Remove keys with None values
        data = {k: v for k, v in data.items() if v is not None}
        insert_post_res = self.db.post_insert_one(data)
        update_user_res = userinfo_service.add_post(author, post_id=insert_post_res.inserted_id)
        update_book_res = book_service.push_post(bound_book, post_id=insert_post_res.inserted_id)
        return insert_post_res, update_user_res, update_book_res

    def find_post_by_id(self, post_id: str, *required_fields) -> dict[str, Any] | None:
        """
        使用_id寻找帖子指定字段的值
        :param post_id: ObjectId
        :param required_fields: 需要的字段
        :return: 帖子数据
        """
        projection = {field: 1 for field in required_fields}  # 创建投影，仅包含需要的字段
        return self.db.post_find_one({"_id": ObjectId(post_id)}, projection=projection)

    def update_post_likes(self, post_id: str, username: str,
                          click_like: bool, like_act: bool, unlike_act: bool):
        """
        赞/踩帖子，更新帖子的赞/踩，取消赞/踩
        状态：
        1. F F -> T F   纯点赞 push
        2. F F -> F T   纯点踩 push
        3. T F -> F T   赞→踩 set
        4. F T -> T F   踩→赞 set
        5. T F -> F F   取消赞 pull
        6. F T -> F F   取消踩 pull
        :param post_id: 帖子id
        :param username: 用户名
        :param click_like: 点击赞/踩，True赞，False踩
        :param like_act: 点击按钮之前，赞按钮的状态
        :param unlike_act: 点击按钮之前，踩按钮的状态
        :return: 更新是否成功
        """
        _filter, _update = None, None

        if not like_act and not unlike_act and click_like:
            _filter = {"_id": ObjectId(post_id)}
            _update = {"$push": {"likes": {"username": username, "like": True, "timestamp": str(datetime.now())}}}
        elif not like_act and not unlike_act and not click_like:
            _filter = {"_id": ObjectId(post_id)}
            _update = {"$push": {"likes": {"username": username, "like": False, "timestamp": str(datetime.now())}}}
        elif like_act and not unlike_act and not click_like:
            _filter = {"_id": ObjectId(post_id), "likes.username": username}
            _update = {"$set": {"likes.$.like": False, "likes.$.timestamp": str(datetime.now())}}
        elif not like_act and unlike_act and click_like:
            _filter = {"_id": ObjectId(post_id), "likes.username": username}
            _update = {"$set": {"likes.$.like": True, "likes.$.timestamp": str(datetime.now())}}
        elif like_act and not unlike_act and click_like:
            _filter = {"_id": ObjectId(post_id)}
            _update = {"$pull": {"likes": {"username": username}}}
        elif not like_act and unlike_act and not click_like:
            _filter = {"_id": ObjectId(post_id)}
            _update = {"$pull": {"likes": {"username": username}}}

        res = self.db.post_update_one(_filter, _update)
        return res.acknowledged

    def get_post_likes(self, post_id: str) -> dict[str, Any | None]:
        """
        获取帖子点赞/踩
        :param post_id:
        :return: 获取帖子赞和踩的数量
        """
        pipeline = [
            {"$match": {"_id": ObjectId(post_id)}},
            {"$unwind": "$likes"},
            {"$group": {"_id": "$likes.like", "count": {"$sum": 1}}}
        ]
        count = {}
        res = self.db.post_aggregate(pipeline)
        for doc in res:
            count[str(doc.get("_id")).lower()] = doc.get("count")

        return count

    def have_user_liked_post(self, post_id: str, username: str) -> dict[None | str, bool]:
        """
        判断用户是否点赞过帖子
        :param post_id:
        :param username:
        :return: 用户是否点赞过帖子，{}为没点赞/踩，{‘user_post_like',True}为点赞，{'user_post_unlike':True}为点踩
        """
        post = self.db.post_find_one(
            {"_id": ObjectId(post_id), "likes.username": username},
            {"likes.$": 1}
        )
        if post is None:
            return {}
        return {"user_post_like": True} if post.get("likes")[0].get("like") else {"user_post_unlike": True}

    def find_post_by_labels(self, labels: list[str], skip: int, limit: int, sort_by: dict[str, int] | None = None) -> List[Mapping[str, Any]]:
        """

        :param labels:
        :param skip:
        :param limit:
        :param sort_by:
        :return:
        """
        pipeline = [
            {"$match": {"labels": {"$in": labels}}},
            {
                "$addFields": {
                    "match_label_count": {
                        "$size": {
                            "$setIntersection": ["$labels", labels]
                        }
                    }
                }
            },
            {"$sort": {"match_label_count": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {"$project": {
                'title': 1,
                'content': 1,
                'author': 1,
                'labels': 1,
                'bound_book': 1,
                'match_label_count': 1
            }}
        ]
        posts = list(self.db.post_aggregate(pipeline))
        for post in posts:
            post["id"] = str(post["_id"])
            del post["_id"]
        return posts

    def text_search_posts(self, query: str, skip: int = 0, limit: int = 0, sort_by: dict[str, Any] = None) -> List[dict[str, Any]]:
        """

        :param query:
        :param skip:
        :param limit:
        :param sort_by:
        :return:
        """
        query = Tokenizer.tokenize(query)
        if sort_by is None:
            sort_by = {}
        sort_by.update({"score": {"$meta": "textScore"}})
        filter_ = {"$text": {"$search": query}}
        cursor = self.db.post_find(filter_, {"score": {"$meta": "textScore"}, "title_tokenized": 0,
                                             "content_tokenized": 0}).sort(sort_by)
        posts = list(cursor.skip(skip).limit(limit))
        for post in posts:
            post["id"] = str(post["_id"])
            del post["_id"]
        return posts

    def find_book_posts(self, book: dict[str, Any], skip: int, limit: int, sort_by: dict[str, Any]) -> List[dict[str, Any]]:
        """
        找到绑定book的帖子
        :param book:
        :param skip:
        :param limit:
        :param sort_by:
        :return:
        """
        if len(book.get("posts", [])) == 0:
            return []
        post_ids = book.get("posts")
        posts = []
        for post_id in post_ids:
            post = self.find_post_by_id(post_id, 'title', 'content', 'author', 'labels')
            author_id = post.get("author")
            author_info = userinfo_service.find_userinfo_by_id(author_id, 'avatar_url', 'username')
            post["author"] = author_info.get('username')
            post['avatar_url'] = author_info.get('avatar_url')
            post['time'] = get_datetime_by_objectId(post['_id'])
            posts.append(post)
        return posts

    def reply_to_post(self, post_id: str | ObjectId, user_id: str | ObjectId, content: str) -> tuple[UpdateResult, ObjectId]:
        """
        帖子回复
        :param post_id: 帖子ID
        :param user_id: 用户ID
        :param content: 回复内容
        :return:
        """
        doc = {"id": ObjectId(), "user_id": ObjectId(user_id), "content": content}
        res: UpdateResult = self.db.post_update_one({"_id": ObjectId(post_id)}, {"$push": {"reply": doc}})
        userinfo_service.add_reply(user_id, post_id, doc['id'])
        return res, doc['id']

    def reply_to_reply(self, post_id: str | ObjectId, user_id: str | ObjectId, content: str,
                       root_reply: str | ObjectId, reply_to: None | str | ObjectId = None) -> tuple[UpdateResult, ObjectId]:
        """
        回复的回复
        :param post_id: 帖子ID
        :param user_id: 用户ID
        :param content: 回复内容
        :param root_reply: 顶级回复ID
        :param reply_to: 回复本回复的顶级回复下的某条回复
        :return:
        """
        doc = {"id": ObjectId(), "user_id": ObjectId(user_id), "content": content}
        if reply_to:
            doc["reply_to"] = reply_to
        res: UpdateResult = self.db.post_update_one(
            {"_id": ObjectId(post_id), "reply.id": ObjectId(root_reply)},
            {"$push": {"reply.$.reply": doc}}
        )
        userinfo_service.add_reply(user_id, post_id, root_reply, doc['id'])
        return res, doc['id']

    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯
    # 准备发疯

    def find_replies(self, post_id: str | ObjectId, skip: int, limit: int, sort_by: dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """
        找顶级回复
        :param post_id: 帖子id
        :param skip:
        :param limit:
        :param sort_by:
        :return:
        """
        pipeline = [
            {"$match": {"_id": ObjectId(post_id)}},
            {"$project": {"reply": 1, "_id": 0}},
            {"$unwind": "$reply"},
            {"$sort": {"reply.id": -1}},
            {"$skip": skip},
            {"$limit": limit},
            {"$project": {"reply.id": 1, "reply.user_id": 1, "reply.content": 1}},
            {"$replaceRoot": {"newRoot": "$reply"}},
            {"$lookup": {"from": "userinfo", "localField": "user_id", "foreignField": "_id", "as": "user_info"}},
            {"$project": {"id": 1, "user_id": 1, "content": 1, "user_info.username": 1, "user_info.avatar_url": 1}},
            {
                "$replaceRoot": {
                    "newRoot": {
                        "$mergeObjects": [
                            {"$arrayElemAt": ["$user_info", 0]}, "$$ROOT"
                        ]
                    }
                }
            },
            {"$project": {"user_info": 0}},
            {"$addFields": {"reply_time": {"$toDate": "$id"}}}
        ]
        cursor = self.db.post_aggregate(pipeline)
        replies = list(cursor)
        return replies

    def find_replies_of_reply(self, post_id: str | ObjectId, root_reply: ObjectId | str, skip: int, limit: int,
                              sort_by: None | Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        找顶级回复下的回复
        :param post_id: 帖子ID
        :param root_reply: 顶级回复ID
        :param skip:
        :param limit:
        :param sort_by:
        :return:
        """
        pipeline = [
            {"$match": {"_id": ObjectId(post_id)}},
            {"$project": {"reply": 1, "_id": 0}},
            {"$unwind": "$reply"},
            {"$match": {"reply.id": ObjectId(root_reply)}},
            {"$replaceRoot": {"newRoot": "$reply"}},
            {"$project": {"reply": 1}},
            {"$unwind": "$reply"},
            {"$sort": {"reply.id": 1}},
            {"$skip": skip},
            {"$limit": limit},
            {"$replaceRoot": {"newRoot": "$reply"}},
            {"$lookup": {"from": "userinfo", "localField": "user_id", "foreignField": "_id", "as": "user_info"}},
            {"$project": {"id": 1, "user_id": 1, "content": 1, "reply_to": 1, "user_info.username": 1, "user_info.avatar_url": 1}},
            {
                "$replaceRoot": {
                    "newRoot": {
                        "$mergeObjects": [
                            {"$arrayElemAt": ["$user_info", 0]}, "$$ROOT"
                        ]
                    }
                }
            },
            {"$project": {"user_info": 0}},
            {"$addFields": {"reply_time": {"$toDate": "$id"}}}
        ]
        cursor = self.db.post_aggregate(pipeline)
        replies = list(cursor)
        for reply in replies:
            if "reply_to" in reply:
                reply["reply_to"] = self.find_one_reply(post_id, root_reply, reply['reply_to'])
        return replies

    def find_one_reply(self, post_id: str | ObjectId, root_reply_id: str | ObjectId, secondary_reply_id: str | ObjectId | None = None):
        """
        找回复
        :param post_id: 帖子ID
        :param root_reply_id: 顶级回复ID
        :param secondary_reply_id: 次级回复ID, 如果为空则在顶级评论找，否在在次级评论找
        :return:
        """
        pipeline = [
            {"$match": {"_id": ObjectId(post_id)}},
            {"$project": {"reply": 1, "_id": 0}},
            {"$unwind": "$reply"},
            {"$match": {"reply.id": ObjectId(root_reply_id)}},
            {"$replaceRoot": {"newRoot": "$reply"}},
        ]
        if not secondary_reply_id:
            pipeline += [
                {"$project": {"id": 1, "content": 1, "user_id": 1}}
            ]
        else:
            pipeline += [
                {"$project": {"reply": 1}},
                {"$unwind": "$reply"},
                {"$match": {"reply.id": ObjectId(secondary_reply_id)}},
                {"$replaceRoot": {"newRoot": "$reply"}}
            ]
        pipeline += [
            {"$lookup": {"from": "userinfo", "localField": "user_id", "foreignField": "_id", "as": "user_info"}},
            {"$project": {"id": 1, "user_id": 1, "content": 1, "reply_to": 1, "user_info.username": 1, "user_info.avatar_url": 1}},
            {
                "$replaceRoot": {
                    "newRoot": {
                        "$mergeObjects": [
                            {"$arrayElemAt": ["$user_info", 0]}, "$$ROOT"
                        ]
                    }
                }
            },
            {"$project": {"user_info": 0}},
            {"$addFields": {"reply_time": {"$toDate": "$id"}}}
        ]
        cursor: CommandCursor = self.db.post_aggregate(pipeline)
        reply = cursor.next()
        cursor.close()
        for k, v in reply.items():
            reply[k] = str(v)
        return reply

    def find_chain_reply(self, post_id: str | ObjectId, root_reply_id: str | ObjectId, secondary_reply_id: str | ObjectId | None = None,
                         depth: int | Literal["inf"] = 2, direction: Literal['both', 'back', 'forward'] = 'backward'):
        reply_root = self.find_one_reply(post_id, root_reply_id, secondary_reply_id)
        reply = reply_root
        for _ in range(depth - 1):
            if "reply_to" in reply:
                secondary_reply_id = reply["reply_to"]
                reply_ = self.find_one_reply(post_id, root_reply_id, secondary_reply_id)
                reply["reply_to"] = reply_
                reply = reply_
            else:
                break
        return reply_root

    def find_hottest_posts(self, skip: int, limit: int, sort_by=None):
        pipeline = [
            {
                '$project': {
                    'title': 1,
                    'content': 1,
                    'author': 1,
                    'labels': 1,
                    'bound_book': 1,
                    'reply_count': {'$size': {"$ifNull": ["$reply", []]}},
                    'reply_reply_counts': {
                        '$map': {
                            'input': '$reply',
                            'as': 'r',
                            'in': {'$size': {'$ifNull': ['$$r.reply', []]}}
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "total_reply_count": {
                        "$add": [{"$sum": "$reply_reply_counts"}, "$reply_count"]
                    }
                }
            },
            {
                "$sort": {"total_reply_count": -1}
            },
            {"$skip": skip},
            {"$limit": limit},
            {
                "$project": {
                    "total_reply_count": 1,
                    'title': 1,
                    'content': 1,
                    'author': 1,
                    'labels': 1,
                    'bound_book': 1
                }
            }
        ]

        posts = list(self.db.post_aggregate(pipeline))
        for post in posts:
            post["id"] = str(post["_id"])
            post['time'] = get_datetime_by_objectId(post['id'])
            del post["_id"]
        # pprint.PrettyPrinter().pprint(posts)
        return posts

    def find_new_posts(self, skip, limit, sort_by=None):
        sort_by = {"_id": -1}
        cursor = self.db.post_find({}, projection={'title': 1, 'content': 1, 'author': 1, 'labels': 1, 'bound_book': 1})
        if sort_by:
            cursor = cursor.sort(sort_by)
        posts = list(cursor.skip(skip).limit(limit))
        for post in posts:
            post["id"] = str(post["_id"])
            post['time'] = get_datetime_by_objectId(post['id'])
            del post["_id"]
        # pprint.PrettyPrinter().pprint(posts)
        return posts


if __name__ == '__main__':
    post_service = PostService()
    # print(post_service.have_user_liked_post("65f7e2bd9b0a0c39127c1cea", "testuser1"))
    # print(post_service.find_post_by_labels(['测试'], 0, 10, {}))
    # print(post_service.text_search_posts("丰乳肥臀", limit=5))
    # post_service.reply_to_post("665c3221447867a69e1d51dd", "65f7e03cf2d605e647ba0168", "测试回复2")
    # post_service.reply_to_reply("665c3221447867a69e1d51dd", "65f7e03cf2d605e647ba0168", "测试回复",
    #                             "6660a2fcd54779a40c26c0cd", "6660a300d54779a40c26d4ea")
    # post_service.find_replies("665c3221447867a69e1d51dd", 0, 10)
    # print(post_service.find_replies_of_reply("665c3221447867a69e1d51dd", "665ec1a1e39c0862b3056a4f", 0, 10))
    # print(post_service.find_one_reply("665c3221447867a69e1d51dd", "665ec1a1e39c0862b3056a4f"))

    # import random
    #
    # users = ['65f05515abc9fcbee905ecce', "65f450d87572e71eed946c80", "65f7d61550f37bf5756e2b06", "65f7e03cf2d605e647ba0168", "65f90c7a81ade435b8c616cd"]
    #
    # for i in range(100, 0, -1):
    #     post_id = "665c3221447867a69e1d51dd"
    #     post_service.reply_to_post(post_id, random.choice(users), "帖子回复" + str(i))
    #
    # post_id = "665c3221447867a69e1d51dd"
    # replies = post_service.find_replies(post_id, skip=0, limit=100)
    # num_replies = 100
    # for reply in replies:
    #     root_reply_id = reply["id"]
    #     for i in range(num_replies, 0, -1):
    #         post_service.reply_to_reply(post_id, random.choice(users), "回复的回复" + str(i), root_reply_id)
    #     num_replies -= 1

    # reply = post_service.find_chain_reply("665c3221447867a69e1d51dd", "6660a2fcd54779a40c26c0ce", "6660a5889d0d804a04f1ac69")
    # pprint.PrettyPrinter().pprint(reply)
    # post_service.find_hottest_posts(0, 4)
    # post_service.find_new_posts(0, 4)
    pprint.PrettyPrinter().pprint(post_service.find_post_by_labels(["测试", "帖子"], 0, 10))
