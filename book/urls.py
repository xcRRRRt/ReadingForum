from django.urls import path

from book import views

urlpatterns = [
    path("", views.BookHomeView.as_view(), name="book-home"),
    path("new/", views.BookNewListView.as_view(), name="book-new-list"),
    path("hot/", views.BookHotListView.as_view(), name="book-hot-list"),
    path("<str:book_id>/", views.BookDetailView.as_view(), name="book_detail"),
    path("comment/<str:book_id>/", views.book_comment, name="book_comment"),  # 发布评论
    path("<str:book_id>/comments/", views.CommentsListView.as_view(), name="book-comments"),  # 全部评论
    path("<str:book_id>/posts/", views.PostsListView.as_view(), name="book-posts")
]
