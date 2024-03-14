from typing import Optional

from forum.dao.post import *


def launch_post(content: str, title: str, author: str, labels: Optional[str] = None):
    """
    发布帖子后，将帖子数据插入数据库（发布日期从ObjectId中获取）
    :param content: 帖子内容
    :param title: 帖子标题
    :param author: 作者
    :param labels: 帖子标签
    :return 是否插入成功
    """
    # TODO 往用户的posts中增加这条post的记录
    return insert_post(content=content, title=title, labels=labels, author=author)


def find_post_by_id(post_id: str):
    return find_post({"_id": post_id})
