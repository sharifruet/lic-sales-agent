# RAG Knowledge Base Implementation Plan

## Overview

This document outlines the implementation plan for migrating from a traditional database-based policy system to a **RAG-based custom knowledge base** architecture. This enables semantic search of company-specific insurance policies and improves accuracy through retrieval-augmented generation.

**Key Changes:**
- Replace database queries with semantic search on vector database
- Implement document ingestion pipeline for policy documents
- Integrate RAG retrieval into conversation flow
- Update admin interfaces for knowledge base management

---

## Implementation Phases

### Phase 0: Foundation & Setup (Week 1-2)
**Goal**: Set up infrastructure and development environment for RAG

#### Tasks
1. **Vector Database Setup**
   - [ ] Evaluate and select vector database (Chroma for dev, Pinecone/Qdrant for production)
   - [ ] Set up Chroma locally for development
   - [ ] Configure vector database connection and client
   - [ ] Create collection/schema for policy documents

2. **Embedding Service Setup (Multi-Provider Support)**
   - [ ] **Implement multi-provider EmbeddingService** supporting:
     - Sentence Transformers (FREE for development)
     - Voyage AI voyage-3.5-lite (recommended for production)
     - OpenAI (alternative for production)
   - [ ] Install dependencies:
     - `pip install sentence-transformers` (FREE, for development)
     - `pip install voyageai` (for production - Voyage AI)
     - `pip install openai` (optional, for production - OpenAI)
   - [ ] Implement provider abstraction layer
   - [ ] Add configuration via environment variables
   - [ ] Test embedding generation with each provider
   - [ ] Verify easy switching between providers
   
   **Recommended Setup:**
   - **Development**: Sentence Transformers all-MiniLM-L6-v2 (FREE)
   - **Production**: Voyage AI voyage-3.5-lite (recommended)
   - **Alternative**: OpenAI text-embedding-3-small (if Voyage not available)
   
   **Provider Switching:**
   - Change `EMBEDDING_PROVIDER` environment variable
   - No code changes required
   - All providers use same interface

3. **Development Environment**
   - [ ] Add vector database dependencies to `requirements.txt` (Chroma)
   - [ ] Add embedding dependencies to `requirements.txt` (sentence-transformers)
   - [ ] Update Docker Compose (if needed for local vector DB)
   - [ ] Create environment variables for vector DB and embedding config
   - [ ] Set up local testing environment
   - [ ] Test complete FREE setup (Chroma + Sentence Transformers = $0/month)

#### Deliverables
- Vector database configured and running (Chroma - FREE)
- Embedding service implemented and tested (Sentence Transformers - FREE)
- Development environment ready for RAG development
- **Total Setup Cost: $0/month** ✅

#### Estimated Effort
- **Time**: 1-2 weeks
- **Story Points**: 5 points
- **Dependencies**: None
- **Cost**: $0 (using free Chroma + Sentence Transformers)

---

### Phase 1: Document Processing Pipeline (Week 3-4)
**Goal**: Build infrastructure to ingest policy documents into knowledge base

#### Tasks
1. **Document Loading & Extraction**
   - [ ] Implement `DocumentLoader` for multiple formats (PDF, text, markdown, JSON)
   - [ ] Integrate PDF parsing library (pdfplumber/PyPDF2)
   - [ ] Implement text extraction from various formats
   - [ ] Add error handling for unsupported formats

2. **Chunking Service**
   - [ ] Implement `ChunkingService` class
   - [ ] Configure chunking parameters (size: 500-1000 tokens, overlap: 100-200 tokens)
   - [ ] Implement smart chunking (sentence/paragraph boundaries)
   - [ ] Add tokenizer integration (tiktoken or transformers)

3. **Document Ingestion Service**
   - [ ] Implement `DocumentIngestionService` class
   - [ ] Integrate document loading, chunking, embedding generation
   - [ ] Implement metadata extraction and storage
   - [ ] Add batch ingestion support
   - [ ] Create ingestion status reporting

4. **Initial Data Ingestion**
   - [ ] Prepare sample policy documents
   - [ ] Ingest initial set of company policies
   - [ ] Verify ingested documents in vector database
   - [ ] Create documentation for document preparation

#### Deliverables
- Document processing pipeline functional
- Sample policy documents ingested into knowledge base
- Ingestion service can process documents from various formats

#### Estimated Effort
- **Time**: 2 weeks
- **Story Points**: 13 points
- **Dependencies**: Phase 0 complete

#### User Story
- **US-030**: Manage Policy Knowledge Base (Part 1: Document Ingestion)

---

### Phase 2: RAG Retrieval Service (Week 5-6)
**Goal**: Implement semantic search and retrieval from knowledge base

#### Tasks
1. **RAG Retriever Implementation**
   - [ ] Implement `PolicyService.search_policies()` with semantic search
   - [ ] Build query enhancement (add customer profile context)
   - [ ] Implement top-k retrieval with similarity scoring
   - [ ] Add metadata filtering (age eligibility, policy type, etc.)
   - [ ] Implement result formatting and ranking

2. **Query Enhancement**
   - [ ] Build enhanced query from user message and customer profile
   - [ ] Add context enrichment logic
   - [ ] Implement query optimization

3. **Retrieval Optimization**
   - [ ] Implement similarity threshold filtering
   - [ ] Add diversity filtering (ensure different policies in results)
   - [ ] Optimize retrieval performance
   - [ ] Add caching for frequent queries (optional)

4. **Testing & Validation**
   - [ ] Create test queries for policy retrieval
   - [ ] Verify retrieval accuracy and relevance
   - [ ] Test edge cases (no results, low similarity, etc.)
   - [ ] Performance testing (retrieval latency < 200ms)

#### Deliverables
- RAG retrieval service fully functional
- Semantic search working with customer profile context
- Retrieval performance optimized
- Test suite for retrieval service

#### Estimated Effort
- **Time**: 2 weeks
- **Story Points**: 13 points
- **Dependencies**: Phase 1 complete

---

### Phase 3: LLM Integration with RAG (Week 7-8)
**Goal**: Integrate RAG retrieval into conversation flow and LLM prompts

#### Tasks
1. **RAG-Augmented Prompt Construction**
   - [ ] Update prompt templates to include retrieved policy context
   - [ ] Implement `build_rag_enhanced_prompt()` function
   - [ ] Add instructions for LLM to use ONLY retrieved context
   - [ ] Format retrieved context for prompt injection

2. **Conversation Service Updates**
   - [ ] Update `ConversationService` to use RAG retrieval
   - [ ] Integrate policy retrieval into message processing flow
   - [ ] Determine when to trigger policy retrieval
   - [ ] Handle cases where retrieval not needed (greetings, etc.)

3. **LangGraph Retriever Node Updates**
   - [ ] Update `graph/nodes/retriever.py` to use knowledge base
   - [ ] Integrate with vector database retrieval
   - [ ] Update retriever chain to use policy knowledge base
   - [ ] Ensure retrieved context flows to action node

4. **Response Verification**
   - [ ] Implement response verification against retrieved context
   - [ ] Add logging for unverified policy claims
   - [ ] Create fallback mechanisms

5. **Testing**
   - [ ] Test RAG-augmented conversations
   - [ ] Verify policy information accuracy
   - [ ] Test edge cases (no relevant policies, ambiguous queries)
   - [ ] Compare responses before/after RAG integration

#### Deliverables
- RAG fully integrated into conversation flow
- LLM responses grounded in retrieved policy context
- Updated conversation service and LangGraph nodes
- Comprehensive testing completed

#### Estimated Effort
- **Time**: 2 weeks
- **Story Points**: 13 points
- **Dependencies**: Phase 2 complete

#### User Stories
- **US-004**: Present Company Policies (RAG-based retrieval)
- **US-006**: Compare Policy Options (RAG-based comparison)

---

### Phase 4: Admin Knowledge Base Management (Week 9-10)
**Goal**: Build admin interface for managing knowledge base

#### Tasks
1. **Knowledge Base Management API**
   - [ ] Create `POST /api/knowledge-base/ingest` endpoint
   - [ ] Create `GET /api/knowledge-base/documents` endpoint
   - [ ] Create `POST /api/knowledge-base/test-query` endpoint
   - [ ] Create `PUT /api/knowledge-base/documents/{id}` for updates
   - [ ] Add authentication and authorization

2. **Admin UI Components**
   - [ ] Create document upload interface
   - [ ] Build document list view
   - [ ] Create metadata configuration form
   - [ ] Implement test query interface
   - [ ] Add ingestion status/progress indicators

3. **Knowledge Base Operations**
   - [ ] Implement document versioning
   - [ ] Add deprecation workflow for old documents
   - [ ] Create bulk ingestion interface
   - [ ] Implement document search/filtering in admin UI

4. **Quality Assurance Tools**
   - [ ] Build test query interface
   - [ ] Create retrieval accuracy reports
   - [ ] Implement knowledge base coverage analysis
   - [ ] Add validation tools

#### Deliverables
- Admin API endpoints for knowledge base management
- Admin UI for document ingestion and management
- Quality assurance tools for verifying knowledge base

#### Estimated Effort
- **Time**: 2 weeks
- **Story Points**: 13 points
- **Dependencies**: Phase 1 complete (can run parallel to Phase 3)

#### User Story
- **US-030**: Manage Policy Knowledge Base (Complete)
- **US-019**: Manage Policy Information (Updated for knowledge base)

---

### Phase 5: Migration & Data Migration (Week 11-12)
**Goal**: Migrate existing policies to knowledge base and update systems

#### Tasks
1. **Existing Policy Migration**
   - [ ] Export existing policies from database
   - [ ] Convert structured policy data to documents
   - [ ] Ingest existing policies into knowledge base
   - [ ] Verify all policies migrated correctly

2. **System Updates**
   - [ ] Update `PolicyService` to use RAG as primary method
   - [ ] Keep database for metadata/caching (optional)
   - [ ] Update all API endpoints using policy data
   - [ ] Update tests to use knowledge base

3. **Backward Compatibility**
   - [ ] Ensure existing API contracts maintained
   - [ ] Handle transition period gracefully
   - [ ] Create migration scripts
   - [ ] Document migration process

4. **Deployment**
   - [ ] Deploy vector database in staging
   - [ ] Deploy knowledge base services
   - [ ] Perform staging testing
   - [ ] Deploy to production

#### Deliverables
- All existing policies migrated to knowledge base
- System fully operational with RAG architecture
- Migration documentation

#### Estimated Effort
- **Time**: 2 weeks
- **Story Points**: 8 points
- **Dependencies**: Phases 1-3 complete

---

### Phase 6: Testing & Optimization (Week 13-14)
**Goal**: Comprehensive testing and performance optimization

#### Tasks
1. **Integration Testing**
   - [ ] End-to-end conversation flow testing
   - [ ] Test policy retrieval in various scenarios
   - [ ] Test knowledge base updates and propagation
   - [ ] Test error handling and edge cases

2. **Performance Optimization**
   - [ ] Optimize retrieval latency (target: < 200ms)
   - [ ] Optimize embedding generation
   - [ ] Implement caching where appropriate
   - [ ] Optimize vector database queries

3. **Accuracy Validation**
   - [ ] Test retrieval accuracy with sample queries
   - [ ] Verify LLM responses match policy documents
   - [ ] Test coverage (all policies retrievable)
   - [ ] Validate against test dataset

4. **User Acceptance Testing**
   - [ ] Test with real policy documents
   - [ ] Gather feedback from admin users
   - [ ] Test conversation quality
   - [ ] Validate business requirements

5. **Documentation**
   - [ ] Update API documentation
   - [ ] Create knowledge base management guide
   - [ ] Document ingestion workflows
   - [ ] Create troubleshooting guide

#### Deliverables
- Comprehensive test suite passing
- Performance optimized
- Documentation complete
- System ready for production

#### Estimated Effort
- **Time**: 2 weeks
- **Story Points**: 8 points
- **Dependencies**: Phases 1-5 complete

---

## Implementation Timeline

```
Week 1-2:   Phase 0 - Foundation & Setup
Week 3-4:   Phase 1 - Document Processing Pipeline
Week 5-6:   Phase 2 - RAG Retrieval Service
Week 7-8:   Phase 3 - LLM Integration with RAG
Week 9-10:  Phase 4 - Admin Knowledge Base Management (can parallel with Phase 3)
Week 11-12: Phase 5 - Migration & Data Migration
Week 13-14: Phase 6 - Testing & Optimization

Total Duration: 14 weeks (~3.5 months)
```

**Parallel Execution Opportunities:**
- Phase 3 and Phase 4 can run partially in parallel
- Testing can begin incrementally during each phase

---

## Dependencies & Prerequisites

### Technical Prerequisites
- [ ] Vector database selected and accessible
- [ ] Embedding model/API configured
- [ ] Development environment set up
- [ ] Existing policy data available for migration

### External Dependencies
- [ ] Access to company policy documents
- [ ] Policy documents in digital format (PDF, text, etc.)
- [ ] Approval for knowledge base architecture approach
- [ ] Resources allocated (developer time)

### Team Requirements
- [ ] Developer(s) with RAG/vector database experience
- [ ] Access to LLM APIs (OpenAI/Anthropic) or local LLM
- [ ] Admin user for testing knowledge base management

---

## Risk Assessment & Mitigation

### High Risk Items

1. **Risk**: Vector database performance issues
   - **Impact**: Slow retrieval, poor user experience
   - **Mitigation**: Performance testing early, optimize queries, consider caching
   - **Contingency**: Use faster vector DB or optimize chunking strategy

2. **Risk**: Embedding quality insufficient
   - **Impact**: Poor retrieval accuracy, irrelevant results
   - **Mitigation**: Test different embedding models, fine-tune chunking
   - **Contingency**: Try different embedding models or domain-specific models

3. **Risk**: Document ingestion complexity
   - **Impact**: Delays in getting policies into knowledge base
   - **Mitigation**: Start with simple formats, iterate
   - **Contingency**: Manual document preparation or structured data import

4. **Risk**: LLM hallucination despite RAG
   - **Impact**: Incorrect policy information
   - **Mitigation**: Strict prompts, response verification, testing
   - **Contingency**: Add additional validation layers

5. **Risk**: Migration of existing policies
   - **Impact**: Data loss or incomplete migration
   - **Mitigation**: Thorough testing, backup existing data
   - **Contingency**: Keep old system running during transition

### Medium Risk Items

1. **Risk**: Vector database costs (if using managed service)
   - **Mitigation**: Monitor usage, optimize storage
   - **Contingency**: Consider self-hosted option

2. **Risk**: Knowledge base maintenance complexity
   - **Mitigation**: Build good admin tools, document processes
   - **Contingency**: Train admin users thoroughly

---

## Success Criteria

### Phase Completion Criteria

**Phase 0 Complete:**
- ✅ Vector database running and accessible
- ✅ Embedding service generates embeddings successfully
- ✅ Development environment configured

**Phase 1 Complete:**
- ✅ Documents can be ingested into knowledge base
- ✅ At least 5 sample policies successfully ingested
- ✅ Ingestion pipeline handles multiple formats

**Phase 2 Complete:**
- ✅ Semantic search retrieves relevant policies
- ✅ Query enhancement improves retrieval quality
- ✅ Retrieval latency < 500ms (initial target)

**Phase 3 Complete:**
- ✅ Conversations use RAG-retrieved policy information
- ✅ LLM responses grounded in retrieved context
- ✅ Response accuracy improved vs. baseline

**Phase 4 Complete:**
- ✅ Admin can ingest documents via UI/API
- ✅ Knowledge base management interface functional
- ✅ Quality assurance tools available

**Phase 5 Complete:**
- ✅ All existing policies migrated to knowledge base
- ✅ System fully operational with RAG
- ✅ No breaking changes to existing functionality

**Phase 6 Complete:**
- ✅ All tests passing
- ✅ Performance targets met
- ✅ Documentation complete
- ✅ Ready for production deployment

### Overall Success Metrics

1. **Accuracy**: Policy information accuracy > 95% (verified against source documents)
2. **Performance**: Policy retrieval latency < 200ms (p95)
3. **Coverage**: All active policies available in knowledge base
4. **Usability**: Admin can ingest new policies within 10 minutes
5. **Quality**: LLM responses grounded in knowledge base (no hallucinations)

---

## Testing Strategy

### Unit Tests
- Document loading and extraction
- Chunking service
- Embedding generation
- Retrieval logic
- Query enhancement

### Integration Tests
- End-to-end document ingestion
- Semantic search and retrieval
- RAG-augmented conversation flow
- Knowledge base updates propagation

### Acceptance Tests
- User story acceptance criteria validation
- Business requirement validation
- Conversation quality assessment

### Performance Tests
- Retrieval latency
- Ingestion throughput
- Concurrent conversation handling
- Vector database query performance

### Quality Assurance Tests
- Retrieval accuracy (relevant policies retrieved)
- Response accuracy (matches policy documents)
- Coverage (all policies retrievable)
- Edge case handling

---

## Rollout Strategy

### Development Environment
- Week 1-8: Develop and test in dev environment
- Use sample/dummy policy documents
- Test with small document set

### Staging Environment
- Week 9-12: Deploy to staging
- Use real policy documents (sanitized if needed)
- Full integration testing
- Performance testing
- Admin user training

### Production Deployment
- Week 13-14: Final testing and optimization
- Deploy to production
- Monitor closely for first week
- Gradual rollout (migrate policies incrementally)

### Rollback Plan
- Keep existing database-based system available
- Feature flag to switch between systems
- Ability to rollback vector database changes
- Data backup before migration

---

## Resource Requirements

### Development Team
- **Backend Developer**: 1 FTE for 14 weeks (RAG implementation)
- **Full-Stack Developer**: 0.5 FTE for 4 weeks (Admin UI)
- **DevOps Engineer**: 0.25 FTE for 2 weeks (Infrastructure setup)

### Infrastructure
- **Vector Database**: Chroma (dev) / Pinecone/Qdrant (production)
- **Embedding API**: OpenAI API or local Sentence Transformers
- **Storage**: Additional storage for vector embeddings
- **Compute**: Additional compute for embedding generation (if local)

### External Services
- **Embedding API**: OpenAI embeddings API (if used)
- **Vector Database**: Pinecone (if managed service used)
- **LLM API**: Existing OpenAI/Anthropic API (no change)

---

## Documentation Deliverables

### Technical Documentation
- [ ] Vector database setup guide
- [ ] Document ingestion guide
- [ ] Knowledge base architecture overview
- [ ] API documentation updates
- [ ] Troubleshooting guide

### User Documentation
- [ ] Admin guide for knowledge base management
- [ ] Document preparation guidelines
- [ ] Knowledge base best practices
- [ ] FAQ for knowledge base operations

### Development Documentation
- [ ] Developer setup guide
- [ ] Code architecture documentation
- [ ] Testing guide
- [ ] Migration guide

---

## Post-Implementation

### Monitoring & Maintenance
- Monitor retrieval accuracy
- Track knowledge base query patterns
- Monitor embedding generation costs
- Review and update policy documents regularly

### Future Enhancements
- Fine-tune embedding model on insurance domain
- Implement hybrid search (keyword + semantic)
- Add feedback loop for retrieval quality
- Implement A/B testing for retrieval strategies

---

## Free Embedding Models for Local Development

### Recommended: Sentence Transformers (100% FREE)

For local development, we strongly recommend using **Sentence Transformers** - completely free, open-source embedding models that run locally on your machine.

#### Why Sentence Transformers for Development?

✅ **Completely FREE** - No API costs, no usage limits  
✅ **Runs Locally** - Complete data privacy, works offline  
✅ **Good Quality** - Excellent for development and testing  
✅ **Fast** - Quick inference on modern CPUs  
✅ **No Setup Hassle** - Simple Python package installation  

#### Recommended Model: all-MiniLM-L6-v2

**Best for Development:**
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Size: ~80MB
- Dimensions: 384
- Speed: Very fast on CPU
- Quality: Good for semantic search

**Installation:**
```bash
pip install sentence-transformers
```

**Usage Example:**
```python
from sentence_transformers import SentenceTransformer

# Load model (downloads on first use, ~80MB)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
sentences = ["This is a policy document", "Life insurance coverage"]
embeddings = model.encode(sentences)
# Returns numpy array of shape (2, 384)
```

#### Alternative Free Models

**Option 2: all-mpnet-base-v2** (Better Quality)
- Higher quality embeddings (768 dimensions)
- Slower inference (~420MB)
- Use if you need better semantic understanding

**Option 3: multi-qa-MiniLM-L6-cos-v1** (Optimized for Q&A)
- Optimized for question-answering scenarios
- Good for RAG retrieval
- Similar size/speed to all-MiniLM-L6-v2

#### Comparison: Free vs. Paid Embeddings

| Feature | Sentence Transformers (FREE) | OpenAI Embeddings (PAID) |
|---------|------------------------------|--------------------------|
| **Cost** | $0/month | ~$0.02 per 1M tokens |
| **Setup** | `pip install sentence-transformers` | API key required |
| **Privacy** | 100% local, no data leaves machine | Data sent to OpenAI |
| **Quality** | Good (suitable for development) | Excellent |
| **Speed** | Fast (local CPU) | Very fast (cloud) |
| **Offline** | Yes | No (requires internet) |
| **Best For** | Development, testing, production (if quality acceptable) | Production (if quality critical) |

#### Setup Instructions for Free Embeddings

**1. Install Sentence Transformers:**
```bash
pip install sentence-transformers
```

**2. Update Embedding Service:**
```python
# rag/services/embedding_service.py
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        return self.model.encode(text).tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return self.model.encode(texts).tolist()
```

**3. Update Environment Configuration:**
```bash
# .env
EMBEDDING_PROVIDER=sentence_transformers  # or "openai" for production
EMBEDDING_MODEL=all-MiniLM-L6-v2
# No API key needed for Sentence Transformers!
```

**4. Verify Setup:**
```python
from rag.services.embedding_service import EmbeddingService

service = EmbeddingService()
embedding = service.embed("test policy document")
print(f"Embedding dimension: {len(embedding)}")  # Should be 384 for all-MiniLM-L6-v2
```

#### Development Cost Savings

Using free embeddings for development:
- **Traditional Approach**: ~$50-100/month for embedding API during development
- **Free Approach**: **$0/month** using Sentence Transformers
- **Savings**: 100% cost reduction for development! 💰

#### Production Cost Comparison

**Voyage AI voyage-3.5-lite (Recommended):**
- Lower cost than OpenAI (6.5x lower)
- Better quality than OpenAI v3-large (6.34% improvement)
- Optimized for retrieval tasks
- **Best choice for production** ✅

**OpenAI (Alternative):**
- Higher cost than Voyage AI
- Good quality
- Widely available

**Sentence Transformers (FREE Option):**
- $0 cost
- Good quality (may be acceptable for production)
- Requires local compute resources

#### Migration Path

**Development → Production:**
1. **Development**: Use Sentence Transformers (free)
2. **Staging**: Test with both Sentence Transformers and OpenAI
3. **Production**: Choose based on quality vs. cost:
   - Continue with Sentence Transformers if quality acceptable
   - Upgrade to OpenAI if quality improvements needed

**Both options can coexist:**
- Abstract embedding service supports multiple providers
- Easy to switch between providers via configuration
- No code changes needed when switching

---

## Appendix

### Technology Stack Decisions

#### Vector Database Options
- **Chroma**: Best for development, easy setup, open source
- **Pinecone**: Best for production, managed service, scalable
- **Qdrant**: Good for self-hosted production, open source, performant

**Recommendation**: Start with Chroma for development, evaluate Pinecone/Qdrant for production.

#### Embedding Models

**For Local Development (FREE - Recommended):**
- **Sentence Transformers (all-MiniLM-L6-v2)**: 
  - ✅ **Completely FREE** - no API costs
  - ✅ Open source, runs locally
  - ✅ Good quality for development (384-dimensional embeddings)
  - ✅ Fast inference on CPU
  - ✅ No internet required after initial download
  - ✅ ~80MB model size
  - **Installation**: `pip install sentence-transformers`
  
- **all-mpnet-base-v2** (Alternative - Better Quality):
  - ✅ FREE, open source
  - ✅ Higher quality embeddings (768 dimensions)
  - ✅ Better semantic understanding
  - ⚠️ Slower and larger (~420MB)

- **multi-qa-MiniLM-L6-cos-v1** (Alternative - Optimized for Q&A):
  - ✅ FREE, optimized for question-answering
  - ✅ Good for RAG retrieval scenarios
  - ✅ ~80MB model size

**For Production (Recommended):**
- **Voyage AI voyage-3.5-lite**: 
  - ✅ **Recommended for production** - Best balance of quality and cost
  - ✅ Excellent retrieval quality (outperforms OpenAI v3-large by 6.34% on average)
  - ✅ Lower cost than OpenAI (6.5x lower costs)
  - ✅ Supports multiple dimensions (256, 512, 1024, 2048)
  - ✅ Optimized for RAG/retrieval scenarios
  - ✅ Supports input_type ("document" vs "query") for better retrieval
  - ✅ Installation: `pip install voyageai`
  - ✅ Cost: Lower than OpenAI, check Voyage AI pricing

**For Production (Alternative):**
- **OpenAI text-embedding-3-small**: Excellent quality, requires API key (~$0.02 per 1M tokens)
- **OpenAI text-embedding-ada-002**: Previous generation, cheaper

**Recommendation**: 
- **Development**: Use Sentence Transformers (all-MiniLM-L6-v2) - FREE and perfect for local development
- **Production**: Use Voyage AI voyage-3.5-lite (recommended) - best quality/cost ratio
- **Alternative**: OpenAI embeddings if Voyage AI not available
- **Switching**: Easy provider switching via configuration - no code changes needed

### Estimated Costs

#### Development Phase (FREE Setup)
- Vector Database (Chroma): **FREE** (local, open source)
- Embedding Model (Sentence Transformers): **FREE** (local, open source)
- Infrastructure: Existing (local development)
- **Total Development Cost: $0/month** ✅

#### Production Phase

**Option 1: Voyage AI (Recommended)**
- Vector Database (Pinecone): ~$70-200/month (depending on scale)
- Embedding API (Voyage AI voyage-3.5-lite): ~$15-50/month (lower cost than OpenAI)
- Storage: ~$20-50/month (embeddings storage)
- **Total Estimated Monthly Cost**: ~$105-300/month

**Option 2: OpenAI (Alternative)**
- Vector Database (Pinecone): ~$70-200/month (depending on scale)
- Embedding API (OpenAI): ~$100-300/month (production usage)
- Storage: ~$20-50/month (embeddings storage)
- **Total Estimated Monthly Cost**: ~$190-550/month

**Option 3: Sentence Transformers (FREE)**
- Vector Database (Pinecone): ~$70-200/month (depending on scale)
- Embedding API: $0/month (local execution)
- Storage: ~$20-50/month (embeddings storage)
- **Total Estimated Monthly Cost**: ~$90-250/month (if quality acceptable)

**Recommendation**: Use Voyage AI voyage-3.5-lite for production - best quality/cost ratio

---

**Document Version**: 1.0  
**Last Updated**: [Date]  
**Status**: Draft  
**Next Review**: [Date]

