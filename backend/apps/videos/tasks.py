from celery import shared_task
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import yt_dlp
import moviepy.editor as mp
from moviepy.video.fx import resize
import os
import tempfile
from .models import Video, VideoProcessingTask, YouTubeDownload
from apps.ai_processing.services import TranscriptionService


@shared_task
def download_youtube_video(download_id):
    """Download video from YouTube using yt-dlp"""
    try:
        download = YouTubeDownload.objects.get(id=download_id)
        download.status = 'processing'
        download.save()

        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[height<=720]',  # Limit to 720p
            'outtmpl': f'/tmp/%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info
            info = ydl.extract_info(download.youtube_url, download=False)
            title = info.get('title', 'Downloaded Video')
            description = info.get('description', '')
            duration = info.get('duration', 0)

            # Download the video
            ydl.download([download.youtube_url])

            # Find the downloaded file
            video_path = None
            for file in os.listdir('/tmp'):
                if title in file and file.endswith(('.mp4', '.webm', '.mkv')):
                    video_path = os.path.join('/tmp', file)
                    break

            if video_path and os.path.exists(video_path):
                # Create Video object
                video = Video.objects.create(
                    user=download.user,
                    title=title,
                    description=description[:500],  # Limit description length
                    status='processing'
                )

                # Save video file
                with open(video_path, 'rb') as f:
                    video.video_file.save(
                        f"{video.id}.mp4",
                        ContentFile(f.read()),
                        save=True
                    )

                # Clean up temporary file
                os.remove(video_path)

                # Update download record
                download.video = video
                download.status = 'completed'
                download.save()

                # Start video processing tasks
                process_video.delay(video.id)

            else:
                download.status = 'failed'
                download.error_message = 'Could not find downloaded file'
                download.save()

    except Exception as e:
        download.status = 'failed'
        download.error_message = str(e)
        download.save()


@shared_task
def process_video(video_id):
    """Process uploaded video - generate thumbnail, compress, etc."""
    try:
        video = Video.objects.get(id=video_id)
        video.status = 'processing'
        video.save()

        # Create processing tasks
        tasks = [
            'generate_thumbnail',
            'extract_transcription',
            'compress_video'
        ]

        for task_type in tasks:
            task = VideoProcessingTask.objects.create(
                video=video,
                task_type=task_type,
                status='pending'
            )

            # Start the specific task
            if task_type == 'generate_thumbnail':
                generate_thumbnail.delay(task.id)
            elif task_type == 'extract_transcription':
                extract_transcription.delay(task.id)
            elif task_type == 'compress_video':
                compress_video.delay(task.id)

    except Exception as e:
        video.status = 'failed'
        video.save()


@shared_task
def generate_thumbnail(task_id):
    """Generate thumbnail from video"""
    try:
        task = VideoProcessingTask.objects.get(id=task_id)
        task.status = 'processing'
        task.save()

        video = task.video
        video_path = video.video_file.path

        # Use MoviePy to extract frame at 10% of video duration
        with mp.VideoFileClip(video_path) as clip:
            # Get frame at 10% of duration or 1 second, whichever is smaller
            time = min(clip.duration * 0.1, 1.0)
            frame = clip.get_frame(time)

            # Save thumbnail
            thumbnail_path = f"/tmp/thumbnail_{video.id}.jpg"
            mp.ImageClip(frame).save_frame(thumbnail_path)

            # Save to model
            with open(thumbnail_path, 'rb') as f:
                video.thumbnail.save(
                    f"thumb_{video.id}.jpg",
                    ContentFile(f.read()),
                    save=True
                )

            # Clean up
            os.remove(thumbnail_path)

        task.status = 'completed'
        task.save()

    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()


@shared_task
def extract_transcription(task_id):
    """Extract transcription from video using AI services"""
    try:
        task = VideoProcessingTask.objects.get(id=task_id)
        task.status = 'processing'
        task.save()

        video = task.video
        
        # Use AI service to transcribe
        transcription_service = TranscriptionService()
        transcription = transcription_service.transcribe_video(video.video_file.path)

        video.transcription = transcription
        video.save()

        task.status = 'completed'
        task.result = {'transcription': transcription}
        task.save()

    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()


@shared_task
def compress_video(task_id):
    """Compress video for better performance"""
    try:
        task = VideoProcessingTask.objects.get(id=task_id)
        task.status = 'processing'
        task.save()

        video = task.video
        video_path = video.video_file.path

        # Create compressed version
        with mp.VideoFileClip(video_path) as clip:
            # Resize if too large
            if clip.h > 720:
                clip = resize(clip, height=720)

            # Compress and save
            compressed_path = f"/tmp/compressed_{video.id}.mp4"
            clip.write_videofile(
                compressed_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='/tmp/temp-audio.m4a',
                remove_temp=True
            )

            # Replace original with compressed version
            with open(compressed_path, 'rb') as f:
                video.video_file.save(
                    video.video_file.name,
                    ContentFile(f.read()),
                    save=True
                )

            # Clean up
            os.remove(compressed_path)

        # Mark video as ready
        video.status = 'ready'
        video.save()

        task.status = 'completed'
        task.save()

    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.save()

        # Mark video as failed
        video = task.video
        video.status = 'failed'
        video.save()
