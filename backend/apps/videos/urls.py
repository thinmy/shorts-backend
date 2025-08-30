from django.urls import path
from . import views

urlpatterns = [
    path('', views.VideoListCreateView.as_view(), name='video-list-create'),
    path('<int:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
    path('<int:pk>/upload/', views.VideoUploadView.as_view(), name='video-upload'),
    path('youtube/download/', views.YouTubeDownloadView.as_view(), name='youtube-download'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('<int:pk>/processing-status/', views.VideoProcessingStatusView.as_view(), name='video-processing-status'),
]
