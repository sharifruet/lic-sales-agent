# US-028: Update Lead Status

## User Story
As an **admin/sales manager**
I want to **update the status of leads**
So that **I can track lead progression through the sales pipeline and manage follow-ups**

## Acceptance Criteria

### AC-028.1: Status Update Capability
- Given admin views a lead
- When updating lead status
- Then the system allows changing status to:
  - `new` → `contacted` (when sales team first contacts lead)
  - `contacted` → `converted` (when lead becomes a customer)
  - `contacted` → `not_interested` (when lead declines)
  - Any status can be updated to any other status (flexibility)
- And status change is saved immediately

### AC-028.2: Status Update Interface
- Given admin wants to update status
- When accessing update functionality
- Then the system provides:
  - Dropdown/select menu with all available statuses
  - Clear status descriptions (tooltips or labels)
  - Current status is highlighted
  - Confirmation before saving (optional)
- And interface is intuitive and quick to use

### AC-028.3: Status Change Logging
- Given admin updates lead status
- When status is changed
- Then the system logs:
  - Previous status
  - New status
  - Timestamp of change
  - User/admin who made the change
  - Optional notes/reason for change
- And log is stored for audit trail

### AC-028.4: Bulk Status Updates
- Given admin needs to update multiple leads
- When selecting multiple leads
- Then the system allows bulk status update:
  - Select multiple leads (checkbox selection)
  - Choose new status for all selected
  - Confirm bulk action
  - All selected leads updated to new status
- And each change is logged individually

### AC-028.5: Status-Based Filtering
- Given leads have different statuses
- When viewing lead list
- Then the system allows filtering by status:
  - Filter by single status (e.g., only "new" leads)
  - Filter by multiple statuses (e.g., "new" and "contacted")
  - Quick filter buttons for common statuses
- And filtered view updates immediately

### AC-028.6: Status Validation
- Given admin attempts to update status
- When providing invalid status value
- Then the system:
  - Validates status is one of allowed values
  - Shows error message if invalid
  - Prevents saving invalid status
- And provides helpful error message

### AC-028.7: Status Change Notifications (Future)
- Given lead status is updated
- When status changes to specific values (future feature)
- Then the system can send notifications:
  - Email to assigned sales agent (if assigned)
  - Notification in admin dashboard
  - Optional SMS notification
- And notifications are configurable

## Detailed Scenarios

### Scenario 1: Single Lead Status Update
**Given**: Admin views lead with status "new"  
**When**: Admin changes status to "contacted"  
**Then**: Status updates immediately, change is logged with timestamp and admin user, lead appears in "contacted" filter

### Scenario 2: Bulk Status Update
**Given**: Admin has 10 leads with status "new"  
**When**: Admin selects all 10, chooses "contacted", confirms  
**Then**: All 10 leads updated to "contacted", each change logged separately, leads move to "contacted" filter view

### Scenario 3: Status Change with Notes
**Given**: Admin updates lead status  
**When**: Admin changes status and adds note "Customer requested callback next week"  
**Then**: Status updated, note saved, both appear in lead detail view and audit log

### Scenario 4: Invalid Status Attempt
**Given**: Admin tries to set status to "invalid_status"  
**When**: Admin attempts to save  
**Then**: System shows error "Invalid status. Allowed values: new, contacted, converted, not_interested", status not changed

## Technical Notes

- Status values: `new`, `contacted`, `converted`, `not_interested`
- Status stored in `Lead.status` field (enum or string)
- Status changes logged in audit log or status_history table
- API endpoint: `PUT /api/leads/{lead_id}` with `status` field
- Bulk update endpoint: `PUT /api/leads/bulk-update` with array of lead IDs and status
- Validation: Status must be one of allowed enum values
- Authorization: Only admin users can update status

## API Implementation

**Current Implementation**:
- Lead model has status field (needs to be added if not present)
- `PUT /api/leads/{lead_id}` endpoint can accept status updates
- Status validation in `LeadService.update_lead()`

**Required Implementation**:
- Add `status` field to `Lead` model if not present
- Implement status update logic in `LeadService`
- Add status change logging (audit log)
- Add bulk update endpoint
- Add status filtering to lead list endpoint

**API Endpoint**: `PUT /api/leads/{lead_id}`

**Request**:
```json
{
  "status": "contacted",
  "notes": "Called customer, scheduled follow-up call"
}
```

**Response**:
```json
{
  "id": 123,
  "status": "contacted",
  "updated_at": "2024-01-15T10:30:00Z",
  "status_history": [
    {
      "previous_status": "new",
      "new_status": "contacted",
      "changed_at": "2024-01-15T10:30:00Z",
      "changed_by": "admin_user_id"
    }
  ]
}
```

## Related Requirements
- **FR-7.1**: Store lead information in database
- **FR-7.4**: Timestamp all stored records
- **NFR-13**: Log access to sensitive information

## Dependencies
- **Depends on**: US-013 (store leads), US-016 (view leads)
- **Blocks**: US-029 (assign leads - status helps with assignment workflow)

## Story Points
**Estimate**: 3 points

## Priority
**High** - Essential for lead management and sales pipeline tracking

## Implementation Status
- **Status**: ⚠️ Partially Implemented
- **Current State**: 
  - Lead model may not have `status` field (needs verification)
  - Status update endpoint may exist but needs enhancement
  - Status change logging not implemented
  - Bulk update not implemented
- **Implementation Notes**: 
  - Status field needs to be added to Lead model if missing
  - Status update logic needs to be implemented in LeadService
  - Audit logging for status changes needs to be added
  - Bulk update functionality needs to be implemented

---

## Implementation Considerations

- **Status Enum**: Define status as enum for type safety
- **Audit Trail**: Consider separate `status_history` table or audit log table
- **Validation**: Ensure status transitions make business sense (optional business rules)
- **Performance**: Bulk updates should be efficient for large datasets
- **UI/UX**: Status update should be quick and accessible from lead list and detail views

