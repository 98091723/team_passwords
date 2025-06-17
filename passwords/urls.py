from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_password, name='add_password'),
    path('<int:password_id>/', views.view_password, name='view_password'),
    path('<int:password_id>/edit/', views.edit_password, name='edit_password'),
    path('<int:password_id>/delete/', views.delete_password, name='delete_password'),
    path('generate/', views.generate_password, name='generate_password'),
]