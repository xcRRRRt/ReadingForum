import pprint
from typing import *

from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from utils.db_operation import MongodbOperation
from forum.service.post_service import PostService
from book.service.book_service import BookService
from user.service.userinfo_service import UserInfoService

post_service = PostService()
book_service = BookService()
user_service = UserInfoService()


class ReportService:
    """
    字段有_id, report_type, report_path, feedback, is_reviewed, report_user
    report_type: 1是帖子，2是根回复，3是子回复，4是短评
    """

    def __init__(self):
        self.db = MongodbOperation("readingforum", 'report')
        self.report_type_map = {1: "post", 2: "reply", 3: "reply_of_reply", 4: "comment"}

    def add_report(self, report_type: int | str, report_path: List[str | ObjectId], reporter: str | ObjectId, content: str) -> InsertOneResult:
        report_type = int(report_type)
        report_path = list(map(lambda x: ObjectId(x), report_path))
        doc = {
            "report_type": report_type,
            "report_path": report_path,
            "reporter": ObjectId(reporter),
            "is_reviewed": False,
            "content": content
        }
        res = self.db.report_insert_one(doc)
        return res

    def find_unreviewed_posts(self, skip: int, limit: int, sort_by=None) -> List[Dict[str, Any]]:
        filter_ = {
            "is_reviewed": False,
            "report_type": 1
        }
        if not sort_by:
            sort_by = {"_id": -1}
        cursor = self.db.report_find(filter_).sort(sort_by).skip(skip).limit(limit)
        reports = list(cursor)
        for report in reports:
            post_id = report["report_path"][0]
            post = post_service.find_post_by_id(post_id, "author", "title", all_=True)
            post_author_id = post["author"]
            author = user_service.find_userinfo_by_id(post_author_id, "username")
            reporter_id = report.get("reporter")
            reporter = user_service.find_userinfo_by_id(reporter_id, "username")
            report['author'] = author.get("username")
            report['reporter'] = reporter.get("username")
            report['post_id'] = post_id
            report["title"] = post["title"]
            report["id"] = str(report.get("_id"))
        return reports

    def find_unreviewed_replies(self, skip: int, limit: int, sort_by=None) -> List[Dict[str, Any]]:
        filter_ = {
            "is_reviewed": False,
            "report_type": {"$in": [2, 3]}
        }
        if not sort_by:
            sort_by = {"_id": -1}
        cursor = self.db.report_find(filter_).sort(sort_by).skip(skip).limit(limit)
        reports = list(cursor)
        for report in reports:
            report_path = report["report_path"]
            reply = None
            if len(report_path) == 2:
                post_id = report_path[0]
                root_reply_id = report_path[1]
                reply = post_service.find_one_reply(post_id, root_reply_id)
            elif len(report_path) == 3:
                post_id = report_path[0]
                root_reply_id = report_path[1]
                secondary_reply_id = report_path[2]
                reply = post_service.find_chain_reply(post_id, root_reply_id, secondary_reply_id)
            report["reply"] = reply
            report['post_id'] = report_path[0]
            reporter = user_service.find_userinfo_by_id(report.get("reporter"), "username")
            report["reporter"] = reporter
        return reports

    def find_unreviewed_comments(self, skip: int, limit: int, sort_by=None) -> List[Dict[str, Any]]:
        filter_ = {
            "is_reviewed": False,
            "report_type": 4
        }
        if not sort_by:
            sort_by = {"_id": -1}
        cursor = self.db.report_find(filter_).sort(sort_by).skip(skip).limit(limit)
        reports = list(cursor)
        for report in reports:
            book_id = report["report_path"][0]
            comment_id = report["report_path"][1]
            comment = book_service.find_book_comment(book_id, comment_id)
            report["comment"] = comment
            report["id"] = str(report["_id"])
            reporter = user_service.find_userinfo_by_id(report.get("reporter"), "username", "avatar_url")
            report["reporter"] = reporter.get("username")
            report['book_id'] = book_id
        return reports

    def count_type(self):
        pipeline = [
            {"$match": {"is_reviewed": False}},
            {
                "$group": {
                    "_id": "$report_type",
                    "count": {"$sum": 1}
                }
            }
        ]
        res = list(self.db.report_aggregate(pipeline))
        result = {}
        for group in res:
            result[self.report_type_map.get(group["_id"])] = group["count"]
        print(result)
        return result

    def set_reviewed(self, report_id: str | ObjectId, operation: Literal["agree", "cancel"] = "agree") -> UpdateResult | None:
        operation = operation.lower()
        res = self.db.report_update_one({"_id": ObjectId(report_id)}, {"$set": {"is_reviewed": True}})
        if operation == "cancel":
            return None
        report = self.db.report_find_one({"_id": ObjectId(report_id)})
        report_type = report.get("report_type")
        report_path = report.get("report_path")
        if report_type == 1:
            post_service.update_post_block_status(*report_path, status=True)
        elif report_type == 2:
            post_service.update_reply_block_status(*report_path, status=True)
        elif report_type == 3:
            post_service.update_reply_reply_block_status(*report_path, status=True)
        elif report_type == 4:
            book_service.update_comment_block_status(*report_path, status=True)
        else:
            raise Exception("跳出三界之外，不在五行之中")
        return res


if __name__ == "__main__":
    report_service = ReportService()
    # report_service.find_unreviewed_replies(0, 10)
    # report_service.count_type()
    report_service.set_reviewed("66666d753c7ee8c30ec90fe8")
