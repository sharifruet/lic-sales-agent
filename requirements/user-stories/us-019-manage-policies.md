# US-019: Manage Policy Information

## User Story
As an **admin**
I want to **manage policy information in the system**
So that **I can keep policy details up-to-date and add new policies**

## Acceptance Criteria

### AC-019.1: View Policies
- Given admin accesses policy management
- When viewing policies
- Then the system displays list of all policies:
  - Policy name
  - Provider/Company
  - Coverage range
  - Premium range
  - Term years
  - Medical exam required
  - Last updated date
- And list is sortable and searchable

### AC-019.2: View Policy Details
- Given admin selects a policy
- When viewing details
- Then the system displays complete policy information:
  - Policy name and provider
  - Coverage amount range (min, max)
  - Premium range (monthly)
  - Term years
  - Medical examination requirements
  - Created date, updated date
- And information is clearly formatted

### AC-019.3: Create New Policy
- Given admin wants to add new policy
- When creating policy
- Then the system allows entering:
  - Policy name (required)
  - Provider/Company (required)
  - Coverage amount (required, min 10000)
  - Monthly premium (required, > 0)
  - Term years (required, >= 1)
  - Medical exam required (boolean, default false)
- And system validates required fields
- And policy is saved to database

### AC-019.4: Update Policy Information
- Given admin views policy details
- When updating information
- Then the system allows editing all policy fields
- And system validates changes
- And updated_at timestamp is updated
- And change history is logged (optional)

### AC-019.5: Delete/Deactivate Policy
- Given admin wants to remove policy
- When deleting/deactivating
- Then the system:
  - Allows deactivating policy (sets status to inactive)
  - Prevents deletion if policy is referenced by leads
  - Shows warning if policy has active references
  - Optionally allows soft delete (archive)
- And system handles references gracefully

### AC-019.6: Policy Validation
- Given admin creates or updates policy
- When saving
- Then the system validates:
  - Required fields are present
  - Coverage amount is valid (>= 10000)
  - Premium is valid (> 0)
  - Term years is valid (>= 1)
  - Data types are correct
- And validation errors are clearly displayed

### AC-019.7: Search and Filter Policies
- Given admin views policy list
- When searching or filtering
- Then the system allows:
  - Search by name (can be added)
  - Filter by provider (can be added)
  - Filter by type (can be added)
- And filters can be combined

### AC-019.8: Access Control
- Given policy management is accessed
- When performing operations
- Then the system enforces access control:
  - Authentication required (can be added for create/update)
  - Admin role required (can be added)
  - Actions are logged (can be added)
- And unauthorized access is prevented

## Detailed Scenarios

### Scenario 1: Add New Company Policy
**Given**: Admin accesses policy management  
**When**: Creates new term life policy with all details  
**Then**: System validates, saves to database, policy becomes available for AI agent to present

### Scenario 2: Update Premium Range
**Given**: Policy premium rates have changed  
**When**: Admin updates premium range  
**Then**: System saves update, updates timestamp, change is immediately available in conversations

### Scenario 3: Deactivate Competitor Policy
**Given**: Competitor policy is no longer relevant  
**When**: Admin deactivates policy  
**Then**: System sets status to inactive, policy no longer shown to customers, existing references preserved

### Scenario 4: Delete Policy with Active Leads
**Given**: Admin tries to delete policy  
**When**: Policy has leads referencing it  
**Then**: System warns about active references, prevents deletion, suggests deactivation instead

## Technical Notes

- Policy CRUD API via `PolicyService` and `PolicyRepository`
- Policy database schema (`Policy` model)
- Validation via Pydantic models (`PolicyCreate`)
- Reference checking (can be added for leads using policy)
- Soft delete vs hard delete logic (can be added)
- Access control and logging (can be added)

## API Implementation

**Endpoint**: `GET /api/policies/` (public)

**Response**:
```json
[
  {
    "id": 1,
    "name": "Term Life 20-Year",
    "provider": "Life Insurance Company",
    "coverage_amount": 500000,
    "monthly_premium": 50.00,
    "term_years": 20,
    "medical_exam_required": false
  }
]
```

**Endpoint**: `GET /api/policies/{policy_id}` (public)

**Endpoint**: `POST /api/policies/` (create - admin auth can be added)

**Request**:
```json
{
  "name": "Term Life 20-Year",
  "provider": "Life Insurance Company",
  "coverage_amount": 500000,
  "monthly_premium": 50.00,
  "term_years": 20,
  "medical_exam_required": false
}
```

**Implementation Details**:
- Policy CRUD via `PolicyService`
- Validation via Pydantic models
- Database storage via `PolicyRepository`
- Policies available for conversation context
- Admin authentication can be added for create/update

## Related Requirements
- **FR-9.1**: Maintain company policy database
- **FR-9.2**: Maintain competitor policy database
- **FR-9.3**: Include policy details
- **FR-9.4**: Allow policy updates

## Dependencies
- **Depends on**: None (standalone admin feature, but foundational for US-004)
- **Blocks**: US-004 (policies must exist to be presented)

## Story Points
**Estimate**: 8 points

## Priority
**High** - Foundational for policy presentation features

## Implementation Status
- **Status**: ✅ Done
- **API Endpoints**: 
  - `GET /api/policies/` - List all policies
  - `GET /api/policies/{id}` - Get policy details
  - `POST /api/policies/` - Create policy
- **Implementation Notes**: 
  - Policy CRUD operations implemented
  - Validation via Pydantic
  - Database storage
  - Policies integrated into conversation context
  - Admin authentication can be added (future enhancement)

---

## Implementation Considerations

- ✅ Policy database schema designed and implemented (`Policy` model)
- ✅ CRUD operations with proper validation (`PolicyService`)
- ✅ Policy data available for conversations
- ✅ Reference checking (can be added before deletion)
- ✅ Caching strategy (can be added for performance)
- ✅ Admin authentication (can be added for create/update)
