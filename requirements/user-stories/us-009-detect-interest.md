# US-009: Detect Customer Interest

## User Story
As an **AI insurance agent**
I want to **detect when a customer shows buying interest**
So that **I can transition to information collection and close the sale**

## Acceptance Criteria

### AC-009.1: Positive Signal Detection
- Given a conversation is in progress
- When customer shows interest signals
- Then the system identifies positive signals such as:
  - Explicit interest statements ("I'm interested", "That sounds good", "I want to apply")
  - Questions about next steps ("What do I need to do?", "How do I sign up?")
  - Policy selection ("I'll go with the term life policy")
  - Affirmative responses to closing questions
  - Requests for registration or application process
- And signals are detected accurately

### AC-009.2: Buying Intent Detection
- Given conversation includes policy discussion
- When analyzing conversation
- Then the system detects buying intent through:
  - Sentiment analysis (positive sentiment toward policies)
  - Question pattern analysis (shifting from "what is" to "how do I")
  - Engagement level (asking detailed questions about specific policy)
  - Commitment language ("I'll take", "I'm ready", "let's do this")
- And intent detection is reliable

### AC-009.3: Distinguish Interest Levels
- Given various customer responses
- When evaluating interest
- Then the system distinguishes between:
  - NONE: No interest detected
  - LOW: Some interest, gathering information
  - MEDIUM: Interested, considering options
  - HIGH: Ready to proceed, strong buying intent
- And system adapts approach based on interest level

### AC-009.4: Transition to Data Collection
- Given buying interest is detected (MEDIUM or HIGH)
- When system responds
- Then the system transitions smoothly from information-sharing to data collection
- And the system confirms readiness before starting data collection
- And transition feels natural, not abrupt

### AC-009.5: False Positive Handling
- Given system detects interest signal
- When customer actually isn't ready
- Then the system gracefully handles the situation
- And the system doesn't push if customer clarifies they're not ready
- And the system returns to information-sharing mode

## Detailed Scenarios

### Scenario 1: Explicit Interest Statement
**Given**: Customer says "I'm interested in the term life policy"  
**When**: System detects this  
**Then**: System acknowledges interest, confirms policy selection, transitions to "Great! To get started, I'll need some information..."

### Scenario 2: Next Steps Question
**Given**: Customer asks "What do I need to do to get this?"  
**When**: System detects buying intent  
**Then**: System recognizes this as strong buying signal, explains next steps, begins information collection

### Scenario 3: Policy Selection
**Given**: Customer says "I'll go with option A"  
**When**: System detects selection  
**Then**: System confirms selection, highlights benefits of chosen policy, transitions to registration

### Scenario 4: Gradual Interest Building
**Given**: Customer asks increasingly specific questions about policy  
**When**: System analyzes conversation pattern  
**Then**: System detects growing interest, may test with soft close, prepares for transition

### Scenario 5: False Positive - Not Ready
**Given**: System detects interest and starts data collection  
**When**: Customer says "Wait, I'm not ready yet"  
**Then**: System acknowledges, asks what additional information is needed, returns to information mode without pressure

## Technical Notes

- Interest detection via `detect_interest()` method in `ConversationService`
- Scoring algorithm based on conversation state and collected data
- Interest levels: NONE, LOW, MEDIUM, HIGH
- Integration with conversation stage management
- Automatic transition to INFORMATION_COLLECTION stage when interest is HIGH or MEDIUM

## API Implementation

**Endpoint**: `POST /api/conversation/message`

**Request**:
```json
{
  "session_id": "abc123...",
  "message": "I'm interested in that policy"
}
```

**Response**:
```json
{
  "session_id": "abc123...",
  "response": "Great! I'd be happy to help you get started...",
  "interest_detected": "high",
  "conversation_stage": "information_collection",
  "metadata": {
    "message_count": 8,
    "extracted_data": {}
  }
}
```

**Implementation Details**:
- Interest detection via `detect_interest()` method
- Scoring based on:
  - Policy selection (score +5)
  - Information collection started (score +3)
  - Conversation stage (score +2 to +5)
- Automatic stage transition when interest is HIGH or MEDIUM
- Interest level included in response metadata

## Related Requirements
- **FR-5.1**: Identify positive signals
- **FR-5.2**: Detect buying intent
- **FR-5.3**: Distinguish informational vs serious prospects
- **FR-4.3.1**: Detect readiness signals
- **FR-4.3.2**: Use sentiment analysis

## Dependencies
- **Depends on**: US-004, US-007 (need policy discussion and objection handling before interest detection)
- **Blocks**: US-010 (information collection)

## Story Points
**Estimate**: 8 points

## Priority
**High** - Critical for conversion and sales process

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `POST /api/conversation/message` (with interest detection)
- **Implementation Notes**: 
  - Interest detection algorithm implemented
  - Four-level interest classification (NONE, LOW, MEDIUM, HIGH)
  - Automatic stage transition based on interest
  - Interest level included in API response
  - Scoring based on conversation state and collected data

---

## Implementation Considerations

- ✅ Interest detection using conversation state analysis
- ✅ Scoring mechanism based on multiple factors
- ✅ Automatic transition logic between conversation stages
- ✅ Balance between being proactive and respecting customer pace
- ✅ False positive handling with graceful fallback
