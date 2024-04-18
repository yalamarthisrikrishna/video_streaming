from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='home'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('create/', views.create_video, name='create_video'),
    path('<int:pk>/edit/', views.edit_video, name='edit_video'),
    path('<int:pk>/delete/', views.delete_video_confirm, name='delete_video'),
    path('<int:pk>/confirm_delete/', views.delete_video, name='confirm_delete_video'),
    path('all_videos/', views.all_videos, name='all_videos'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video_feed/<path:video_path>/', views.video_feed, name='video_feed'),
    path('permission_denied/', views.permission_denied, name='permission_denied'),
]