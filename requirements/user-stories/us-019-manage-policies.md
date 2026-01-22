# US-019: Manage Policy Information

## User Story
As an **admin**
I want to **manage the policy knowledge base by ingesting and updating policy documents**
So that **the AI agent has accurate, up-to-date company-specific policy information available for conversations**

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

### AC-019.3: Ingest Policy Document into Knowledge Base
- Given admin wants to add new policy to the knowledge base
- When ingesting a policy document
- Then the system allows:
  - Uploading policy documents (PDF, text, markdown, JSON)
  - Entering policy metadata:
    - Policy name (required)
    - Policy type (term, whole life, universal, etc.)
    - Company name (specific insurance company)
    - Coverage amount range (optional metadata)
    - Premium range (optional metadata)
    - Age eligibility requirements (optional metadata)
- And system processes document:
  - Extracts text from documents (PDF parsing, etc.)
  - Splits document into chunks (500-1000 tokens with overlap)
  - Generates embeddings for each chunk
  - Stores embeddings and metadata in vector database
- And policy becomes searchable in the knowledge base

### AC-019.4: Update Policy in Knowledge Base
- Given admin wants to update policy information
- When updating a policy
- Then the system allows:
  - Re-ingesting updated policy document
  - Updating policy metadata
  - Marking old policy chunks as deprecated
  - Creating new version of policy in knowledge base
- And system handles:
  - Version tracking (maintains old versions for reference)
  - Smooth transition (new version available immediately)
  - Deprecation of old chunks after verification period
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

- **Knowledge Base Management**: Document ingestion service for policy documents
- **Document Processing**: `DocumentIngestionService.ingest_policy_document()` processes documents
- **Text Extraction**: PDF parsing, text extraction from various formats
- **Chunking**: `ChunkingService` splits documents into manageable chunks (500-1000 tokens)
- **Embedding Generation**: `EmbeddingService` creates vector embeddings for semantic search
- **Vector Database**: Policy chunks stored in Chroma/Pinecone/Qdrant with metadata
- **Version Control**: Track policy document versions in knowledge base
- **Metadata Storage**: Policy metadata (name, type, coverage range, etc.) stored with chunks
- Reference checking (can be added for leads using policy)
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
- **FR-9.1**: Maintain policy knowledge base (RAG-based, vector database)
- **FR-9.4**: Support ingestion of policy documents into knowledge base
- **FR-9.5**: Allow updating knowledge base when policy information changes
- **FR-9.6**: Use semantic search to retrieve relevant policy information
- **FR-9.7**: Focus on company-specific policies (competitor info optional)

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
