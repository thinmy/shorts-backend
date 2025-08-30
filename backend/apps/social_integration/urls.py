from django.urls import path
from . import views

urlpatterns = [
    path('platforms/', views.SocialPlatformListView.as_view(), name='platform-list'),
    path('upload/', views.SocialMediaUploadView.as_view(), name='social-upload'),
    path('upload-status/<int:pk>/', views.UploadStatusView.as_view(), name='upload-status'),
]
