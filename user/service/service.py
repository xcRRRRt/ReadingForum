from book.service.book_service import BookService
from forum.service.post_service import PostService
from forum.service.report_service import ReportService
from user.service.userinfo_service import UserInfoService

userinfo_service = UserInfoService()
post_service = PostService()
book_service = BookService()
report_service = ReportService()