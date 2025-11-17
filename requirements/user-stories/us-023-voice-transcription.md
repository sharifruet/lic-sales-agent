# US-023: Voice-to-Text Transcription

## User Story
As a **customer**
I want to **speak to the AI insurance agent using my voice**
So that **I can have natural voice conversations without typing**

## Acceptance Criteria

### AC-023.1: Audio Input Processing
- Given a customer wants to use voice input
- When they send an audio file or stream
- Then the system transcribes the audio to text
- And transcription is accurate for common speech patterns
- And system handles various audio formats (MP3, WAV, WebM)

### AC-023.2: Language Support
- Given audio input in different languages
- When transcribing
- Then the system detects language automatically or uses specified language
- And transcription supports multiple languages (English, Spanish, etc.)
- And language detection is accurate

### AC-023.3: Real-Time Transcription
- Given a real-time voice conversation
- When customer speaks
- Then the system transcribes speech as it happens
- And transcription latency is minimal (< 2 seconds)
- And transcription quality is maintained

### AC-023.4: Error Handling
- Given audio input with poor quality or noise
- When transcribing
- Then the system handles errors gracefully
- And system provides feedback if transcription fails
- And system can request audio resubmission if needed

## Detailed Scenarios

### Scenario 1: Upload Audio File
**Given**: Customer uploads audio file  
**When**: System processes audio  
**Then**: System transcribes to text, processes as conversation message, returns transcription and response

### Scenario 2: Real-Time Voice Stream
**Given**: Customer uses WebSocket for voice  
**When**: Customer speaks  
**Then**: System transcribes in real-time, processes message, generates response

### Scenario 3: Multi-Language Support
**Given**: Customer speaks in Spanish  
**When**: System transcribes  
**Then**: System detects language, transcribes accurately, processes in appropriate language

## Technical Notes

- Speech-to-Text (STT) service abstraction supporting multiple providers
- Providers: OpenAI Whisper, Ollama, Google Cloud Speech
- Audio format conversion and preprocessing
- Language detection and selection
- Error handling and retry logic

## API Implementation

**Endpoint**: `POST /api/voice/transcribe`

**Request**:
- `audio_file`: Audio file (multipart/form-data)
- `language`: Optional language code (default: "en")
- `session_id`: Optional session ID for conversation context

**Response**:
```json
{
  "transcription": "I'm interested in life insurance",
  "language": "en",
  "session_id": "abc123...",
  "response": {
    "message": "Great! I'd be happy to help...",
    "interest_detected": "medium",
    "conversation_stage": "qualification"
  }
}
```

**Implementation Details**:
- `STTService` with provider abstraction
- Supports OpenAI Whisper API
- Supports Ollama for local processing
- Automatic language detection
- Integration with conversation service

## Related Requirements
- **FR-10.1**: Voice-to-text conversion
- **NFR-1**: Response time < 2 seconds

## Dependencies
- **Depends on**: US-001 (conversation system)
- **Blocks**: US-025 (real-time voice conversations)

## Story Points
**Estimate**: 5 points

## Priority
**Medium** - Phase 2 feature

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `POST /api/voice/transcribe`
- **Implementation Notes**: 
  - STT service with multiple provider support
  - OpenAI Whisper and Ollama integration
  - Language detection and selection
  - Error handling implemented

