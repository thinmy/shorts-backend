from rest_framework import serializers
from .models import Video, Tag, VideoProcessingTask, YouTubeDownload


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'created_at')


class VideoSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=50), 
        write_only=True, 
        required=False
    )

    class Meta:
        model = Video
        fields = (
            'id', 'title', 'description', 'video_file', 'thumbnail', 
            'duration', 'file_size', 'status', 'transcription', 'tags', 
            'tag_names', 'is_public', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'thumbnail', 'duration', 'file_size', 'status', 
            'transcription', 'created_at', 'updated_at'
        )

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        video = Video.objects.create(**validated_data)
        
        # Create or get tags
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip().lower())
            video.tags.add(tag)
        
        return video

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        
        # Update video fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tag_names is not None:
            instance.tags.clear()
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name.strip().lower())
                instance.tags.add(tag)
        
        return instance


class VideoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('title', 'description', 'video_file', 'is_public')

    def validate_video_file(self, value):
        # Validate file size (100MB limit)
        if value.size > 100 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 100MB")
        
        # Validate file format
        allowed_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm']
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in allowed_formats:
            raise serializers.ValidationError(
                f"File format not supported. Allowed formats: {', '.join(allowed_formats)}"
            )
        
        return value


class VideoProcessingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoProcessingTask
        fields = (
            'id', 'task_type', 'status', 'result', 'error_message', 
            'started_at', 'completed_at', 'created_at'
        )


class YouTubeDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeDownload
        fields = ('id', 'youtube_url', 'status', 'error_message', 'created_at')
        read_only_fields = ('id', 'status', 'error_message', 'created_at')

    def validate_youtube_url(self, value):
        # Basic YouTube URL validation
        youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com']
        if not any(domain in value for domain in youtube_domains):
            raise serializers.ValidationError("Please provide a valid YouTube URL")
        return value


class VideoListSerializer(serializers.ModelSerializer):
    """Simplified serializer for video lists"""
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Video
        fields = (
            'id', 'title', 'thumbnail', 'duration', 'status', 
            'tags', 'is_public', 'created_at'
        )
