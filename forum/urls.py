from django.urls import path
from forum import views

urlpatterns = [
    path('', views.homepage, name="home"),
    path('editor/', views.EditorView.as_view(), name="editor"),
    path("editor/search-book/", views.search_book, name="editor_search_book"),
    path("detail-post/<post_id>", views.PostDetailView.as_view(), name="detail_post"),

    path("search/", views.SearchResultView.as_view(), name='search'),

]
