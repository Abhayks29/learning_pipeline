from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('episodes/new/', views.episode_create, name='episode_create'),
    path('episodes/<int:pk>/', views.episode_detail, name='episode_detail'),
    path('episodes/<int:pk>/submit/', views.stage_submit, name='stage_submit'),
    path('team/<str:team>/', views.team_view, name='team_view'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/team/', views.edit_user_team, name='edit_user_team'),
]
