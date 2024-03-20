from django.urls import path

from admin import views

urlpatterns = [
    path('', views.AdminIndexView.as_view(), name='admin_index'),
    path("book/", views.AdminBookView.as_view(), name='admin_book'),
    path("book/add/", views.AdminBookAddView.as_view(), name='admin_book_add'),
]
