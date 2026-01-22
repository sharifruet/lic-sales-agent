# US-015: Maintain Conversation Context

## User Story
As a **potential customer**
I want the **AI agent to remember our conversation**
So that **I don't have to repeat information and the conversation feels natural**

## Acceptance Criteria

### AC-015.1: Context Memory
- Given a conversation is in progress
- When customer provides information or asks questions
- Then the system remembers throughout conversation:
  - Customer profile information (age, family, needs)
  - Policies discussed and customer reactions
  - Questions asked and answers provided
  - Objections raised and responses given
  - Stated preferences and concerns
  - Collected information
- And context is maintained for entire session

### AC-015.2: Natural Context Reference
- Given previous conversation elements exist
- When system responds
- Then the system references previous elements naturally:
  - "Earlier you mentioned..."
  - "As we discussed..."
  - "Based on your situation..."
- And references feel natural, not forced

### AC-015.3: Avoid Repetition
- Given information was already provided
- When system responds
- Then the system doesn't repeat entire information unless:
  - Customer requests clarification
  - Customer asks to repeat
  - Summarizing at end of conversation
- And system acknowledges previous discussion

### AC-015.4: Context History
- Given conversation is ongoing
- When maintaining context
- Then the system maintains conversation history:
  - Minimum 50 previous messages in context
  - Full conversation history accessible
  - Context window optimized for LLM
- And system manages context window efficiently

### AC-015.5: Context Switching
- Given customer changes topic
- When handling topic change
- Then the system:
  - Preserves relevant background information
  - Maintains connection to previous topics when relevant
  - Switches context smoothly
- And system doesn't lose important information

### AC-015.6: Long Conversation Handling
- Given conversation exceeds context window
- When managing long conversations
- Then the system:
  - Maintains summary of earlier conversation
  - Preserves key information (profile, collected data)
  - Manages context window intelligently
- And conversation remains coherent

## Detailed Scenarios

### Scenario 1: Reference Previous Statement
**Given**: Customer earlier said "I have two children"  
**When**: Discussing policy benefits  
**Then**: System says "Since you mentioned you have two children, this policy would protect them with..."

### Scenario 2: Avoid Repeating Policy Info
**Given**: System already explained Term Life policy  
**When**: Customer asks follow-up question about same policy  
**Then**: System answers without repeating entire policy description, references previous explanation

### Scenario 3: Context Across Topics
**Given**: Customer discussed age (35), then asked about policies, then asked about cost  
**When**: Discussing cost  
**Then**: System remembers age when discussing age-related premiums, remembers policy interest when discussing payment

### Scenario 4: Long Conversation - Context Management
**Given**: 100-message conversation  
**When**: System responds to latest message  
**Then**: System maintains summary of earlier conversation, keeps key profile data, references recent messages, stays coherent

## Technical Notes

- Conversation state management via `SessionManager` (Redis)
- Context window management via `ContextManager` (50 messages, 8000 tokens)
- Conversation summarization for long conversations (context compression)
- Key information extraction and preservation (customer profile, collected data)
- Message history stored in PostgreSQL, loaded into context
- Context building via `ContextManager.build_context()`

## API Implementation

**Endpoint**: `POST /api/conversation/message`

**Context Management**:
- Session state loaded from Redis
- Message history loaded from database
- Context built via `ContextManager`
- Customer profile included in context
- Policies included in context
- Context summary for long conversations

**Implementation Details**:
- `ContextManager` maintains up to 50 recent messages
- Context compression for long conversations (summarizes middle messages)
- Customer profile always preserved in context
- Policies included in context for natural references
- LLM receives full context for coherent responses

## Related Requirements
- **FR-4.1.1**: Maintain context throughout session
- **FR-4.1.2**: Remember discussed information
- **FR-4.1.3**: Reference previous elements naturally
- **FR-4.1.4**: Avoid repetition
- **FR-4.1.5**: Maintain conversation history (50 messages minimum)
- **FR-4.1.6**: Handle context switches

## Dependencies
- **Depends on**: US-001 (session management)
- **Blocks**: All conversation features (enhances all)

## Story Points
**Estimate**: 8 points

## Priority
**High** - Critical for natural conversation and user experience

## Implementation Status
- **Status**: ✅ Done
- **Implementation Notes**: 
  - `ContextManager` fully implemented
  - Session state management via Redis
  - Message history from database
  - Context window management (50 messages, 8000 tokens)
  - Context compression for long conversations
  - Customer profile preservation
  - Natural context references via LLM

---

## Implementation Considerations

- ✅ Conversation state data structure (`SessionState` in Redis)
- ✅ Context window management (sliding window, summarization)
- ✅ Conversation summarization (LLM-based compression)
- ✅ Key information extraction (profile, collected data, preferences)
- ✅ Context optimization for LLM token limits
- ✅ Efficient context storage and retrieval
