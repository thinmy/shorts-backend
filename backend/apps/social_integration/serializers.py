from rest_framework import serializers
from .models import SocialPlatform, SocialMediaUpload, PlatformAnalytics
from apps.videos.models import Video


class SocialPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialPlatform
        fields = (
            'id', 'name', 'max_video_size', 'supported_formats', 
            'max_duration', 'is_active'
        )


class SocialMediaUploadSerializer(serializers.ModelSerializer):
    video_title = serializers.CharField(source='video.title', read_only=True)
    platform_name = serializers.CharField(source='platform.name', read_only=True)

    class Meta:
        model = SocialMediaUpload
        fields = (
            'id', 'video', 'video_title', 'platform', 'platform_name',
            'caption', 'hashtags', 'schedule_date', 'status', 
            'external_id', 'external_url', 'error_message',
            'created_at', 'published_at'
        )
        read_only_fields = (
            'id', 'status', 'external_id', 'external_url', 
            'error_message', 'created_at', 'published_at'
        )

    def validate_video(self, value):
        # Check if video belongs to the user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You don't have permission to use this video")
        
        # Check if video is ready
        if value.status != 'ready':
            raise serializers.ValidationError("Video is not ready for upload")
        
        return value

    def validate(self, attrs):
        video = attrs['video']
        platform = attrs['platform']
        
        # Check if video meets platform requirements
        if video.file_size and video.file_size > platform.max_video_size:
            raise serializers.ValidationError(
                f"Video is too large for {platform.name}. "
                f"Maximum size: {platform.max_video_size} bytes"
            )
        
        if video.duration and platform.max_duration and video.duration > platform.max_duration:
            raise serializers.ValidationError(
                f"Video is too long for {platform.name}. "
                f"Maximum duration: {platform.max_duration}"
            )
        
        # Check if already uploaded to this platform
        if SocialMediaUpload.objects.filter(
            video=video, 
            platform=platform, 
            status__in=['published', 'uploading', 'pending']
        ).exists():
            raise serializers.ValidationError(
                f"Video is already uploaded or being uploaded to {platform.name}"
            )
        
        return attrs


class PlatformAnalyticsSerializer(serializers.ModelSerializer):
    upload_info = SocialMediaUploadSerializer(source='upload', read_only=True)

    class Meta:
        model = PlatformAnalytics
        fields = (
            'views', 'likes', 'comments', 'shares', 
            'engagement_rate', 'last_updated', 'upload_info'
        )


class BulkUploadSerializer(serializers.Serializer):
    video = serializers.PrimaryKeyRelatedField(queryset=Video.objects.all())
    platforms = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=SocialPlatform.objects.all())
    )
    caption = serializers.CharField(required=False, allow_blank=True)
    hashtags = serializers.CharField(required=False, allow_blank=True)
    schedule_date = serializers.DateTimeField(required=False)

    def validate_video(self, value):
        # Check if video belongs to the user
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("You don't have permission to use this video")
        
        # Check if video is ready
        if value.status != 'ready':
            raise serializers.ValidationError("Video is not ready for upload")
        
        return value

    def create(self, validated_data):
        video = validated_data['video']
        platforms = validated_data['platforms']
        caption = validated_data.get('caption', '')
        hashtags = validated_data.get('hashtags', '')
        schedule_date = validated_data.get('schedule_date')
        
        uploads = []
        for platform in platforms:
            upload = SocialMediaUpload.objects.create(
                user=self.context['request'].user,
                video=video,
                platform=platform,
                caption=caption,
                hashtags=hashtags,
                schedule_date=schedule_date
            )
            uploads.append(upload)
        
        return uploads
