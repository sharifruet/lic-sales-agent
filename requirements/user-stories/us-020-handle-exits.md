# US-020: Handle Conversation Exits

## User Story
As a **potential customer**
I want to **end the conversation gracefully when I'm not interested**
So that **I don't feel pressured and can leave with a positive impression**

## Acceptance Criteria

### AC-020.1: Exit Signal Detection
- Given conversation is in progress
- When customer wants to exit
- Then the system detects exit signals:
  - Explicit rejection ("Not interested", "No thanks", "I'll pass")
  - Repeated objections that remain unresolved
  - Time-based disengagement (no response for extended period)
  - Clear statements of unwillingness ("I don't want insurance", "Not for me")
  - Requests to end conversation ("I have to go", "Thanks but no thanks")
- And signals are detected accurately

### AC-020.2: Graceful Exit Process
- Given exit signal is detected
- When customer wants to leave
- Then the system:
  - Acknowledges customer's decision respectfully
  - Thanks customer for their time
  - Offers to help in the future
  - Provides contact information for future reference (optional)
  - Does not push further or become aggressive
- And exit feels natural and respectful

### AC-020.3: Exit at Any Stage
- Given customer wants to exit
- When exiting
- Then the system handles exit appropriately regardless of stage:
  - Early in conversation (before qualifying)
  - During policy discussion
  - During objection handling
  - During information collection
- And appropriate exit message is provided for each stage

### AC-020.4: Conversation Log Preservation
- Given customer exits conversation
- When exiting
- Then the system:
  - Saves conversation log even if no lead was created
  - Records exit reason (if detectable)
  - Marks conversation as completed
  - Stores outcome (not interested, exited early, etc.)
- And log is accessible for analysis

### AC-020.5: No Judgment Language
- Given customer is exiting
- When system responds
- Then the system:
  - Uses respectful, non-judgmental language
  - Does not criticize customer's decision
  - Maintains professional tone
  - Leaves door open for future engagement
- And customer feels respected

### AC-020.6: Repeated Exit Attempts
- Given customer has indicated disinterest multiple times
- When system detects repeated signals
- Then the system:
  - Recognizes persistent lack of interest
  - Exits more quickly on repeated attempts
  - Does not continue pushing
- And system respects customer's clear decision

### AC-020.7: Partial Information Handling
- Given customer exits during information collection
- When exiting
- Then the system:
  - Acknowledges exit
  - Does not save partial lead information (unless business rule allows)
  - Offers to save progress if customer wants to return (optional feature)
- And partial data handling is clear

## Detailed Scenarios

### Scenario 1: Early Exit - Not Interested
**Given**: Customer says "I'm not interested in life insurance" after introduction  
**When**: System detects exit signal  
**Then**: System acknowledges, thanks for time, offers future help, exits gracefully, saves conversation log

### Scenario 2: Exit During Policy Discussion
**Given**: Customer has heard about policies but says "I'll think about it" repeatedly  
**When**: System detects persistent delay/exit intent  
**Then**: System acknowledges, offers to send information, provides contact, exits respectfully

### Scenario 3: Exit During Information Collection
**Given**: System is collecting customer information  
**When**: Customer says "Actually, I'm not ready"  
**Then**: System acknowledges, asks if they want to continue later, doesn't save partial data, exits gracefully

### Scenario 4: Time-Based Disengagement
**Given**: Customer hasn't responded for 15 minutes  
**When**: System detects inactivity  
**Then**: System sends gentle follow-up, if no response, sends closing message, exits, saves conversation

### Scenario 5: Explicit Exit Request
**Given**: Customer says "I have to go, thanks"  
**When**: System detects exit  
**Then**: System acknowledges, thanks customer, provides contact info, exits immediately without push

## Technical Notes

- Exit signal detection via `_is_exit_signal()` method
- Exit intent classification via `Intent.EXIT`
- Exit handling via `_handle_exit()` method
- Exit message templates in `PromptManager.EXIT_TEMPLATES`
- Conversation state updated to `ENDED` stage
- Conversation summary generated at exit
- Conversation log saved regardless of outcome

## API Implementation

**Endpoint**: `POST /api/conversation/end`

**Request**:
```json
{
  "session_id": "abc123...",
  "reason": "customer_requested"  // Optional
}
```

**Response**:
```json
{
  "session_id": "abc123...",
  "conversation_id": "def456...",
  "status": "ended",
  "summary": "Customer was not interested in life insurance...",
  "duration_seconds": 420
}
```

**Automatic Exit Detection**:
- Exit signals detected during `process_message()`
- Automatic exit handling when exit intent detected
- Conversation ended gracefully with summary

**Implementation Details**:
- Exit detection via keyword matching and intent classification
- Exit handling via `_handle_exit()` method
- Exit templates for different exit types
- Conversation summary generation
- Session state updated to `ENDED`
- Conversation log preserved

## Related Requirements
- **FR-4.4.1**: Recognize exit signals
- **FR-4.4.2**: Exit gracefully
- **FR-4.4.3**: Save conversation log
- **FR-4.4.4**: Handle exits at any stage
- **FR-4.4.5**: Respectful language

## Dependencies
- **Depends on**: US-001 (conversation session)
- **Blocks**: None (standalone feature but important for UX)

## Story Points
**Estimate**: 5 points

## Priority
**High** - Critical for customer experience and brand reputation

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `POST /api/conversation/end`
- **Implementation Notes**: 
  - Exit signal detection implemented
  - Exit handling via `_handle_exit()` method
  - Exit templates in `PromptManager`
  - Conversation summary generation
  - Graceful exit at any stage
  - Conversation log preservation

---

## Implementation Considerations

- ✅ Exit signal detection (keywords, intent classification)
- ✅ Exit message templates for different exit types (`PromptManager.EXIT_TEMPLATES`)
- ✅ Timeout detection (can be added via session TTL)
- ✅ Conversation state handling for exit (`ConversationStage.ENDED`)
- ✅ Conversation logs saved even without leads
- ✅ Balance between graceful exit and conversion opportunity
