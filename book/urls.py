from django.urls import path

from book import views

urlpatterns = [
    path("", views.BookListView.as_view(), name="book_list"),
    path("<str:book_id>/", views.BookDetailView.as_view(), name="book_detail"),
    path("comment/<str:book_id>/", views.book_comment, name="book_comment"),  # 发布评论
    path("<str:book_id>/comments/", views.Comments.as_view(), name="comments"),  # 全部评论
]
