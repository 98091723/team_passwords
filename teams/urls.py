from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('create/', views.create_team, name='create_team'),
    path('<int:team_id>/', views.team_detail, name='team_detail'),
    path('<int:team_id>/add-member/', views.add_member, name='add_member'),
    path('<int:team_id>/invite/', views.invite_member, name='invite_member'),
    path('invite/<str:code>/', views.accept_invite, name='accept_invite'),
]