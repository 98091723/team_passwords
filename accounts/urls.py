from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('setup/', views.setup_super_admin, name='setup_super_admin'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_user, name='register'),
    path('users/', views.user_list, name='user_list'),
]