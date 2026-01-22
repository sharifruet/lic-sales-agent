# US-030: Manage Policy Knowledge Base

## User Story
As an **admin**
I want to **ingest and manage policy documents in the knowledge base**
So that **the AI agent can accurately retrieve and present company-specific policy information to customers**

## Acceptance Criteria

### AC-030.1: Document Ingestion
- Given admin has policy documents to add
- When ingesting documents into knowledge base
- Then the system supports multiple document formats:
  - PDF files (policy brochures, fact sheets)
  - Text/Markdown files
  - Structured JSON/CSV (policy metadata)
  - Web pages (scraped content)
- And system extracts text from documents
- And system splits documents into appropriate chunks (500-1000 tokens with overlap)
- And system generates embeddings for each chunk
- And system stores embeddings and metadata in vector database

### AC-030.2: Metadata Configuration
- Given admin ingests a policy document
- When configuring metadata
- Then the system allows specifying:
  - Policy name (required)
  - Policy type (term, whole life, universal, etc.)
  - Company name (specific insurance company)
  - Coverage amount range (optional)
  - Premium range (optional)
  - Age eligibility requirements (optional)
  - Document source (filename, URL, etc.)
  - Last updated date
- And metadata is stored with each document chunk
- And metadata enables filtering during retrieval

### AC-030.3: Document Processing Pipeline
- Given admin uploads a policy document
- When processing the document
- Then the system:
  1. Validates document format
  2. Extracts text (handles PDF, text, markdown, JSON)
  3. Splits into chunks with overlap (preserves context)
  4. Generates vector embeddings for each chunk
  5. Stores chunks with embeddings and metadata in vector database
  6. Reports ingestion status (success, failures, chunk count)

### AC-030.4: Knowledge Base Updates
- Given admin wants to update existing policy information
- When updating a policy in knowledge base
- Then the system allows:
  - Re-ingesting updated document (creates new version)
  - Updating metadata without re-ingestion
  - Marking old chunks as deprecated
- And system maintains version history
- And system supports rollback if needed
- And updated information becomes available for retrieval immediately

### AC-030.5: Knowledge Base Viewing
- Given admin wants to view knowledge base contents
- When accessing knowledge base
- Then the system displays:
  - List of ingested documents
  - Document metadata
  - Chunk count per document
  - Last updated date
  - Document status (active, deprecated)
- And system allows searching/filtering documents
- And system shows document statistics (total chunks, storage size)

### AC-030.6: Quality Assurance
- Given policy documents are in knowledge base
- When verifying knowledge base quality
- Then the system provides:
  - Test query interface to verify retrieval
  - Search result preview (shows what would be retrieved)
  - Accuracy verification tools
  - Coverage reports (which policies are in knowledge base)
- And admin can verify retrieved information matches source documents

### AC-030.7: Bulk Ingestion
- Given admin has multiple policy documents
- When ingesting multiple documents
- Then the system supports:
  - Batch upload (multiple files at once)
  - Folder/directory upload
  - Bulk metadata configuration
  - Progress tracking for bulk operations
- And system processes documents efficiently
- And system reports results per document

### AC-030.8: Access Control
- Given knowledge base management is accessed
- When performing operations
- Then the system enforces:
  - Authentication required (admin only)
  - Authorization checks for ingestion/updates
  - Audit logging of all knowledge base changes
  - Version tracking for compliance

## Detailed Scenarios

### Scenario 1: Ingest New Policy Document
**Given**: Admin has a new policy brochure (PDF) to add  
**When**: Admin uploads PDF and configures metadata  
**Then**: System extracts text, creates chunks, generates embeddings, stores in vector database, policy becomes searchable in conversations

### Scenario 2: Update Existing Policy
**Given**: Policy information has changed (new premium rates)  
**When**: Admin re-uploads updated document  
**Then**: System creates new version, marks old chunks as deprecated, new information available immediately, old version preserved for reference

### Scenario 3: Verify Retrieval Quality
**Given**: Admin wants to verify knowledge base is working correctly  
**When**: Admin runs test queries  
**Then**: System shows what documents would be retrieved, admin can verify accuracy and relevance

### Scenario 4: Bulk Document Ingestion
**Given**: Admin has folder of 20 policy documents  
**When**: Admin uploads entire folder  
**Then**: System processes all documents, shows progress, reports results, all policies available in knowledge base

## Technical Notes

- **Document Ingestion Service**: `DocumentIngestionService.ingest_policy_document()`
- **Text Extraction**: PDF parsing (pdfplumber/PyPDF2), text/markdown reading
- **Chunking Service**: `ChunkingService` splits documents (500-1000 tokens, 100-200 token overlap)
- **Embedding Service**: `EmbeddingService` generates embeddings (OpenAI or Sentence Transformers)
- **Vector Database**: Chroma/Pinecone/Qdrant for storing embeddings
- **Metadata Storage**: Policy metadata stored with each chunk in vector database
- **Version Control**: Track policy document versions and deprecation
- **Admin Interface**: Web UI or API endpoints for knowledge base management

## API Implementation

**Endpoint**: `POST /api/knowledge-base/ingest`

**Request**:
```json
{
  "document": "<file_upload>",
  "metadata": {
    "policy_name": "Term Life 20-Year",
    "policy_type": "term",
    "company": "SecureLife Insurance",
    "coverage_range": {"min": 50000, "max": 1000000},
    "premium_range": {"min": 50, "max": 200},
    "age_requirements": {"min_age": 18, "max_age": 65}
  },
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

**Response**:
```json
{
  "status": "success",
  "document_id": "uuid",
  "chunks_created": 15,
  "message": "Document ingested successfully"
}
```

**Endpoint**: `GET /api/knowledge-base/documents`

**Response**:
```json
{
  "documents": [
    {
      "id": "uuid",
      "policy_name": "Term Life 20-Year",
      "source": "term_life_brochure.pdf",
      "chunks_count": 15,
      "last_updated": "2024-01-15T10:00:00Z",
      "status": "active"
    }
  ]
}
```

**Endpoint**: `POST /api/knowledge-base/test-query`

**Request**:
```json
{
  "query": "policies for young families",
  "top_k": 3
}
```

**Response**:
```json
{
  "results": [
    {
      "content": "...",
      "source": "term_life_brochure.pdf",
      "similarity_score": 0.89,
      "metadata": {...}
    }
  ]
}
```

**Implementation Details**:
- Document ingestion via `DocumentIngestionService`
- Vector database operations via vector DB client (Chroma/Pinecone/Qdrant)
- Metadata management via `PolicyMetadataRepository`
- Admin authentication required for all operations
- Audit logging for all knowledge base changes

## Related Requirements
- **FR-9.1**: Maintain policy knowledge base (RAG-based)
- **FR-9.4**: Support ingestion of policy documents
- **FR-9.5**: Allow updating knowledge base when policies change
- **FR-9.6**: Use semantic search for retrieval
- **FR-9.8**: Knowledge base configuration specific to insurance company

## Dependencies
- **Depends on**: Knowledge base infrastructure (vector database setup)
- **Blocks**: US-004 (policies must be in knowledge base to be presented)

## Story Points
**Estimate**: 13 points

## Priority
**High** - Foundational for RAG-based policy retrieval

## Implementation Status
- **Status**: 📝 Draft
- **Implementation Notes**: 
  - Knowledge base architecture designed
  - Document ingestion pipeline needs implementation
  - Admin interface needs development
  - Quality assurance tools need creation

---

## Implementation Considerations

- ✅ **Architecture Designed**: RAG knowledge base architecture documented
- ✅ **Component Design**: Document ingestion, chunking, embedding services designed
- ⚠️ **Vector Database Setup**: Need to configure Chroma/Pinecone/Qdrant
- ⚠️ **Document Processing**: PDF parsing, text extraction needs implementation
- ⚠️ **Admin Interface**: Need to build UI or API for knowledge base management
- ⚠️ **Quality Assurance**: Test query interface needs development
- ⚠️ **Version Control**: Policy version tracking needs implementation

