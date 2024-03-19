from django.urls import path

from admin import views

urlpatterns = [
    path('', views.AdminIndexView.as_view(), name='admin_index'),
    path("test/", views.test)
]
