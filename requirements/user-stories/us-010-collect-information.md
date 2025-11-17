# US-010: Collect Customer Information

## User Story
As an **AI insurance agent**
I want to **collect customer information from interested prospects**
So that **I can register them as leads for the sales team to follow up**

## Acceptance Criteria

### AC-010.1: Mandatory Information Collection
- Given customer has shown interest
- When collecting information
- Then the system collects the following mandatory fields:
  - Full Name
  - Phone Number
  - National ID (NID)
  - Address (complete address)
  - Policy of Interest (specific policy name/ID)
- And all mandatory fields are collected before submission

### AC-010.2: Optional Information Collection
- Given mandatory information is being collected
- When system requests information
- Then the system may also collect optional information:
  - Email address
  - Preferred contact time
  - Additional notes/comments
- And optional fields don't block submission

### AC-010.3: Sequential Information Gathering
- Given system is collecting information
- When requesting each piece of information
- Then the system asks for one piece at a time
- And the system waits for response before asking next
- And the system confirms each piece before moving forward

### AC-010.4: Information Explanation
- Given system needs to ask for information
- When requesting each field
- Then the system explains why the information is needed
- And explanations are brief and reassuring
- And system addresses privacy concerns

### AC-010.5: Validation During Collection
- Given customer provides information
- When system receives input
- Then the system validates format immediately
- And the system asks for correction if invalid
- And the system provides helpful error messages

### AC-010.6: Information Confirmation
- Given all mandatory information is collected
- Before saving to database
- Then the system confirms all collected information with customer
- And customer can review and correct if needed
- And confirmation is clear and easy to understand

### AC-010.7: Missing Information Handling
- Given customer skips or provides incomplete information
- When system detects missing mandatory data
- Then the system politely asks for missing information
- And the system explains why it's needed
- And the system doesn't proceed until all mandatory data is collected

## Detailed Scenarios

### Scenario 1: Complete Information Collection
**Given**: Customer has shown interest  
**When**: System collects information  
**Then**: System asks for each field sequentially, validates each, confirms all at end, saves successfully

### Scenario 2: Invalid Phone Number
**Given**: Customer provides phone number "123"  
**When**: System validates  
**Then**: System detects invalid format, explains expected format (e.g., country code + number), asks for correction

### Scenario 3: Partial Address
**Given**: Customer provides only city name  
**When**: System requests address  
**Then**: System asks for complete address (street, city, postal code), explains why needed, validates completeness

### Scenario 4: Information Confirmation
**Given**: All information collected  
**When**: System confirms  
**Then**: System displays: "Let me confirm: Name: John Doe, Phone: +1234567890, Policy: Term Life 20yr... Is this correct?"
- Customer can say "yes" or request changes

### Scenario 5: Customer Changes Mind Mid-Collection
**Given**: System is collecting information  
**When**: Customer says "Actually, I'm not ready"  
**Then**: System acknowledges, asks if they want to continue later, offers to save progress (if partial data acceptable) or exits gracefully

## Technical Notes

- Information collection via `INFORMATION_COLLECTION` conversation stage
- Entity extraction using `InformationExtractionService` (LLM-based with regex fallback)
- Data stored in `SessionState.collected_data` and `SessionState.customer_profile`
- Validation via `ValidationService` for phone, email, NID
- Encryption via `EncryptionService` for sensitive data (phone, NID)
- Lead creation via `LeadService` when collection complete

## API Implementation

**Endpoint**: `POST /api/conversation/message`

**Request**:
```json
{
  "session_id": "abc123...",
  "message": "My name is John Doe and my phone is +1234567890"
}
```

**Response**:
```json
{
  "session_id": "abc123...",
  "response": "Great! I have your name and phone. Now I'll need your address...",
  "interest_detected": "high",
  "conversation_stage": "information_collection",
  "metadata": {
    "message_count": 10,
    "extracted_data": {
      "name": "John Doe",
      "phone": "+1234567890"
    }
  }
}
```

**Lead Creation Endpoint**: `POST /api/leads/`

**Request**:
```json
{
  "name": "John Doe",
  "phone": "+1234567890",
  "nid": "123456789",
  "address": "123 Main St, City, Country",
  "interested_policy": "Term Life 20-Year",
  "email": "john@example.com"
}
```

**Implementation Details**:
- Information extraction from natural language
- Validation of phone, email, NID formats
- Encryption of sensitive data before storage
- Sequential collection guided by LLM
- Data stored in session state
- Lead creation when collection complete

## Related Requirements
- **FR-6.1**: Mandatory information list
- **FR-6.2**: Validate before saving
- **FR-6.3**: Ask for missing information
- **FR-6.4**: Confirm information
- **FR-6.5**: Optional information
- **FR-8.1**: Phone number validation
- **FR-8.2**: NID validation
- **FR-8.3**: Email validation

## Dependencies
- **Depends on**: US-009 (interest detection), US-004 (policy selection)
- **Blocks**: US-011, US-012, US-013

## Story Points
**Estimate**: 10 points (complex state management and validation)

## Priority
**High** - Core functionality for lead generation

## Implementation Status
- **Status**: ✅ Done
- **API Endpoints**: 
  - `POST /api/conversation/message` (information collection)
  - `POST /api/leads/` (lead creation)
- **Implementation Notes**: 
  - Information collection stage fully implemented
  - Entity extraction via LLM and regex
  - Validation service for all fields
  - Encryption service for sensitive data
  - Sequential collection with LLM guidance
  - Lead service for final storage

---

## Implementation Considerations

- ✅ Information collection workflow/state machine implemented
- ✅ Field-by-field validation via `ValidationService`
- ✅ Natural language extraction for structured data (`InformationExtractionService`)
- ✅ Validation patterns for each field type
- ✅ Encryption for sensitive data (`EncryptionService`)
- ✅ Lead creation with validation and encryption
- ✅ Error handling for invalid data
