"""Text-to-Speech service for voice output."""
from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path
import io


class TTSProvider(ABC):
    """Abstract base class for Text-to-Speech providers."""
    
    @abstractmethod
    async def synthesize(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> bytes:
        """Synthesize text to speech audio bytes."""
        pass


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS API provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "tts-1", voice: str = "alloy"):
        self.api_key = api_key
        self.model = model
        self.default_voice = voice
        if not self.api_key:
            from src.config import settings
            self.api_key = settings.openai_api_key
    
    async def synthesize(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> bytes:
        """Synthesize text to speech using OpenAI TTS."""
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.audio.speech.create(
                model=self.model,
                voice=voice or self.default_voice,
                input=text
            )
            
            # Read audio bytes
            audio_bytes = b""
            async for chunk in response:
                audio_bytes += chunk
            
            return audio_bytes
        except Exception as e:
            raise Exception(f"OpenAI TTS error: {str(e)}")


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs TTS API provider (alternative)."""
    
    def __init__(self, api_key: Optional[str] = None, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        self.api_key = api_key
        self.voice_id = voice_id
    
    async def synthesize(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> bytes:
        """Synthesize text to speech using ElevenLabs."""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice or self.voice_id}",
                    headers={
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": self.api_key or ""
                    },
                    json={
                        "text": text,
                        "model_id": "eleven_monolingual_v1",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.5
                        }
                    }
                )
                response.raise_for_status()
                return response.content
        except Exception as e:
            raise Exception(f"ElevenLabs TTS error: {str(e)}")


class GoogleTTSProvider(TTSProvider):
    """Google Cloud TTS provider (alternative)."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    async def synthesize(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> bytes:
        """Synthesize text to speech using Google TTS."""
        import httpx
        
        try:
            lang = language or "en-US"
            voice_name = voice or "en-US-Wavenet-D"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"https://texttospeech.googleapis.com/v1/text:synthesize?key={self.api_key}",
                    json={
                        "input": {"text": text},
                        "voice": {"languageCode": lang, "name": voice_name},
                        "audioConfig": {"audioEncoding": "MP3"}
                    }
                )
                response.raise_for_status()
                data = response.json()
                import base64
                return base64.b64decode(data["audioContent"])
        except Exception as e:
            raise Exception(f"Google TTS error: {str(e)}")


class TTSService:
    """Service for Text-to-Speech operations."""
    
    def __init__(self, provider: Optional[TTSProvider] = None):
        from src.config import settings
        self.provider = provider or self._create_default_provider(settings)
    
    def _create_default_provider(self, settings) -> TTSProvider:
        """Create default TTS provider based on settings."""
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return OpenAITTSProvider(api_key=settings.openai_api_key)
        else:
            # For local/dev, you might want to use a free TTS service
            # or provide a simple fallback
            # Defaulting to OpenAI for now
            return OpenAITTSProvider(api_key=settings.openai_api_key)
    
    async def synthesize_speech(self, text: str, language: Optional[str] = None, voice: Optional[str] = None) -> bytes:
        """Synthesize text to speech audio."""
        return await self.provider.synthesize(text, language, voice)
    
    def get_supported_voices(self) -> list[str]:
        """Get list of supported voices."""
        if isinstance(self.provider, OpenAITTSProvider):
            return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        elif isinstance(self.provider, ElevenLabsTTSProvider):
            return ["21m00Tcm4TlvDq8ikWAM"]  # Default voice
        else:
            return ["default"]

