"""Tests for voice services."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path

from src.services.voice import STTService, TTSService
from src.services.voice.stt_service import OpenAISTTProvider
from src.services.voice.tts_service import OpenAITTSProvider


@pytest.mark.asyncio
async def test_stt_transcribe():
    """Test STT transcription."""
    mock_provider = AsyncMock(spec=OpenAISTTProvider)
    mock_provider.transcribe = AsyncMock(return_value="Hello, this is a test.")
    
    service = STTService(provider=mock_provider)
    
    audio_data = b"fake_audio_data"
    result = await service.transcribe_audio(audio_data, language="en")
    
    assert result == "Hello, this is a test."
    mock_provider.transcribe.assert_called_once_with(audio_data, "en")


@pytest.mark.asyncio
async def test_tts_synthesize():
    """Test TTS synthesis."""
    mock_provider = AsyncMock(spec=OpenAITTSProvider)
    mock_provider.synthesize = AsyncMock(return_value=b"fake_audio_bytes")
    
    service = TTSService(provider=mock_provider)
    
    text = "Hello, this is a test."
    result = await service.synthesize_speech(text, language="en", voice="alloy")
    
    assert result == b"fake_audio_bytes"
    mock_provider.synthesize.assert_called_once_with(text, "en", "alloy")


@pytest.mark.asyncio
async def test_stt_transcribe_file():
    """Test STT transcription from file."""
    mock_provider = AsyncMock(spec=OpenAISTTProvider)
    mock_provider.transcribe_file = AsyncMock(return_value="Transcribed text")
    
    service = STTService(provider=mock_provider)
    
    test_file = Path("/tmp/test_audio.webm")
    result = await service.transcribe_file(test_file, language="en")
    
    assert result == "Transcribed text"
    mock_provider.transcribe_file.assert_called_once_with(test_file, "en")


def test_tts_get_voices():
    """Test getting available voices."""
    mock_provider = Mock(spec=OpenAITTSProvider)
    
    service = TTSService(provider=mock_provider)
    voices = service.get_supported_voices()
    
    assert isinstance(voices, list)
    assert len(voices) > 0

