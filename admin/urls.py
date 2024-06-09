from django.urls import path

from admin import views

urlpatterns = [
    path('', views.AdminIndexView.as_view(), name='admin_index'),

    path("user/", views.AdminUserView.as_view(), name='admin_user'),

    path("book/", views.AdminBookView.as_view(), name='admin_book'),
    path("book/add/", views.AdminBookAddView.as_view(), name='admin_book_add'),
    path("book/edit/<_id>/", views.AdminBookUpdateView.as_view(), name='admin_book_edit'),
    path("book/delete/<_id>/", views.AdminBookDeleteView.as_view(), name='admin-delete')
]
