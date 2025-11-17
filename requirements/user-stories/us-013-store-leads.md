# US-013: Store Lead Information

## User Story
As a **system**
I want to **store collected lead information persistently**
So that **leads can be retrieved, managed, and assigned to sales team**

## Acceptance Criteria

### AC-013.1: Database Storage
- Given customer information is confirmed
- When saving lead
- Then the system stores information in database with:
  - Full Name
  - Phone Number (encrypted)
  - National ID (encrypted)
  - Address
  - Policy of Interest
  - Email (if provided)
  - Preferred contact time (if provided)
  - Notes/comments (if provided)
  - Conversation ID (link to conversation log)
  - Timestamp (created_at, updated_at)
  - Status (new, contacted, converted, not_interested)
- And all mandatory fields are stored

### AC-013.2: File Storage (Phase 1)
- Given lead information is saved
- When storing
- Then the system also stores in daily JSON files:
  - Format: JSON
  - One file per day: `leads_YYYY-MM-DD.json`
  - Includes all lead fields
  - Includes headers and structure
- And JSON file format is readable and importable

### AC-013.3: Data Persistence
- Given lead is saved
- When system restarts or encounters error
- Then lead information is not lost
- And data is persisted to durable storage (PostgreSQL)
- And system recovers gracefully

### AC-013.4: Timestamp Recording
- Given lead is created or updated
- When storing
- Then the system records:
  - created_at: When lead was first created
  - updated_at: When lead was last modified
- And timestamps are accurate and timezone-aware

### AC-013.5: Conversation Linkage
- Given lead is saved
- When storing
- Then the system links lead to conversation:
  - Conversation ID can be stored in lead record
  - Link enables retrieval of full conversation transcript
- And linkage is bidirectional (can find lead from conversation, conversation from lead)

### AC-013.6: Status Management
- Given lead is created
- When storing
- Then the system sets initial status to "new"
- And status can be updated later (by admin or system)
- And status changes are tracked

### AC-013.7: Save Confirmation
- Given lead is saved successfully
- When save completes
- Then the system provides confirmation to customer
- And customer receives clear message about next steps
- And system thanks customer for their interest

### AC-013.8: Data Encryption
- Given sensitive information (phone, NID)
- When storing
- Then the system encrypts sensitive fields using Fernet encryption
- And encryption key is secure and managed properly
- And data can be decrypted for authorized access only

## Detailed Scenarios

### Scenario 1: Successful Database Save
**Given**: All information confirmed  
**When**: System saves to database  
**Then**: Record created with all fields, timestamps set, status="new", conversation_id linked, customer receives confirmation

### Scenario 2: File Storage (Phase 1)
**Given**: System configured for file storage  
**When**: Lead is saved  
**Then**: Information appended to daily JSON file with proper format, all fields included, file is readable

### Scenario 3: Save Failure Handling
**Given**: Database connection fails during save  
**When**: Save attempt fails  
**Then**: System retries (with backoff), logs error, notifies customer of delay, ensures eventual persistence

### Scenario 4: Duplicate Prevention
**Given**: Customer information matches existing lead  
**When**: System attempts save  
**Then**: System detects duplicate, raises error with message, prevents duplicate creation

### Scenario 5: Encryption Verification
**Given**: Lead with sensitive data is saved  
**When**: Admin views lead  
**Then**: System decrypts data for authorized admin, masks data for unauthorized users, maintains security

## Technical Notes

- Database schema: `Lead` model with SQLAlchemy
- File storage: `FileStorageService` for daily JSON files
- Encryption: `EncryptionService` using Fernet (cryptography library)
- Validation: `ValidationService` before storage
- Duplicate detection: Phone number and NID checking
- Transaction handling for data consistency
- Backup and recovery procedures (database-level)

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

**Response**:
```json
{
  "id": 1,
  "message": "Lead created successfully"
}
```

**Implementation Details**:
- `LeadService.create_lead()` handles creation
- Validation via `ValidationService`
- Encryption via `EncryptionService` (phone, NID)
- Duplicate checking by phone number
- Database storage via `LeadRepository`
- File storage via `FileStorageService` (async, fire-and-forget)
- Error handling with `LeadValidationError`

## Related Requirements
- **FR-7.1**: Store in database
- **FR-7.2**: Support text file storage
- **FR-7.4**: Timestamp all records
- **FR-7.5**: Ensure data persistence
- **NFR-10**: Encrypt sensitive data

## Dependencies
- **Depends on**: US-010 (information collection), US-011 (validation)
- **Blocks**: US-016, US-017 (viewing leads and conversations)

## Story Points
**Estimate**: 8 points

## Priority
**High** - Core functionality for lead management

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `POST /api/leads/`
- **Implementation Notes**: 
  - Database storage fully implemented (PostgreSQL)
  - File storage implemented (daily JSON files)
  - Encryption for sensitive data (phone, NID)
  - Validation before storage
  - Duplicate detection
  - Error handling and logging
  - Timestamp recording

---

## Implementation Considerations

- ✅ Database schema designed and implemented (`Lead` model)
- ✅ Encryption for PII (NID, phone) using Fernet
- ✅ Text file format (JSON) for daily storage
- ✅ Save retry logic (can be added via middleware)
- ✅ Backup strategy (database-level)
- ✅ Proper error handling and logging
- ✅ Duplicate prevention
