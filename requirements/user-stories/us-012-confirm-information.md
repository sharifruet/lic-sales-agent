# US-012: Confirm Information Before Saving

## User Story
As a **potential customer**
I want to **review and confirm my information before it's saved**
So that **I can ensure accuracy and have a chance to correct any mistakes**

## Acceptance Criteria

### AC-012.1: Information Summary
- Given all mandatory information is collected and validated
- Before saving to database
- Then the system presents a clear summary of all collected information:
  - Full Name
  - Phone Number
  - National ID
  - Address
  - Policy of Interest
  - Optional fields (email, preferred contact time, notes) if provided
- And summary is easy to read and understand

### AC-012.2: Confirmation Request
- Given information summary is presented
- When requesting confirmation
- Then the system clearly asks customer to confirm
- And confirmation question is simple (e.g., "Is this information correct?")
- And system waits for customer response

### AC-012.3: Confirmation Response Handling
- Given customer is asked to confirm
- When customer responds
- Then the system handles responses:
  - "Yes", "Correct", "That's right" → Proceed to save
  - "No", "That's wrong", specific corrections → Allow editing
  - Ambiguous response → Ask for clarification
- And system interprets responses accurately

### AC-012.4: Information Correction
- Given customer wants to correct information
- When customer indicates what's wrong
- Then the system:
  - Identifies which field needs correction
  - Asks for correct information
  - Validates new information
  - Re-confirms updated summary
- And correction process is smooth

### AC-012.5: Multiple Corrections
- Given customer needs to correct multiple fields
- When processing corrections
- Then the system handles corrections one at a time or all at once
- And system re-presents summary after corrections
- And system confirms again before saving

### AC-012.6: Final Confirmation
- Given customer has confirmed information (or corrected and re-confirmed)
- When ready to save
- Then the system confirms one final time
- And system proceeds to save only after final confirmation
- And system provides clear feedback that information is being saved

## Detailed Scenarios

### Scenario 1: Correct Information - Proceed
**Given**: All information collected  
**When**: System presents summary and asks confirmation  
**Then**: Customer confirms "Yes", system saves successfully

### Scenario 2: Incorrect Phone Number
**Given**: Summary shows wrong phone number  
**When**: Customer says "The phone number is wrong"  
**Then**: System asks for correct number, validates, updates summary, re-confirms

### Scenario 3: Partial Correction
**Given**: Summary shows multiple fields  
**When**: Customer corrects address only  
**Then**: System updates address, re-presents full summary, asks for confirmation again

### Scenario 4: Ambiguous Confirmation
**Given**: System asks "Is this correct?"  
**When**: Customer responds "Looks good"  
**Then**: System interprets as confirmation and proceeds to save

### Scenario 5: Customer Changes Mind
**Given**: System asks for confirmation  
**When**: Customer says "Actually, I'm not ready"  
**Then**: System acknowledges, asks if they want to continue later, handles gracefully

## Technical Notes

- Information summary generation from `SessionState.collected_data`
- Confirmation response interpretation via LLM intent detection
- Correction workflow via information collection stage
- Re-confirmation logic in conversation flow
- Save trigger only after explicit confirmation via lead creation endpoint

## API Implementation

**Current Implementation**:
- Information collection happens during conversation
- Lead creation via `POST /api/leads/` requires all fields
- Validation happens before save
- Confirmation can be handled via conversation flow

**Future Enhancement**:
- Explicit confirmation step in conversation flow
- Summary presentation before lead creation
- Correction workflow in conversation

**Implementation Details**:
- Information stored in `SessionState.collected_data` during collection
- Lead creation validates all fields before save
- Confirmation can be added as explicit conversation step
- LLM can handle confirmation responses

## Related Requirements
- **FR-6.4**: Confirm collected information with customer

## Dependencies
- **Depends on**: US-010, US-011
- **Blocks**: US-013 (save only after confirmation)

## Story Points
**Estimate**: 3 points

## Priority
**High** - Important for data accuracy and customer trust

## Implementation Status
- **Status**: ⚠️ Partially Implemented (Core collection works, confirmation step missing)
- **Current State**: 
  - ✅ Information collection implemented in `ConversationService._handle_information_collection()`
  - ✅ Data stored in `SessionState.collected_data` during collection
  - ✅ Validation implemented via `ValidationService` before save
  - ✅ Lead creation endpoint (`POST /api/leads/`) validates all fields
  - ⚠️ **Missing**: Explicit confirmation step before saving
  - ⚠️ **Missing**: Information summary generation and presentation
  - ⚠️ **Missing**: Confirmation response handling (yes/no/correction)
  - ⚠️ **Missing**: Correction workflow in conversation flow

- **Implementation Details**: 
  - **Information Collection**: `ConversationService._handle_information_collection()` uses LLM to guide collection
  - **Data Storage**: Information stored in `SessionState.collected_data` (FullName, PhoneNumber, Email, Address, PolicyOfInterest)
  - **Validation**: `ValidationService` validates phone, NID, email before save
  - **Lead Creation**: `POST /api/leads/` endpoint requires all mandatory fields and validates them
  - **Current Gap**: No explicit step to present summary and request confirmation before calling lead creation endpoint

- **Required Enhancements**:
  1. **Summary Generation Method**: Add `ConversationService._generate_information_summary(state: SessionState) -> str`:
     ```python
     def _generate_information_summary(self, state: SessionState) -> str:
         """Generate human-readable summary of collected information."""
         collected = state.collected_data
         summary = f"""Here's a summary of the information I've collected:
         
         Full Name: {collected.full_name or 'Not provided'}
         Phone Number: {collected.phone_number or 'Not provided'}
         Email: {collected.email or 'Not provided'}
         Address: {collected.address or 'Not provided'}
         Policy of Interest: {collected.policy_of_interest or 'Not provided'}
         
         Is this information correct?"""
         return summary
     ```

  2. **Confirmation Stage Detection**: Add logic to detect when all mandatory fields are collected and trigger confirmation:
     ```python
     def _should_show_confirmation(self, state: SessionState) -> bool:
         """Check if all mandatory fields are collected."""
         collected = state.collected_data
         return all([
             collected.full_name,
             collected.phone_number,
             collected.address,
             collected.policy_of_interest
         ])
     ```

  3. **Confirmation Response Handling**: Add method to interpret confirmation responses:
     ```python
     async def _handle_confirmation_response(
         self, 
         message: str, 
         state: SessionState
     ) -> Tuple[bool, Optional[str]]:
         """Interpret confirmation response. Returns (confirmed, field_to_correct)."""
         # Use LLM to detect intent: confirm, deny, or correction
         intent = await self.detect_intent(message, {})
         if intent == Intent.INTEREST:  # "Yes", "Correct", etc.
             return (True, None)
         elif intent == Intent.OBJECTION:  # "No", "Wrong", etc.
             # Extract which field needs correction
             field = await self._extract_correction_field(message)
             return (False, field)
         return (False, None)  # Ambiguous, ask for clarification
     ```

  4. **Confirmation Step in Flow**: Update `_handle_information_collection()` to:
     - Check if all mandatory fields collected
     - If yes, generate and present summary
     - Wait for confirmation response
     - Handle confirmation/correction
     - Only proceed to lead creation after confirmation

  5. **Correction Workflow**: Add logic to handle corrections:
     - Identify which field needs correction
     - Re-ask for that specific field
     - Validate new input
     - Re-present full summary
     - Re-request confirmation

---

## Implementation Considerations

- ✅ **Collection Works**: Information collection and validation are fully implemented
- ✅ **Data Storage**: `SessionState.collected_data` properly stores collected information
- ⚠️ **Confirmation Missing**: No explicit confirmation step before saving
- ⚠️ **Summary Missing**: No method to generate human-readable summary
- ⚠️ **Correction Missing**: No workflow to handle corrections
- 💡 **Recommendation**: Add confirmation step as part of `INFORMATION_COLLECTION` stage before transitioning to lead creation
- 💡 **Edge Cases**: Handle customer changing mind, ambiguous responses, multiple corrections
