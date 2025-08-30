from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SocialPlatform, SocialMediaUpload, PlatformAnalytics
from .serializers import (
    SocialPlatformSerializer, SocialMediaUploadSerializer, 
    PlatformAnalyticsSerializer
)
from .tasks import upload_to_social_platform


class SocialPlatformListView(generics.ListAPIView):
    queryset = SocialPlatform.objects.filter(is_active=True)
    serializer_class = SocialPlatformSerializer
    permission_classes = [IsAuthenticated]


class SocialMediaUploadView(generics.CreateAPIView):
    serializer_class = SocialMediaUploadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        upload = serializer.save(user=self.request.user)
        # Start the upload process
        upload_to_social_platform.delay(upload.id)


class UploadStatusView(generics.RetrieveAPIView):
    serializer_class = SocialMediaUploadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SocialMediaUpload.objects.filter(user=self.request.user)


class UserUploadsView(generics.ListAPIView):
    serializer_class = SocialMediaUploadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SocialMediaUpload.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retry_upload(request, pk):
    """Retry a failed social media upload"""
    upload = get_object_or_404(SocialMediaUpload, id=pk, user=request.user)
    
    if upload.status != 'failed':
        return Response(
            {'error': 'Upload is not in failed state'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Reset status and retry
    upload.status = 'pending'
    upload.error_message = ''
    upload.save()
    
    # Start upload process again
    upload_to_social_platform.delay(upload.id)
    
    return Response({'message': 'Upload restarted'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_upload(request, pk):
    """Cancel a pending social media upload"""
    upload = get_object_or_404(SocialMediaUpload, id=pk, user=request.user)
    
    if upload.status not in ['pending', 'uploading']:
        return Response(
            {'error': 'Cannot cancel this upload'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    upload.status = 'failed'
    upload.error_message = 'Cancelled by user'
    upload.save()
    
    return Response({'message': 'Upload cancelled'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def platform_analytics(request, pk):
    """Get analytics for a specific upload"""
    upload = get_object_or_404(SocialMediaUpload, id=pk, user=request.user)
    
    try:
        analytics = upload.platformanalytics
        serializer = PlatformAnalyticsSerializer(analytics)
        return Response(serializer.data)
    except PlatformAnalytics.DoesNotExist:
        return Response({'error': 'Analytics not available'}, status=404)
