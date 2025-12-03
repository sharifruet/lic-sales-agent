"""Voice API routes for real-time voice conversations."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import Optional
import json
import asyncio
import base64

from app.src.services.voice import STTService, TTSService
from app.src.services.conversation_service import ConversationService
from app.src.services.session_manager import SessionManager
from config.database import get_db
from app.src.config import settings

router = APIRouter(prefix="/voice", tags=["voice"])

# Initialize services
stt_service = STTService()
tts_service = TTSService()
session_manager = SessionManager()


@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: Optional[str] = None,
    session_id: Optional[str] = None
):
    """Transcribe audio file to text."""
    if not settings.voice_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice features are disabled"
        )
    
    try:
        # Read audio data
        audio_data = await audio_file.read()
        
        # Transcribe
        text = await stt_service.transcribe_audio(audio_data, language or settings.default_language)
        
        # If session_id provided, process as conversation message
        if session_id:
            from config.database import AsyncSessionLocal
            db = AsyncSessionLocal()
            try:
                conversation_service = ConversationService(db)
                response = await conversation_service.process_message(session_id, text)
                await db.commit()
                
                return {
                    "transcription": text,
                    "session_id": session_id,
                    "response": response
                }
            finally:
                await db.close()
        
        return {
            "transcription": text,
            "language": language or settings.default_language
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription error: {str(e)}"
        )


@router.post("/synthesize")
async def synthesize_speech(
    text: str,
    language: Optional[str] = None,
    voice: Optional[str] = None
):
    """Convert text to speech audio."""
    if not settings.voice_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice features are disabled"
        )
    
    try:
        audio_bytes = await tts_service.synthesize_speech(
            text,
            language or settings.default_language,
            voice or settings.tts_voice
        )
        
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Speech synthesis error: {str(e)}"
        )


@router.websocket("/conversation/{session_id}")
async def voice_conversation_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time voice conversations."""
    if not settings.voice_enabled:
        await websocket.close(code=1008, reason="Voice features disabled")
        return
    
    await websocket.accept()
    
    # Initialize conversation service with database session
    from config.database import AsyncSessionLocal
    
    db = AsyncSessionLocal()
    conversation_service = ConversationService(db)
    
    try:
        while True:
            # Receive audio data from client
            data = await websocket.receive()
            
            if "text" in data:
                # Handle text messages (for control/meta)
                message = json.loads(data["text"])
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "close":
                    break
            
            elif "bytes" in data:
                # Handle audio data
                audio_data = data["bytes"]
                
                # Transcribe audio to text
                try:
                    transcription = await stt_service.transcribe_audio(audio_data)
                    
                    # Send transcription back to client
                    await websocket.send_json({
                        "type": "transcription",
                        "text": transcription
                    })
                    
                    # Process message through conversation service
                    response = await conversation_service.process_message(session_id, transcription)
                    response_text = response.get("response", "")
                    
                    # Synthesize response to speech
                    audio_response = await tts_service.synthesize_speech(response_text)
                    
                    # Send audio response
                    await websocket.send_bytes(audio_response)
                    
                    # Send text response metadata
                    await websocket.send_json({
                        "type": "response",
                        "text": response_text,
                        "session_id": session_id,
                        "stage": response.get("conversation_stage", ""),
                        "interest_level": response.get("interest_level", "")
                    })
                
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
    
    except WebSocketDisconnect:
        # Handle disconnect gracefully
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Connection error: {str(e)}"
            })
        except:
            pass
    finally:
        try:
            await db.close()
            await websocket.close()
        except:
            pass


@router.get("/voices")
async def get_available_voices():
    """Get list of available TTS voices."""
    voices = tts_service.get_supported_voices()
    return {
        "voices": voices,
        "default_voice": settings.tts_voice,
        "provider": settings.tts_provider
    }

