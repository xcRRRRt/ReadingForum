from django.urls import path
from user import views

urlpatterns = [
    path('', views.userinfo, name="userinfo"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.logout, name="logout"),
    path('verify/', views.verify, name='verify'),

    path('test_register/', views.register, name='test_register')
]
