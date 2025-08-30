import openai
import google.generativeai as genai
from groq import Groq
from django.conf import settings
import moviepy.editor as mp
import tempfile
import os


class TranscriptionService:
    """Service for transcribing videos using various AI providers"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
        
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    def transcribe_video(self, video_path, provider='openai'):
        """Transcribe video using specified AI provider"""
        # Extract audio from video
        audio_path = self._extract_audio(video_path)
        
        try:
            if provider == 'openai' and self.openai_client:
                return self._transcribe_with_openai(audio_path)
            elif provider == 'groq' and self.groq_client:
                return self._transcribe_with_groq(audio_path)
            elif provider == 'gemini' and settings.GEMINI_API_KEY:
                return self._transcribe_with_gemini(audio_path)
            else:
                raise ValueError(f"Provider {provider} not available or not configured")
        finally:
            # Clean up audio file
            if os.path.exists(audio_path):
                os.remove(audio_path)

    def _extract_audio(self, video_path):
        """Extract audio from video file"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            audio_path = temp_audio.name

        with mp.VideoFileClip(video_path) as video:
            audio = video.audio
            if audio:
                audio.write_audiofile(audio_path, verbose=False, logger=None)
            else:
                raise ValueError("No audio track found in video")

        return audio_path

    def _transcribe_with_openai(self, audio_path):
        """Transcribe using OpenAI Whisper"""
        with open(audio_path, 'rb') as audio_file:
            transcript = self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript

    def _transcribe_with_groq(self, audio_path):
        """Transcribe using Groq"""
        with open(audio_path, 'rb') as audio_file:
            transcript = self.groq_client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="text"
            )
        return transcript.text

    def _transcribe_with_gemini(self, audio_path):
        """Transcribe using Google Gemini"""
        # Note: Gemini API for audio transcription might need different implementation
        # This is a placeholder - check Gemini documentation for audio handling
        model = genai.GenerativeModel('gemini-pro')
        
        # For now, return a placeholder
        return "Gemini transcription not yet implemented"


class ContentAnalysisService:
    """Service for analyzing video content using AI"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    def analyze_content(self, transcription, provider='openai'):
        """Analyze content and generate tags, summary, etc."""
        if provider == 'openai' and self.openai_client:
            return self._analyze_with_openai(transcription)
        elif provider == 'gemini' and settings.GEMINI_API_KEY:
            return self._analyze_with_gemini(transcription)
        else:
            raise ValueError(f"Provider {provider} not available")

    def _analyze_with_openai(self, transcription):
        """Analyze content using OpenAI GPT"""
        prompt = f"""
        Analyze the following video transcription and provide:
        1. A brief summary (max 100 words)
        2. 5-10 relevant tags
        3. Main topics discussed
        4. Sentiment analysis (positive, negative, neutral)

        Transcription: {transcription}

        Please format your response as JSON with keys: summary, tags, topics, sentiment
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    def _analyze_with_gemini(self, transcription):
        """Analyze content using Google Gemini"""
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Analyze the following video transcription and provide:
        1. A brief summary (max 100 words)
        2. 5-10 relevant tags
        3. Main topics discussed
        4. Sentiment analysis (positive, negative, neutral)

        Transcription: {transcription}

        Please format your response as JSON with keys: summary, tags, topics, sentiment
        """

        response = model.generate_content(prompt)
        return response.text
