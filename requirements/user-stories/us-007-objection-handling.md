# US-007: Handle Customer Objections

## User Story
As an **AI insurance agent**
I want to **address customer objections effectively**
So that **I can overcome concerns and help customers see the value of life insurance**

## Acceptance Criteria

### AC-007.1: Objection Detection
- Given a conversation is in progress
- When customer raises objections
- Then the system detects common objection types:
  - Cost objections ("too expensive", "can't afford")
  - Necessity objections ("don't need it", "young and healthy")
  - Complexity objections ("too complicated", "don't understand")
  - Trust objections ("is this legitimate?", "how can I trust?")
  - Timing objections ("I'll think about it", "maybe later")
  - Comparison objections ("Company X has better rates")
- And the system identifies objection type accurately

### AC-007.2: Cost Objection Handling
- Given customer raises cost concern
- When responding to cost objection
- Then the system:
  - Acknowledges concern empathetically
  - Breaks down costs into manageable perspectives (daily/monthly, cost per year)
  - Highlights value proposition and ROI
  - Offers lower coverage options or payment plans
  - Emphasizes long-term financial security benefits
- And the system doesn't minimize the concern

### AC-007.3: Necessity Objection Handling
- Given customer says they don't need insurance
- When responding
- Then the system:
  - Uses statistics and facts about unexpected events
  - Highlights family/dependent protection needs
  - Explains risks of being uninsured
  - References age and health considerations
- And the system provides factual, not fear-based, information

### AC-007.4: Complexity Objection Handling
- Given customer says it's too complicated
- When responding
- Then the system:
  - Simplifies explanations further
  - Offers to guide step-by-step
  - Provides analogies or simple examples
  - Reassures that process will be made simple
- And the system maintains patience

### AC-007.5: Trust Objection Handling
- Given customer expresses trust concerns
- When responding
- Then the system:
  - Provides company credentials and legitimacy information
  - Offers transparency about process
  - Suggests speaking with human agent if preferred
  - Provides testimonials or reviews (if available and verified)
- And the system builds trust without being defensive

### AC-007.6: Timing Objection Handling
- Given customer wants to delay decision
- When responding
- Then the system:
  - Creates appropriate urgency (age-related premium increases)
  - Addresses "what if" scenarios (health changes, unavailability)
  - Offers to send information for later review
  - Proposes next steps without pressure
- And the system balances urgency with respect

### AC-007.7: Comparison Objection Handling
- Given customer mentions better competitor offers
- When responding
- Then the system:
  - Acknowledges competitor offerings
  - Compares fairly and highlights company advantages
  - Addresses specific concern (rates, coverage, service)
  - Focuses on overall value proposition
- And the system maintains professionalism

### AC-007.8: Objection Resolution Attempt
- Given an objection has been raised
- When addressing the objection
- Then the system attempts to resolve with empathy and facts
- And the system doesn't push aggressively
- And the system recognizes when customer is not persuadable
- And the system transitions gracefully if needed

## Detailed Scenarios

### Scenario 1: Cost Objection - Affordability Concern
**Given**: Customer says "It's too expensive"  
**When**: System responds  
**Then**: System acknowledges, breaks down $50/month to $1.67/day, explains protection value, offers lower coverage option, emphasizes financial security

### Scenario 2: Necessity Objection - Young and Healthy
**Given**: Customer says "I'm 28 and healthy, I don't need this"  
**When**: System responds  
**Then**: System provides statistics on unexpected events for young adults, explains locking in lower rates now, discusses family/future planning, uses facts not fear

### Scenario 3: Complexity Objection
**Given**: Customer says "This is too complicated"  
**When**: System responds  
**Then**: System simplifies explanation, offers step-by-step guide, uses simple analogy, reassures about process simplicity

### Scenario 4: Repeated Objections
**Given**: Customer raises same objection multiple times  
**When**: System has addressed it already  
**Then**: System acknowledges previous discussion, offers alternative approach or information, recognizes if customer may not be ready, transitions gracefully

### Scenario 5: Trust Objection
**Given**: Customer asks "How do I know this is legitimate?"  
**When**: System responds  
**Then**: System provides company credentials, offers to connect with human agent, shares verified reviews/testimonials, explains process transparency

## Technical Notes

- Objection detection implemented using keyword matching and LLM-based classification
- Objection type classification: cost, necessity, complexity, trust, timing, comparison
- Response templates for each objection type in `PromptManager`
- Context-aware objection handling (tracks previous objections)
- Natural language generation for empathetic responses using LLM
- Stage transition to `OBJECTION_HANDLING` when objection detected

## API Implementation

**Endpoint**: `POST /api/conversation/message`

**Request**:
```json
{
  "session_id": "abc123...",
  "message": "It's too expensive"
}
```

**Response**:
```json
{
  "session_id": "abc123...",
  "response": "I completely understand that cost is important...",
  "interest_detected": "low",
  "conversation_stage": "objection_handling",
  "metadata": {
    "message_count": 5,
    "extracted_data": {}
  }
}
```

**Implementation Details**:
- Objection detection via `_detect_objection_type()` method
- Uses `PromptManager.get_objection_response()` for template-based responses
- Falls back to LLM generation for custom objections
- Updates conversation stage to `OBJECTION_HANDLING`
- Integrates with conversation flow seamlessly

## Related Requirements
- **FR-3.2.1**: Detect common objections
- **FR-3.2.2**: Cost objection handling
- **FR-3.2.3**: Necessity objection handling
- **FR-3.2.4**: Complexity objection handling
- **FR-3.2.5**: Trust objection handling
- **FR-3.2.6**: Timing objection handling
- **FR-3.2.7**: Attempt resolution with empathy
- **FR-3.2.8**: Recognize when not persuadable

## Dependencies
- **Depends on**: US-002, US-004
- **Blocks**: US-009 (detect interest - objections resolved may indicate readiness)

## Story Points
**Estimate**: 10 points (complex NLP and multiple scenarios)

## Priority
**High** - Critical for conversion and sales success

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `POST /api/conversation/message` (with objection detection)
- **Implementation Notes**: 
  - Objection detection via keyword matching and LLM classification
  - Template-based responses for common objections
  - LLM fallback for custom objections
  - Stage-based handling in conversation flow
  - Empathetic response generation

---

## Implementation Considerations

- ✅ Objection detection using keyword matching and LLM classification
- ✅ Response templates/rules for each objection type (`PromptManager`)
- ✅ Objection tracking (conversation stage management)
- ✅ Escalation paths (graceful exit handling)
- ✅ Balance between being persuasive and respecting customer's position
- A/B testing may be valuable for objection handling strategies (future enhancement)
