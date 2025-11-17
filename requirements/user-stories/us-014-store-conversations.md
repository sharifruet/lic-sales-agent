# US-014: Store Conversation Logs

## User Story
As a **system**
I want to **store conversation transcripts and logs**
So that **conversations can be reviewed, analyzed, and linked to leads**

## Acceptance Criteria

### AC-014.1: Message Storage
- Given a conversation is in progress
- When messages are exchanged
- Then the system stores each message with:
  - Message ID
  - Conversation ID (session identifier)
  - Role (user, assistant, system)
  - Content (message text)
  - Timestamp
  - Metadata (optional: sentiment, intent, etc.)
- And all messages are stored

### AC-014.2: Conversation Record
- Given a conversation session
- When conversation starts
- Then the system creates conversation record with:
  - Conversation ID
  - Session ID
  - Started at timestamp
  - Customer profile information (if collected)
  - Detected interests
  - Detected intent
  - Conversation summary (generated at end)
- And record is created at session start

### AC-014.3: Conversation Summary
- Given conversation ends
- When storing conversation
- Then the system generates and stores summary:
  - Customer profile summary
  - Topics discussed
  - Policies presented
  - Objections raised
  - Interest level detected
  - Outcome (lead created, not interested, etc.)
  - Duration (total conversation time)
- And summary is searchable and human-readable

### AC-014.4: Conversation Linkage
- Given conversation and lead (if created)
- When storing
- Then the system maintains bidirectional linkage:
  - Conversation references lead ID (if lead created)
  - Lead references conversation ID
- And linkage enables easy navigation

### AC-014.5: Complete Transcript Storage
- Given conversation is stored
- When retrieving
- Then the system provides:
  - Complete message history in chronological order
  - All messages with timestamps
  - Full conversation context
- And transcript is easily readable

### AC-014.6: Conversation Metadata
- Given conversation is stored
- When storing
- Then the system includes metadata:
  - Duration (seconds)
  - Message count
  - Customer engagement metrics
  - Topics discussed tags
  - Outcome classification
- And metadata enables analytics and reporting

### AC-014.7: Storage Performance
- Given conversations are stored in real-time
- When storing messages
- Then storage doesn't significantly impact conversation response time
- And system handles high message volume
- And storage is reliable

## Detailed Scenarios

### Scenario 1: Complete Conversation Storage
**Given**: 50-message conversation with lead created  
**When**: Conversation ends  
**Then**: All 50 messages stored with timestamps, conversation record created, summary generated, linked to lead

### Scenario 2: Conversation Without Lead
**Given**: Conversation where customer wasn't interested  
**When**: Conversation ends  
**Then**: Conversation and messages stored, summary indicates "not interested", no lead created, conversation still accessible

### Scenario 3: Long Conversation
**Given**: 200-message conversation  
**When**: Storing conversation  
**Then**: All messages stored efficiently, summary captures key points, metadata includes high engagement metrics

### Scenario 4: Conversation Retrieval
**Given**: Lead ID is known  
**When**: Retrieving conversation  
**Then**: System retrieves full conversation transcript, summary, and metadata linked to that lead

## Technical Notes

- Conversation and Message models in PostgreSQL
- Real-time message storage via `ConversationService`
- Conversation summary generation via LLM (`generate_summary()`)
- Metadata stored in `Conversation` model (stage, message_count)
- Session state in Redis, messages in PostgreSQL
- Indexing for performance (conversation_id, session_id, timestamps)

## API Implementation

**Endpoint**: `GET /api/conversation/{session_id}`

**Response**:
```json
{
  "session_id": "abc123...",
  "conversation_id": "def456...",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hello! I'm Alex...",
      "timestamp": "2024-01-15T10:00:01Z"
    }
  ],
  "customer_profile": {
    "age": 35,
    "name": "John",
    "purpose": "family protection"
  },
  "conversation_stage": "information"
}
```

**Endpoint**: `POST /api/conversation/end`

**Response**:
```json
{
  "session_id": "abc123...",
  "conversation_id": "def456...",
  "status": "ended",
  "summary": "Customer was interested in term life insurance...",
  "duration_seconds": 420
}
```

**Implementation Details**:
- Messages stored in real-time via `ConversationService.process_message()`
- Conversation record created at start
- Summary generated via LLM at end
- All messages linked to conversation
- Metadata tracked (stage, message_count, duration)

## Related Requirements
- **FR-7.3**: Store conversation transcripts/logs
- **FR-7.4**: Timestamp all records

## Dependencies
- **Depends on**: US-001 (conversation session)
- **Blocks**: US-017 (view transcripts)

## Story Points
**Estimate**: 6 points

## Priority
**High** - Important for analytics, quality assurance, and customer service

## Implementation Status
- **Status**: ✅ Done
- **API Endpoints**: 
  - `POST /api/conversation/start` - Creates conversation record
  - `POST /api/conversation/message` - Stores messages
  - `POST /api/conversation/end` - Generates summary
  - `GET /api/conversation/{session_id}` - Retrieves transcript
- **Implementation Notes**: 
  - Real-time message storage
  - Conversation summary via LLM
  - Metadata tracking
  - Full transcript retrieval
  - Session state management

---

## Implementation Considerations

- ✅ Conversation and message database schema (`Conversation`, `Message` models)
- ✅ Real-time message storage (async, non-blocking)
- ✅ Conversation summary generation (LLM-based)
- ✅ Indexing strategy for fast retrieval
- ✅ Metadata tracking (stage, count, duration)
- ✅ Retention policy (database-level)
