# US-029: Assign Leads to Sales Agents

## User Story
As an **admin/sales manager**
I want to **assign leads to specific sales agents**
So that **I can distribute leads efficiently and track which agent is responsible for each lead**

## Acceptance Criteria

### AC-029.1: Lead Assignment Capability
- Given admin views a lead
- When assigning lead to sales agent
- Then the system allows:
  - Selecting sales agent from list of available agents
  - Assigning single lead to one agent
  - Reassigning lead to different agent if needed
  - Unassigning lead (removing assignment)
- And assignment is saved immediately

### AC-029.2: Sales Agent Management
- Given system needs list of sales agents
- When accessing assignment interface
- Then the system provides:
  - List of available sales agents
  - Agent name and identifier
  - Agent contact information (optional)
  - Agent availability status (active/inactive)
- And list is searchable and filterable

### AC-029.3: Assignment Tracking
- Given lead is assigned to agent
- When viewing lead details
- Then the system displays:
  - Assigned agent name
  - Assignment date/time
  - Who made the assignment (admin user)
  - Assignment history (if reassigned)
- And information is clearly visible

### AC-029.4: Bulk Assignment
- Given admin needs to assign multiple leads
- When selecting multiple leads
- Then the system allows:
  - Selecting multiple leads (checkbox selection)
  - Choosing agent for all selected leads
  - Confirming bulk assignment
  - All selected leads assigned to chosen agent
- And each assignment is logged individually

### AC-029.5: Assignment-Based Filtering
- Given leads are assigned to different agents
- When viewing lead list
- Then the system allows filtering by:
  - Assigned agent (show only leads for specific agent)
  - Unassigned leads (show leads with no assignment)
  - Multiple agents (show leads for selected agents)
- And filtered view updates immediately

### AC-029.6: Assignment Notifications
- Given lead is assigned to agent
- When assignment is made
- Then the system can send notification (future feature):
  - Email notification to assigned agent
  - In-app notification in agent dashboard
  - SMS notification (optional, configurable)
- And notification includes lead summary and contact information

### AC-029.7: Assignment Workload Balancing (Future)
- Given multiple agents available
- When assigning leads
- Then the system can suggest agent based on (future feature):
  - Current workload (number of assigned leads)
  - Agent specialization (if applicable)
  - Geographic proximity (if applicable)
  - Agent availability
- And suggestion is optional (admin can override)

### AC-029.8: Agent Performance Tracking (Future)
- Given leads are assigned to agents
- When tracking performance
- Then the system can provide metrics (future feature):
  - Number of leads assigned per agent
  - Conversion rate per agent
  - Average time to contact per agent
  - Lead status distribution per agent
- And metrics are available in analytics dashboard

## Detailed Scenarios

### Scenario 1: Single Lead Assignment
**Given**: Admin views unassigned lead with status "new"  
**When**: Admin selects agent "John Smith" and assigns  
**Then**: Lead is assigned to John Smith, assignment timestamp recorded, lead appears in John's assigned leads list, notification sent to John (if enabled)

### Scenario 2: Bulk Assignment
**Given**: Admin has 5 unassigned leads  
**When**: Admin selects all 5, chooses agent "Sarah Johnson", confirms  
**Then**: All 5 leads assigned to Sarah, each assignment logged, leads appear in Sarah's list, notifications sent

### Scenario 3: Reassignment
**Given**: Lead is assigned to agent "Mike"  
**When**: Admin reassigns to agent "Lisa"  
**Then**: Assignment updated to Lisa, previous assignment logged in history, Mike's assignment count decreases, Lisa's increases, both agents notified (if enabled)

### Scenario 4: Unassignment
**Given**: Lead is assigned to agent "Tom"  
**When**: Admin removes assignment  
**Then**: Lead becomes unassigned, assignment history preserved, lead appears in unassigned filter, Tom's assignment count decreases

### Scenario 5: Agent Workload View
**Given**: Multiple agents with assigned leads  
**When**: Admin views agent workload  
**Then**: System shows number of leads per agent, helps identify agents who need more/fewer leads, supports workload balancing

## Technical Notes

- Assignment stored in `Lead.assigned_to` field (foreign key to User/Agent table)
- Assignment date/time stored in `Lead.assigned_at` field
- Assignment history can be stored in separate `lead_assignments` table for audit trail
- Agent/User model needed if not exists (can extend existing User model)
- API endpoints for assignment operations
- Authorization: Only admin users can assign leads

## API Implementation

**Current Implementation**:
- Lead model may not have `assigned_to` field (needs to be added)
- Assignment endpoints need to be created
- Agent/User model may need to be created or extended

**Required Implementation**:
- Add `assigned_to` field to `Lead` model (foreign key to User)
- Add `assigned_at` field to `Lead` model
- Create or extend User model to support sales agent role
- Implement assignment logic in `LeadService`
- Add assignment endpoints:
  - `PUT /api/leads/{lead_id}/assign` - Assign single lead
  - `PUT /api/leads/bulk-assign` - Bulk assignment
  - `DELETE /api/leads/{lead_id}/assign` - Unassign lead
- Add assignment filtering to lead list endpoint
- Add assignment notifications (future)

**API Endpoint**: `PUT /api/leads/{lead_id}/assign`

**Request**:
```json
{
  "agent_id": 5,
  "notes": "Assigned based on geographic proximity"
}
```

**Response**:
```json
{
  "id": 123,
  "assigned_to": {
    "id": 5,
    "name": "John Smith",
    "email": "john.smith@company.com"
  },
  "assigned_at": "2024-01-15T10:30:00Z",
  "assigned_by": "admin_user_id",
  "status": "new"
}
```

**Bulk Assignment Endpoint**: `PUT /api/leads/bulk-assign`

**Request**:
```json
{
  "lead_ids": [123, 124, 125, 126, 127],
  "agent_id": 5
}
```

**Response**:
```json
{
  "assigned_count": 5,
  "assigned_leads": [123, 124, 125, 126, 127],
  "agent": {
    "id": 5,
    "name": "John Smith"
  }
}
```

## Related Requirements
- **FR-7.1**: Store lead information in database
- **FR-7.4**: Timestamp all stored records
- **NFR-13**: Log access to sensitive information
- **Future**: CRM system integration

## Dependencies
- **Depends on**: US-013 (store leads), US-016 (view leads), US-028 (update lead status)
- **Blocks**: Future CRM integration, agent performance tracking

## Story Points
**Estimate**: 5 points

## Priority
**Medium-High** - Important for sales team workflow, but can be implemented after core lead management

## Implementation Status
- **Status**: 📝 Not Implemented (Future Feature)
- **Current State**: 
  - Lead model does not have `assigned_to` field
  - No agent/user model for sales agents
  - Assignment endpoints not implemented
  - Assignment notifications not implemented
- **Implementation Notes**: 
  - This is a future enhancement mentioned in US-016
  - Requires User/Agent model creation or extension
  - Assignment functionality can be added incrementally
  - Notifications and workload balancing are future enhancements

---

## Implementation Considerations

- **User/Agent Model**: Create separate `SalesAgent` model or extend `User` model with role
- **Assignment History**: Consider `lead_assignments` table for full audit trail
- **Notifications**: Email/SMS notifications can be added later
- **Workload Balancing**: Can be simple (count-based) or advanced (ML-based)
- **Performance**: Bulk assignments should be efficient
- **UI/UX**: Assignment should be quick and accessible from lead list and detail views
- **Future Integration**: Design with CRM integration in mind

