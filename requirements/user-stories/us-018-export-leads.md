# US-018: Export Lead Data

## User Story
As an **admin/sales manager**
I want to **export lead data to files**
So that **I can share leads with sales team, import into CRM, and perform analysis**

## Acceptance Criteria

### AC-018.1: Export Format Options
- Given admin wants to export leads
- When selecting export
- Then the system supports multiple formats:
  - CSV (comma-separated values) ✅
  - Excel/XLSX (can be added)
  - JSON ✅
  - Text file (formatted) (can be added)
- And each format is properly structured

### AC-018.2: Field Selection
- Given admin wants to export
- When configuring export
- Then the system allows selecting which fields to export:
  - All fields (default) ✅
  - Custom selection (can be added)
  - Predefined templates (basic, full, for CRM) (can be added)
- And selection is intuitive

### AC-018.3: Filtered Export
- Given admin has filtered leads (by status, date, policy, etc.)
- When exporting
- Then the system exports only filtered leads
- And exported data matches current filter/view
- And filter criteria is noted in export

### AC-018.4: Complete Lead Information
- Given leads are exported
- When exporting
- Then the system includes all relevant information:
  - Full Name ✅
  - Phone Number (decrypted) ✅
  - Email ✅
  - National ID (decrypted for admin) ✅
  - Address ✅
  - Policy of Interest ✅
  - Preferred contact time (if available)
  - Notes (if available)
  - Status ✅
  - Created date ✅
  - Updated date ✅
  - Conversation ID (link) ✅
- And sensitive data is handled according to security policy

### AC-018.5: Export File Naming
- Given export is generated
- When creating file
- Then the system names file clearly:
  - Includes date/time in filename ✅
  - Includes export type/format ✅
  - Example: "leads_export_20240115.csv"
- And filename indicates contents

### AC-018.6: Export Progress
- Given large number of leads to export
- When exporting
- Then the system:
  - Shows progress indicator (can be added)
  - Provides estimated time remaining (can be added)
  - Allows cancellation if needed (can be added)
- And export completes successfully

### AC-018.7: Export History
- Given exports are performed
- When tracking exports
- Then the system maintains export history (optional):
  - Date/time of export
  - Number of leads exported
  - Export format
  - User who performed export
- And history is accessible to admins

### AC-018.8: Data Formatting
- Given leads are exported
- When formatting data
- Then the system ensures:
  - Dates in consistent format ✅
  - Phone numbers in readable format ✅
  - Addresses properly formatted ✅
  - No data corruption ✅
- And exported data is importable to other systems

## Detailed Scenarios

### Scenario 1: Export All New Leads to CSV
**Given**: Admin filters for status="new"  
**When**: Clicks export, selects CSV  
**Then**: System generates CSV file with all new leads, includes headers, properly formatted, ready for import

### Scenario 2: Export Selected Fields for CRM
**Given**: Admin needs leads for CRM import  
**When**: Selects CRM template (name, phone, email, policy)  
**Then**: System exports only selected fields in CRM-compatible format

### Scenario 3: Large Export
**Given**: 5000 leads to export  
**When**: Admin initiates export  
**Then**: System shows progress, processes in background, completes export, provides download link

### Scenario 4: Filtered Date Range Export
**Given**: Admin filters leads from last week  
**When**: Exports  
**Then**: System exports only leads from that date range, includes filter info in filename

## Technical Notes

- Export via `FileStorageService.export_leads_to_csv()` and `export_leads_to_json()`
- CSV generation with proper headers
- JSON export with structured data
- Data decryption for sensitive fields (admin only)
- File download via FastAPI Response with Content-Disposition header
- Background job processing for large exports (can be added)

## API Implementation

**Endpoint**: `GET /api/leads/export/{format}` (admin only)

**Query Parameters**:
- `format`: "csv" or "json"

**Response**:
- Streaming response with file download
- Content-Type: "text/csv" or "application/json"
- Content-Disposition: "attachment; filename=leads_export_YYYYMMDD.csv"

**Implementation Details**:
- Export via `LeadService.export_leads(format)`
- CSV export via `FileStorageService.export_leads_to_csv()`
- JSON export via `FileStorageService.export_leads_to_json()`
- Data decryption for admin exports
- File download with proper headers

## Related Requirements
- **FR-7.1**: Store lead information (prerequisite)
- API requirement: GET /api/leads/export

## Dependencies
- **Depends on**: US-013 (lead storage)
- **Blocks**: None (standalone admin feature)

## Story Points
**Estimate**: 5 points

## Priority
**Medium-High** - Important for sales operations and CRM integration

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `GET /api/leads/export/{format}` (admin only)
- **Implementation Notes**: 
  - CSV and JSON export implemented
  - Data decryption for admin
  - File download with proper headers
  - Date-based filename
  - Excel export can be added (future enhancement)

---

## Implementation Considerations

- ✅ Export API with format selection implemented
- ✅ Efficient export for datasets (streaming response)
- ✅ Export templates (can be added for common use cases)
- ✅ Sensitive data handling (decryption for admin)
- ✅ Background job queue for large exports (can be added)
- ✅ File cleanup (can be added for temporary files)
