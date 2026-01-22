# US-011: Validate Collected Data

## User Story
As a **system**
I want to **validate all collected customer information**
So that **I ensure data quality and prevent invalid or duplicate entries**

## Acceptance Criteria

### AC-011.1: Phone Number Validation
- Given customer provides phone number
- When validating
- Then the system validates:
  - Format matches country-specific patterns
  - Contains only digits and allowed characters (+, -, spaces)
  - Meets minimum/maximum length requirements
  - Includes country code if required
- And invalid formats are rejected with clear error message

### AC-011.2: NID Validation
- Given customer provides National ID
- When validating
- Then the system validates:
  - Format matches country-specific NID pattern
  - Contains correct number of characters/digits
  - Matches checksum/validation algorithm (if applicable)
- And invalid NIDs are rejected with format explanation

### AC-011.3: Email Validation
- Given customer provides email (if optional field collected)
- When validating
- Then the system validates:
  - Contains @ symbol
  - Has valid domain format
  - Follows email format standards (RFC 5322)
- And invalid emails are rejected with format example

### AC-011.4: Name Validation
- Given customer provides full name
- When validating
- Then the system validates:
  - Contains at least first and last name
  - Has reasonable length (not too short, not excessively long)
  - Contains only allowed characters (letters, spaces, hyphens, apostrophes)
- And invalid names are flagged for clarification

### AC-011.5: Address Validation
- Given customer provides address
- When validating
- Then the system validates:
  - Contains required components (street, city, postal code)
  - Has reasonable format and completeness
  - Postal code format matches country standards (if applicable)
- And incomplete addresses are requested for completion

### AC-011.6: Duplicate Detection
- Given customer information is collected
- When checking for duplicates
- Then the system checks:
  - Phone number matches existing lead
  - NID matches existing lead
- And duplicates are detected and flagged
- And system asks customer if they're a returning customer

### AC-011.7: Real-Time Validation
- Given customer provides information during collection
- When input is received
- Then validation occurs immediately
- And feedback is provided instantly
- And customer can correct before proceeding

### AC-011.8: Validation Error Messages
- Given validation fails
- When providing error message
- Then the system provides:
  - Clear explanation of what's wrong
  - Expected format or example
  - Helpful guidance for correction
- And messages are user-friendly, not technical

## Detailed Scenarios

### Scenario 1: Valid Phone Number
**Given**: Customer provides "+1-555-123-4567"  
**When**: System validates  
**Then**: Validation passes, system acknowledges and proceeds

### Scenario 2: Invalid Phone Format
**Given**: Customer provides "123"  
**When**: System validates  
**Then**: Validation fails, system explains: "Please provide a valid phone number with country code. Example: +1-555-123-4567"

### Scenario 3: Duplicate Phone Number
**Given**: Customer provides phone number that exists in database  
**When**: System checks  
**Then**: System detects duplicate, raises `LeadValidationError` with message about existing lead

### Scenario 4: Invalid NID Format
**Given**: Customer provides NID "ABC123" in country requiring 13 digits  
**When**: System validates  
**Then**: Validation fails, system explains expected format and length

### Scenario 5: Incomplete Address
**Given**: Customer provides only "New York"  
**When**: System validates  
**Then**: System requests: "I need your complete address including street address and postal code. Could you provide that?"

## Technical Notes

- Validation via `ValidationService` with methods for each field type
- Phone validation: format patterns, country code support, normalization
- NID validation: format patterns, length checks
- Email validation: RFC 5322 compliant
- Name validation: length and character checks
- Address validation: completeness checks
- Duplicate checking via `LeadRepository.find_by_phone()`
- Real-time validation during information collection

## API Implementation

**Endpoint**: `POST /api/leads/`

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

**Response (Success)**:
```json
{
  "id": 1,
  "message": "Lead created successfully"
}
```

**Response (Validation Error)**:
```json
{
  "detail": {
    "errors": [
      "Invalid phone number format",
      "NID must be 13 digits"
    ]
  }
}
```

**Implementation Details**:
- Validation via `ValidationService.validate_lead_data()`
- Returns `ValidationResult` with errors list
- `LeadService` raises `LeadValidationError` on validation failure
- Duplicate checking before creation
- Normalization of phone numbers
- Clear error messages returned to API

## Related Requirements
- **FR-8.1**: Phone number format validation
- **FR-8.2**: NID format validation
- **FR-8.3**: Email format validation
- **FR-8.4**: Duplicate entry checking
- **FR-6.2**: Validate before saving

## Dependencies
- **Depends on**: US-010 (data collection)
- **Blocks**: US-012, US-013 (must validate before confirming and saving)

## Story Points
**Estimate**: 5 points

## Priority
**High** - Essential for data quality

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `POST /api/leads/` (with validation)
- **Implementation Notes**: 
  - `ValidationService` fully implemented
  - Phone, email, NID validation
  - Duplicate detection
  - Clear error messages
  - Real-time validation during collection

---

## Implementation Considerations

- ✅ Validation schemas/rules for each field (`ValidationService`)
- ✅ Country-specific validation patterns (extensible)
- ✅ Validation service/module implemented
- ✅ Duplicate checking queries (phone number)
- ✅ User-friendly error messages
- ✅ Performance: efficient duplicate checks
