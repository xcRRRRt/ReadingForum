from django.urls import path
from forum import views

urlpatterns = [
    path('', views.homepage, name="home"),
    path('editor/', views.EditorView.as_view(), name="editor"),
    path("editor/search-book/", views.search_book, name="editor_search_book"),
    path("detail-post/<post_id>/", views.PostDetailView.as_view(), name="detail_post"),
    path("detail-post/<post_id>/reply/", views.ReplyView.as_view(), name="post_reply"),
    path("detail-post/<post_id>/reply/<root_reply_id>/", views.ReplyReplyView.as_view(), name="reply_reply"),

    path("search/", views.SearchResultView.as_view(), name='search'),
    path("search-labels/", views.LabelSearchResultView.as_view(), name='search_labels'),

    path("post/", views.PostListView.as_view(), name="post_list")

]
