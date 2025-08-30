from django.urls import path
from . import views

urlpatterns = [
    path('transcribe/', views.TranscribeVideoView.as_view(), name='transcribe-video'),
    path('analyze/', views.AnalyzeContentView.as_view(), name='analyze-content'),
]
