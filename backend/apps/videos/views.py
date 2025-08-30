from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Video, VideoProcessingTask, YouTubeDownload, Tag
from .serializers import (
    VideoSerializer, VideoUploadSerializer, YouTubeDownloadSerializer,
    TagSerializer, VideoProcessingTaskSerializer
)
from .tasks import download_youtube_video, process_video


class VideoListCreateView(generics.ListCreateAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Video.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        video = serializer.save(user=self.request.user)
        # Start processing the video
        process_video.delay(video.id)


class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Video.objects.filter(user=self.request.user)


class VideoUploadView(generics.CreateAPIView):
    serializer_class = VideoUploadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        video = serializer.save(user=self.request.user)
        # Start processing the uploaded video
        process_video.delay(video.id)


class YouTubeDownloadView(generics.CreateAPIView):
    serializer_class = YouTubeDownloadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        download = serializer.save(user=self.request.user)
        # Start downloading the YouTube video
        download_youtube_video.delay(download.id)


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


class VideoProcessingStatusView(generics.RetrieveAPIView):
    serializer_class = VideoProcessingTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        video_id = self.kwargs['pk']
        video = get_object_or_404(Video, id=video_id, user=self.request.user)
        return video.processing_tasks.all()

    def retrieve(self, request, *args, **kwargs):
        video_id = self.kwargs['pk']
        video = get_object_or_404(Video, id=video_id, user=self.request.user)
        tasks = video.processing_tasks.all()
        
        serializer = VideoProcessingTaskSerializer(tasks, many=True)
        
        # Calculate overall progress
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status='completed').count()
        failed_tasks = tasks.filter(status='failed').count()
        
        progress = 0
        if total_tasks > 0:
            progress = (completed_tasks / total_tasks) * 100
        
        return Response({
            'video_id': video_id,
            'status': video.status,
            'progress': progress,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'tasks': serializer.data
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retry_processing(request, pk):
    """Retry processing a failed video"""
    video = get_object_or_404(Video, id=pk, user=request.user)
    
    if video.status != 'failed':
        return Response(
            {'error': 'Video is not in failed state'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Reset status and retry processing
    video.status = 'processing'
    video.save()
    
    # Clear failed tasks
    video.processing_tasks.filter(status='failed').delete()
    
    # Start processing again
    process_video.delay(video.id)
    
    return Response({'message': 'Video processing restarted'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_processing(request, pk):
    """Cancel video processing"""
    video = get_object_or_404(Video, id=pk, user=request.user)
    
    if video.status not in ['uploading', 'processing']:
        return Response(
            {'error': 'Cannot cancel processing for this video'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Mark as failed and cancel tasks
    video.status = 'failed'
    video.save()
    
    # Cancel pending tasks
    for task in video.processing_tasks.filter(status__in=['pending', 'processing']):
        if task.celery_task_id:
            # Cancel the Celery task
            from celery import current_app
            current_app.control.revoke(task.celery_task_id, terminate=True)
        
        task.status = 'cancelled'
        task.save()
    
    return Response({'message': 'Video processing cancelled'})
