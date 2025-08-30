from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Video(models.Model):
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    file_size = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    transcription = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class VideoProcessingTask(models.Model):
    TASK_TYPES = [
        ('transcription', 'Transcription'),
        ('thumbnail_generation', 'Thumbnail Generation'),
        ('video_compression', 'Video Compression'),
        ('content_analysis', 'Content Analysis'),
    ]

    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='processing_tasks')
    task_type = models.CharField(max_length=30, choices=TASK_TYPES)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    result = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.video.title} - {self.task_type}"


class YouTubeDownload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    youtube_url = models.URLField()
    video = models.OneToOneField(Video, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=20, default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Download: {self.youtube_url}"
