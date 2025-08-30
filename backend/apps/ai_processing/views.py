from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.videos.models import Video
from .services import TranscriptionService, ContentAnalysisService
from .tasks import transcribe_video_task, analyze_content_task


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_video(request):
    """Transcribe a video using AI services"""
    video_id = request.data.get('video_id')
    provider = request.data.get('provider', 'openai')
    
    if not video_id:
        return Response(
            {'error': 'video_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    video = get_object_or_404(Video, id=video_id, user=request.user)
    
    if video.status != 'ready':
        return Response(
            {'error': 'Video is not ready for transcription'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Start transcription task
    task = transcribe_video_task.delay(video.id, provider)
    
    return Response({
        'message': 'Transcription started',
        'task_id': task.id,
        'video_id': video.id,
        'provider': provider
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_content(request):
    """Analyze video content using AI"""
    video_id = request.data.get('video_id')
    provider = request.data.get('provider', 'openai')
    
    if not video_id:
        return Response(
            {'error': 'video_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    video = get_object_or_404(Video, id=video_id, user=request.user)
    
    if not video.transcription:
        return Response(
            {'error': 'Video must be transcribed first'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Start content analysis task
    task = analyze_content_task.delay(video.id, provider)
    
    return Response({
        'message': 'Content analysis started',
        'task_id': task.id,
        'video_id': video.id,
        'provider': provider
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ai_providers(request):
    """Get available AI providers"""
    providers = [
        {
            'name': 'openai',
            'display_name': 'OpenAI (Whisper)',
            'services': ['transcription', 'content_analysis'],
            'description': 'High-quality transcription and analysis'
        },
        {
            'name': 'groq',
            'display_name': 'Groq',
            'services': ['transcription'],
            'description': 'Fast transcription service'
        },
        {
            'name': 'gemini',
            'display_name': 'Google Gemini',
            'services': ['transcription', 'content_analysis'],
            'description': 'Google\'s multimodal AI'
        }
    ]
    
    return Response({'providers': providers})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_transcribe(request):
    """Transcribe multiple videos"""
    video_ids = request.data.get('video_ids', [])
    provider = request.data.get('provider', 'openai')
    
    if not video_ids:
        return Response(
            {'error': 'video_ids array is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    videos = Video.objects.filter(
        id__in=video_ids, 
        user=request.user, 
        status='ready'
    )
    
    if videos.count() != len(video_ids):
        return Response(
            {'error': 'Some videos not found or not ready'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    tasks = []
    for video in videos:
        task = transcribe_video_task.delay(video.id, provider)
        tasks.append({
            'video_id': video.id,
            'task_id': task.id
        })
    
    return Response({
        'message': f'Transcription started for {len(tasks)} videos',
        'tasks': tasks,
        'provider': provider
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transcription_status(request, video_id):
    """Get transcription status for a video"""
    video = get_object_or_404(Video, id=video_id, user=request.user)
    
    # Check if there's an active transcription task
    transcription_task = video.processing_tasks.filter(
        task_type='transcription'
    ).order_by('-created_at').first()
    
    if not transcription_task:
        return Response({
            'video_id': video_id,
            'has_transcription': bool(video.transcription),
            'transcription': video.transcription,
            'status': 'not_started'
        })
    
    return Response({
        'video_id': video_id,
        'has_transcription': bool(video.transcription),
        'transcription': video.transcription,
        'status': transcription_task.status,
        'task_id': transcription_task.celery_task_id,
        'error_message': transcription_task.error_message,
        'started_at': transcription_task.started_at,
        'completed_at': transcription_task.completed_at
    })
