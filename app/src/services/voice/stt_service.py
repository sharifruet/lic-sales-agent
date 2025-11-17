"""Speech-to-Text service for voice input."""
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
from pathlib import Path
import base64
import io


class STTProvider(ABC):
    """Abstract base class for Speech-to-Text providers."""
    
    @abstractmethod
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio to text."""
        pass
    
    @abstractmethod
    async def transcribe_file(self, file_path: Path, language: Optional[str] = None) -> str:
        """Transcribe audio file to text."""
        pass


class OpenAISTTProvider(STTProvider):
    """OpenAI Whisper API provider for STT."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        self.api_key = api_key
        self.model = model
        if not self.api_key:
            from src.config import settings
            self.api_key = settings.openai_api_key
    
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio bytes to text using OpenAI Whisper."""
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            # Create a file-like object from bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.webm"  # Set filename for OpenAI
            
            # Transcribe
            transcript = await client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language
            )
            return transcript.text
        except Exception as e:
            raise Exception(f"OpenAI STT error: {str(e)}")
    
    async def transcribe_file(self, file_path: Path, language: Optional[str] = None) -> str:
        """Transcribe audio file to text."""
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        return await self.transcribe(audio_data, language)


class OllamaSTTProvider(STTProvider):
    """Ollama Whisper model provider for STT (local)."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "whisper"):
        self.base_url = base_url
        self.model = model
    
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio using Ollama Whisper model."""
        import httpx
        
        try:
            # For Ollama, we'd need to use their API format
            # This is a placeholder - actual implementation depends on Ollama Whisper API
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Note: This assumes Ollama has a whisper endpoint
                # Adjust based on actual Ollama Whisper API
                response = await client.post(
                    f"{self.base_url}/api/transcribe",
                    json={
                        "model": self.model,
                        "audio": base64.b64encode(audio_data).decode(),
                        "language": language
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("text", "")
        except Exception as e:
            raise Exception(f"Ollama STT error: {str(e)}")
    
    async def transcribe_file(self, file_path: Path, language: Optional[str] = None) -> str:
        """Transcribe audio file to text."""
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        return await self.transcribe(audio_data, language)


class STTService:
    """Service for Speech-to-Text operations."""
    
    def __init__(self, provider: Optional[STTProvider] = None):
        from src.config import settings
        self.provider = provider or self._create_default_provider(settings)
    
    def _create_default_provider(self, settings) -> STTProvider:
        """Create default STT provider based on settings."""
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return OpenAISTTProvider(api_key=settings.openai_api_key)
        else:
            # Default to Ollama for local development
            return OllamaSTTProvider(
                base_url=settings.ollama_base_url,
                model="whisper"
            )
    
    async def transcribe_audio(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcribe audio data to text."""
        return await self.provider.transcribe(audio_data, language)
    
    async def transcribe_file(self, file_path: Path, language: Optional[str] = None) -> str:
        """Transcribe audio file to text."""
        return await self.provider.transcribe_file(file_path, language)

