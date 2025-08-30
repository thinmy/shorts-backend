from django.db import models
from django.contrib.auth import get_user_model
from apps.videos.models import Video

User = get_user_model()


class SocialPlatform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    api_endpoint = models.URLField()
    is_active = models.BooleanField(default=True)
    max_video_size = models.BigIntegerField(help_text="Tamanho máximo em bytes")
    supported_formats = models.JSONField(default=list)
    max_duration = models.DurationField(blank=True, null=True)
    
    def __str__(self):
        return self.name


class SocialMediaUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('uploading', 'Enviando'),
        ('published', 'Publicado'),
        ('failed', 'Falhou'),
        ('scheduled', 'Agendado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    platform = models.ForeignKey(SocialPlatform, on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    hashtags = models.CharField(max_length=500, blank=True)
    schedule_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_id = models.CharField(max_length=100, blank=True)  # ID da plataforma
    external_url = models.URLField(blank=True)  # URL do post
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['video', 'platform']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.video.title} → {self.platform.name}"


class PlatformAnalytics(models.Model):
    upload = models.OneToOneField(SocialMediaUpload, on_delete=models.CASCADE)
    views = models.BigIntegerField(default=0)
    likes = models.BigIntegerField(default=0)
    comments = models.BigIntegerField(default=0)
    shares = models.BigIntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics: {self.upload}"
