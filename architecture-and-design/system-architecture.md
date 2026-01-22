# System Architecture Document
## AI Life Insurance Sales Agent Application

**Version**: 1.0  
**Last Updated**: [Date]  
**Authors**: Architecture Team  
**Status**: Draft

---

## Table of Contents

1. [Document Purpose](#document-purpose)
2. [System Overview](#system-overview)
3. [Architecture Principles](#architecture-principles)
4. [High-Level Architecture](#high-level-architecture)
5. [Component Architecture](#component-architecture)
6. [Technology Stack](#technology-stack)
7. [System Boundaries and Interfaces](#system-boundaries-and-interfaces)
8. [Data Flow Architecture](#data-flow-architecture)
9. [Integration Architecture](#integration-architecture)
10. [Scalability and Performance](#scalability-and-performance)
11. [Security Architecture](#security-architecture)
12. [Deployment Architecture](#deployment-architecture)
13. [Infrastructure Requirements](#infrastructure-requirements)

---

## Document Purpose

This document defines the system architecture for the AI Life Insurance Sales Agent Application. It provides a comprehensive overview of the system's structure, components, technology choices, and design decisions that guide the development team.

**Intended Audience**:
- Development team
- Technical leads
- System architects
- DevOps engineers
- Project managers

---

## System Overview

### 2.1 System Purpose

The AI Life Insurance Sales Agent is a conversational AI application that:
- Conducts natural, persuasive conversations with potential customers
- Provides information about **a specific insurance company's life insurance policies** using a **custom knowledge base (RAG-based)**
- Identifies interested prospects and collects lead information
- Stores leads and conversation logs for sales team follow-up

### 2.2 Key System Characteristics

- **Real-time conversational AI**: Uses LLM for natural language understanding and generation
- **RAG-Based Knowledge Base**: Uses Retrieval Augmented Generation (RAG) with vector database for semantic search of company-specific policy information
- **Custom Policy Knowledge Base**: Configured with the specific insurance company's policy documents, terms, and information
- **Stateful conversations**: Maintains conversation context throughout sessions
- **Lead generation focus**: Designed to convert conversations into qualified leads
- **Text-based (Phase 1)**: Initial implementation supports text interactions only
- **Scalable**: Designed to handle multiple concurrent conversations

### 2.3 Why RAG Architecture?

**Retrieval Augmented Generation (RAG) is the recommended architecture** for this application because:

1. **Semantic Search**: Enables natural language queries to find relevant policies (e.g., "policies for young families" finds term life policies even if customer doesn't mention "term life")
2. **Accurate Information**: Retrieves actual policy documents and details from the knowledge base, reducing hallucinations
3. **Easy Updates**: New policies or policy changes can be ingested into the vector database without code changes
4. **Context-Aware Responses**: LLM receives relevant policy context, enabling more accurate and specific answers
5. **Scalability**: Vector databases efficiently handle semantic search across large policy document collections
6. **Company-Specific**: Perfect fit for a custom knowledge base containing one insurance company's policies

**Alternative Approaches Considered**:
- **Rule-Based Matching**: Too rigid, requires constant updates, doesn't handle natural language queries well
- **Traditional Database Queries**: Limited to exact matches, doesn't understand semantic similarity
- **LLM Without RAG**: Higher risk of hallucinations, no way to ensure policy accuracy, harder to update

**Conclusion**: RAG provides the best balance of accuracy, flexibility, and maintainability for company-specific policy information retrieval.

### 2.3 System Context

```
┌─────────────────────────────────────────────────────────────┐
│                    External Systems                         │
├─────────────────────────────────────────────────────────────┤
│  • LLM API (OpenAI/Anthropic/Claude)                        │
│  • Customer Access (Web Browser/Chat Interface)             │
│  • Admin Users (Web Dashboard)                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              AI Life Insurance Sales Agent                  │
│                    Application                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Data Storage                               │
├─────────────────────────────────────────────────────────────┤
│  • Database (PostgreSQL/SQLite) - Leads, Conversations      │
│  • Vector Database (Chroma/Pinecone/FAISS) - Policy KB      │
│  • File Storage (Optional - Text/JSON)                      │
│  • Session Cache (Redis)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture Principles

### 3.1 Design Principles

1. **Modularity**: System designed as loosely coupled, independently deployable modules
2. **Scalability**: Architecture supports horizontal scaling for increased load
3. **Reliability**: Designed for high availability (99% uptime target)
4. **Security**: Security-first approach with encryption and access controls
5. **Maintainability**: Clean code, documentation, and testability
6. **Performance**: Response time target < 2 seconds for customer messages
7. **Flexibility**: Support for multiple LLM providers and deployment options

### 3.2 Architectural Patterns

- **Layered Architecture**: Separation of concerns across layers
- **API Gateway Pattern**: Single entry point for all requests
- **Repository Pattern**: Data access abstraction
- **Service Layer Pattern**: Business logic encapsulation
- **Session State Pattern**: Conversation state management
- **Microservices-Ready**: Can be decomposed into services if needed

---

## High-Level Architecture

### 4.1 System Layers

```
┌──────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Web Chat UI │  │  Admin UI    │  │  REST API    │        │
│  │  (React/Vue) │  │  (Dashboard) │  │  Endpoints   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Conversation │  │ Lead Mgmt    │  │ Policy Mgmt  │        │
│  │   Service    │  │   Service    │  │   Service    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Session    │  │  Validation  │  │   Admin      │        │
│  │   Manager    │  │   Service    │  │   Service    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    AI/LLM Integration Layer                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  LLM Client  │  │  Prompt      │  │ Context      │        │
│  │  (Adapter)   │  │  Manager     │  │  Manager     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Response    │  │  Intent      │  │  RAG         │        │
│  │  Filter      │  │  Detection   │  │  Retriever   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Knowledge Base Layer (RAG)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Embedding   │  │  Vector      │  │  Document    │        │
│  │  Generator   │  │  Search      │  │  Ingestor    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│  ┌──────────────┐                                            │
│  │  Policy      │                                            │
│  │  Knowledge   │                                            │
│  │  Base        │                                            │
│  └──────────────┘                                            │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Data Access Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Lead        │  │  Conversation│  │  Policy      │        │
│  │  Repository  │  │  Repository  │  │  Repository  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  PostgreSQL  │  │    Redis     │  │ File Storage │        │
│  │  / SQLite    │  │  (Sessions)  │  │  (Optional)  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└──────────────────────────────────────────────────────────────┘
```

### 4.2 Component Overview

#### 4.2.1 Presentation Layer
- **Web Chat Interface**: Customer-facing chat UI (React/Vue.js)
- **Admin Dashboard**: Management interface for leads and policies
- **REST API**: Programmatic access for integrations

#### 4.2.2 Application Layer
- **Conversation Service**: Core conversation orchestration
- **Lead Management Service**: Lead CRUD operations and validation
- **Policy Management Service**: Policy information management
- **Session Manager**: Conversation session state management
- **Validation Service**: Data validation and sanitization
- **Admin Service**: Administrative operations

#### 4.2.3 AI/LLM Integration Layer
- **LLM Client**: Abstraction for multiple LLM providers
- **Prompt Manager**: System prompt and template management
- **Context Manager**: Conversation context window management
- **Response Filter**: Safety and content filtering
- **Intent Detection**: Customer intent classification
- **RAG Retriever**: Retrieves relevant policy documents from knowledge base using semantic search

#### 4.2.4 Knowledge Base Layer (RAG)
- **Document Ingestor**: Ingests policy documents into vector database
- **Embedding Generator**: Converts policy documents to vector embeddings
- **Vector Search**: Performs semantic similarity search on policy knowledge base
- **Policy Knowledge Base**: Vector database containing company-specific policy documents and information

#### 4.2.4 Agent Orchestration (LangGraph)
- **LangGraph Conversation Graph**: State machine built from nodes in `graph/nodes`
- **Runnable Pipelines**: LangChain-powered planner/retriever/action chains in `chains/`
- **State & Memory**: Typed conversation state and memory policies under `state/`
- **Tooling Integrations**: MCP clients and tool specifications under `tools/`
- **Observability**: LangSmith tracing and evaluation harness in `observability/`
- **API Integration**: FastAPI entrypoint in `apps/api` composes the graph; the legacy `app/src` stack has been deprecated

#### 4.2.4 Data Access Layer
- **Repositories**: Data access abstraction (Leads, Conversations, Policies)

#### 4.2.5 Data Storage Layer
- **PostgreSQL/SQLite**: Primary database for leads, conversations, metadata
- **Vector Database**: Policy knowledge base (Chroma, Pinecone, FAISS, or similar)
- **Redis**: Session and cache storage
- **File Storage**: Optional text/JSON file storage (Phase 1)

---

## Component Architecture

### 5.1 Conversation Service

**Responsibilities**:
- Orchestrate conversation flow
- Manage conversation state transitions
- Coordinate between LLM and other services
- Handle conversation lifecycle (start, continue, end)

**Key Operations**:
- `startConversation()`: Initialize new conversation session
- `processMessage(userMessage)`: Process customer message and generate response
- `endConversation()`: Gracefully end conversation and save logs
- `detectIntent(message)`: Analyze customer intent
- `detectInterest()`: Identify buying signals

**Dependencies**:
- LLM Integration Layer
- Session Manager
- Policy Management Service
- Validation Service

### 5.2 LLM Integration Component

**Responsibilities**:
- Interface with LLM APIs (OpenAI, Anthropic, etc.)
- Manage prompt templates and system prompts
- Handle context window management
- Implement response filtering and safety checks
- Manage API rate limiting and retries

**Key Operations**:
- `generateResponse(context, userMessage)`: Generate AI response
- `updateContext(messages)`: Manage conversation context
- `detectIntent(message)`: Intent classification
- `filterResponse(response)`: Safety/content filtering

**LLM Provider Abstraction**:
```python
class LLMProvider:
    def generate(self, messages: List[Message], config: LLMConfig) -> Response
    def classify_intent(self, message: str) -> Intent
    def extract_entities(self, message: str) -> Dict[str, Any]
```

### 5.3 Session Manager

**Responsibilities**:
- Manage conversation sessions
- Store conversation state
- Track conversation metadata
- Handle session expiration

**Storage Options**:
- **In-Memory**: Fast, but lost on restart (development)
- **Redis**: Persistent, scalable, recommended for production

**Session Data Structure**:
```json
{
  "session_id": "uuid",
  "conversation_id": "uuid",
  "customer_profile": {},
  "collected_data": {},
  "conversation_stage": "qualification|information|persuasion|collection",
  "message_history": [],
  "context_summary": "",
  "created_at": "timestamp",
  "last_activity": "timestamp"
}
```

### 5.4 Lead Management Service

**Responsibilities**:
- Store lead information
- Validate lead data
- Handle duplicate detection
- Provide lead retrieval and filtering
- Support lead export

**Key Operations**:
- `createLead(leadData)`: Create new lead
- `validateLeadData(data)`: Validate lead information
- `checkDuplicate(phone, nid)`: Detect duplicate leads
- `getLeads(filters)`: Retrieve leads with filtering
- `exportLeads(format, filters)`: Export leads to file

### 5.5 Policy Management Service

**Responsibilities**:
- Manage policy knowledge base (RAG-based)
- Retrieve policies using semantic search
- Match policies to customer needs
- Provide policy comparisons
- Ingest new policy documents into knowledge base

**Key Operations**:
- `searchPolicies(query, customerProfile)`: Semantic search for relevant policies from knowledge base
- `getPolicyDetails(policyId)`: Get full policy information from knowledge base
- `comparePolicies(policyIds)`: Compare multiple policies
- `ingestPolicyDocument(document, metadata)`: Add new policy document to knowledge base
- `updatePolicyDocument(policyId, document)`: Update existing policy in knowledge base

**RAG Integration**:
- Uses vector database for semantic search
- Retrieves top-k relevant policy documents based on customer query
- Provides retrieved context to LLM for accurate policy information

### 5.6 Data Access Layer (Repositories)

**Responsibilities**:
- Abstract database operations
- Handle data mapping
- Manage transactions
- Provide query optimization

**Repository Pattern**:
```python
class LeadRepository:
    def create(self, lead: Lead) -> Lead
    def find_by_id(self, id: str) -> Lead
    def find_by_phone(self, phone: str) -> Optional[Lead]
    def find_all(self, filters: Dict) -> List[Lead]
    def update(self, lead: Lead) -> Lead
```

---

## Technology Stack

### 6.1 Recommended Technology Stack

#### 6.1.1 Backend Framework

**Primary Choice: Python with FastAPI**

**Rationale**:
- Excellent LLM integration libraries
- FastAPI provides async support for LLM API calls
- Strong ecosystem for AI/ML
- Good performance
- Automatic API documentation

**Alternative: Node.js with Express**
- Faster for I/O-bound operations
- Good for real-time features
- JavaScript ecosystem

#### 6.1.2 LLM Provider

**Primary Options**:
1. **OpenAI GPT-4/GPT-3.5**
   - Pros: Best performance, reliable, extensive documentation
   - Cons: Cost, rate limits
2. **Anthropic Claude**
   - Pros: Excellent safety, long context windows
   - Cons: Slightly higher cost
3. **Local LLM (Ollama, Llama, etc.)**
   - Pros: No API costs, data privacy
   - Cons: Lower performance, requires infrastructure

**Recommendation**: Start with OpenAI GPT-4 or Claude, implement provider abstraction for flexibility

#### 6.1.3 Database

**Primary: PostgreSQL**
- Production-ready
- Excellent performance
- JSON support for flexible schemas
- ACID compliance

**Development: SQLite**
- Zero configuration
- Good for local development
- Easy migration path to PostgreSQL

#### 6.1.4 Vector Database (Knowledge Base)

**Primary Options for Policy Knowledge Base**:

1. **Chroma** (Recommended for Development)
   - Pros: Easy setup, Python-native, open source, good for local development
   - Cons: Limited scalability for very large datasets
   - Best for: Development and small to medium production deployments

2. **Pinecone** (Recommended for Production)
   - Pros: Managed service, highly scalable, production-ready, fast
   - Cons: Cost, external dependency
   - Best for: Production environments with high traffic

3. **FAISS (Facebook AI Similarity Search)**
   - Pros: Very fast, open source, good performance
   - Cons: Requires more setup, in-memory or file-based
   - Best for: High-performance requirements, on-premise deployments

4. **Qdrant**
   - Pros: Open source, scalable, good API
   - Cons: Requires self-hosting setup
   - Best for: Production with self-hosted infrastructure

**Embedding Models**:

**For Local Development (FREE - Recommended):**
- **Sentence Transformers (all-MiniLM-L6-v2)**: 
  - ✅ **100% FREE** - No API costs, no usage limits
  - ✅ Open source, runs locally on your machine
  - ✅ Good quality for development (384-dimensional embeddings)
  - ✅ Fast inference on CPU, no internet required
  - ✅ Installation: `pip install sentence-transformers`
  - ✅ Model size: ~80MB (downloads automatically on first use)

**For Production (Recommended):**
- **Voyage AI voyage-3.5-lite**: 
  - ✅ **Recommended for production** - Excellent quality and cost efficiency
  - ✅ High-quality embeddings (supports 256, 512, 1024, 2048 dimensions)
  - ✅ Optimized for retrieval tasks
  - ✅ Lower cost than OpenAI with better performance
  - ✅ Supports input_type parameter ("document" vs "query") for better retrieval
  - ✅ Installation: `pip install voyageai`
  - ✅ Requires: `VOYAGE_API_KEY` environment variable

**For Production (Alternative):**
- **OpenAI text-embedding-3-small** or **text-embedding-ada-002**: 
  - Excellent quality, requires API key (~$0.02 per 1M tokens)
  - Can be used as alternative to Voyage AI
  - Requires: `OPENAI_API_KEY` environment variable

**Provider Switching:**
- All providers use the same `EmbeddingService` interface
- Switch via environment variable: `EMBEDDING_PROVIDER=sentence_transformers|voyage|openai`
- No code changes needed when switching providers

**Recommendation**: 
- **Development**: Use Sentence Transformers (FREE) - perfect for local development with zero costs
- **Production**: Use Voyage AI voyage-3.5-lite (recommended) - best balance of quality and cost
- **Alternative**: OpenAI embeddings if Voyage AI not available

#### 6.1.5 Session/Cache Store

**Redis**
- Fast in-memory storage
- Pub/sub for real-time features
- Session management
- Caching

**Alternative (Development): In-Memory**
- Simple for local development
- No infrastructure required

#### 6.1.6 Frontend Framework

**Primary: React with TypeScript**
- Component-based architecture
- Rich ecosystem
- Good performance
- Strong typing

**Alternative: Vue.js**
- Easier learning curve
- Good documentation

#### 6.1.7 Additional Technologies

- **Authentication**: JWT tokens
- **API Documentation**: OpenAPI/Swagger (FastAPI auto-generates)
- **Logging**: Structured logging (Python logging or Winston)
- **Monitoring**: Prometheus, Grafana (optional Phase 1)
- **Error Tracking**: Sentry (optional Phase 1)
- **Containerization**: Docker
- **Orchestration**: Docker Compose (Phase 1), Kubernetes (future)

### 6.2 Technology Stack Summary

```
Frontend:
├── React + TypeScript
├── WebSocket client (for real-time)
└── UI Library (Material-UI or Tailwind CSS)

Backend:
├── Python 3.11+
├── FastAPI
├── AsyncIO (for LLM API calls)
├── SQLAlchemy (ORM)
└── Pydantic (data validation)

AI/LLM:
├── OpenAI Python SDK / Anthropic SDK
├── LangGraph (agent orchestration)
├── LangChain (runnables, retrievers)
└── Prompt engineering framework

Knowledge Base (RAG):
├── Vector Database (Chroma/Pinecone/Qdrant)
├── Embedding Model (OpenAI/Sentence Transformers)
├── Document Processing (chunking, metadata extraction)
└── Semantic Search Engine

Database:
├── PostgreSQL (production) - Leads, conversations, metadata
├── SQLite (development) - Leads, conversations, metadata
├── Vector Database - Policy knowledge base
└── Redis (session/cache)

Infrastructure:
├── Docker
├── Docker Compose
└── Nginx (reverse proxy, optional)
```

### 6.3 Codebase Layout

```
lic-agent/
├── app/                      # Application code
│   ├── src/                  # FastAPI source code
│   ├── tests/                # Tests
│   ├── alembic/              # Database migrations
│   ├── alembic.ini           # Alembic configuration
│   └── scripts/              # Code-related scripts
├── requirements.txt          # Project dependencies (root)
├── docker-compose.yml        # Docker services
├── .env.docker.example       # Environment template
├── docs/                     # Developer documentation
└── architecture-and-design/  # Architecture documents
```

Notes:
- Run app from `app/`:
  - Start: `cd app && uvicorn src.main:app --reload --port 8000`
  - Migrations: `cd app && alembic upgrade head`
- From root using PYTHONPATH:
  - `PYTHONPATH=app uvicorn app.src.main:app --reload --port 8000`

---

## System Boundaries and Interfaces

### 7.1 External Interfaces

#### 7.1.1 LLM Provider API

**Interface**: REST API (HTTP/HTTPS)

**Providers**:
- OpenAI: `https://api.openai.com/v1/chat/completions`
- Anthropic: `https://api.anthropic.com/v1/messages`

**Interaction Pattern**:
- Synchronous API calls
- Async handling in backend
- Retry logic with exponential backoff
- Rate limiting handling

#### 7.1.2 Customer Interface

**Interface**: Web-based chat application

**Protocol**: 
- REST API for message exchange
- WebSocket (optional) for real-time updates
- HTTP/HTTPS

**Endpoints**:
- `POST /api/conversation/start`
- `POST /api/conversation/message`
- `GET /api/conversation/{session_id}`
- `POST /api/conversation/end`

#### 7.1.3 Admin Interface

**Interface**: Web-based admin dashboard

**Protocol**: REST API

**Endpoints**:
- Lead management: `GET/POST/PUT /api/leads`
- Conversation viewing: `GET /api/conversations/{id}`
- Policy management: `GET/POST/PUT /api/policies`
- Export: `GET /api/leads/export`

### 7.2 Internal Interfaces

#### 7.2.1 Service-to-Service Communication

**Pattern**: Direct function calls (monolithic Phase 1) or REST/gRPC (if microservices)

**Phase 1**: Synchronous function calls within same process

**Future**: Consider message queue (RabbitMQ, Kafka) for async processing

#### 7.2.2 Database Interface

**Pattern**: Repository Pattern with ORM (SQLAlchemy)

**Access Control**: Application-level (no direct database access from external)

---

## Data Flow Architecture

### 8.1 Conversation Message Flow

```
Customer Message
       │
       ▼
┌──────────────┐
│  Chat UI     │
└──────────────┘
       │
       ▼ HTTP POST /api/conversation/message
┌──────────────┐
│  API Gateway │
└──────────────┘
       │
       ▼
┌──────────────┐
│ Conversation │
│   Service    │
└──────────────┘
       │
       ├──► Session Manager (load context)
       │
       ▼
┌──────────────┐
│ Context      │
│ Manager      │
└──────────────┘
       │
       ▼ Build context (messages + profile + policies)
┌──────────────┐
│ LLM Client   │
│  (Adapter)   │
└──────────────┘
       │
       ▼ HTTP POST to LLM API
┌──────────────┐
│ LLM Provider │
│  (External)  │
└──────────────┘
       │
       ▼ Response
┌──────────────┐
│ Response     │
│ Filter       │
└──────────────┘
       │
       ├──► Session Manager (save message + context)
       ├──► Conversation Repository (log message)
       │
       ▼
┌──────────────┐
│  Conversation│
│   Service    │
└──────────────┘
       │
       ├──► Detect Intent/Interest
       │    ├──► If Interest: Lead Management Service
       │    └──► If Exit: End conversation
       │
       ▼
┌──────────────┐
│  API Gateway │
└──────────────┘
       │
       ▼ HTTP Response
┌──────────────┐
│  Chat UI     │
└──────────────┘
       │
       ▼ Display to Customer
```

### 8.2 Lead Collection Flow

```
Interest Detected
       │
       ▼
┌──────────────┐
│ Conversation │
│   Service    │
└──────────────┘
       │
       ├──► Start Information Collection
       │
       ▼
┌──────────────┐
│ Lead Mgmt    │
│   Service    │
└──────────────┘
       │
       ├──► Collect Fields Sequentially
       │    ├──► Name
       │    ├──► Phone (validate format)
       │    ├──► NID (validate format)
       │    ├──► Address (validate completeness)
       │    └──► Policy Interest
       │
       ├──► Validation Service
       │    ├──► Format validation
       │    └──► Duplicate check
       │
       ├──► Confirm with Customer
       │
       ▼
┌──────────────┐
│ Lead         │
│ Repository   │
└──────────────┘
       │
       ├──► Save to Database
       ├──► Save to File (optional)
       └──► Link to Conversation
```

### 8.3 Policy Information Retrieval Flow (RAG-Based)

```
Customer asks about policies
       │
       ▼
┌──────────────┐
│ Conversation │
│   Service    │
└──────────────┘
       │
       ├──► Get Customer Profile
       │
       ▼
┌──────────────┐
│ Policy       │
│  Service     │
└──────────────┘
       │
       ├──► Build semantic query from:
       │    ├──► Customer message/question
       │    ├──► Customer profile (age, needs, etc.)
       │    └──► Conversation context
       │
       ▼
┌──────────────┐
│  RAG         │
│  Retriever   │
└──────────────┘
       │
       ├──► Generate query embedding
       │
       ▼
┌──────────────┐
│  Embedding   │
│  Generator   │
└──────────────┘
       │
       ▼
┌──────────────┐
│  Vector      │
│  Search      │
└──────────────┘
       │
       ▼ Semantic similarity search
┌──────────────┐
│  Vector      │
│  Database    │
│  (Policy KB) │
└──────────────┘
       │
       ▼ Top-k relevant policy documents
┌──────────────┐
│  RAG         │
│  Retriever   │
└──────────────┘
       │
       ▼ Retrieved context (policy documents + metadata)
┌──────────────┐
│ Policy       │
│  Service     │
└──────────────┘
       │
       ├──► Format retrieved policies
       ├──► Add customer-specific context
       │
       ▼
┌──────────────┐
│ LLM Client   │
│(RAG-Augmented│
│ Generation)  │
└──────────────┘
       │
       ├──► Prompt includes:
       │    ├──► Customer query
       │    ├──► Retrieved policy context
       │    ├──► Customer profile
       │    └──► Conversation history
       │
       ▼
┌──────────────┐
│  LLM Provider│
│  (External)  │
└──────────────┘
       │
       ▼ Accurate, context-aware response
┌──────────────┐
│ Conversation │
│   Service    │
└──────────────┘
```

---

## Knowledge Base Architecture (RAG)

### 9.1 Knowledge Base Overview

The Policy Knowledge Base is the core component that stores and retrieves company-specific life insurance policy information using RAG (Retrieval Augmented Generation). It enables the system to provide accurate, up-to-date policy information through semantic search.

### 9.2 Knowledge Base Components

```
┌─────────────────────────────────────────────────────────────┐
│              Knowledge Base Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │           Document Ingestion Pipeline              │     │
│  │                                                    │     │
│  │  Policy Documents → Chunking → Embedding → Vector  │     │
│  │      (PDF/Text)      (Split)   (Generate)  (Store) │     │
│  └────────────────────────────────────────────────────┘     │
│                            │                                │
│                            ▼                                │
│  ┌────────────────────────────────────────────────────┐     │
│  │              Vector Database                       │     │
│  │  ┌──────────────┐  ┌──────────────┐                │     │
│  │  │  Embeddings  │  │  Metadata    │                │     │
│  │  │  (Vectors)   │  │  (Policy Info)│               │     │
│  │  └──────────────┘  └──────────────┘                │     │
│  └────────────────────────────────────────────────────┘     │
│                            │                                │
│                            ▼                                │
│  ┌────────────────────────────────────────────────────┐     │
│  │           Query Retrieval Pipeline                 │     │
│  │                                                    │     │
│  │  Query → Embedding → Vector Search → Top-K Results │     │
│  │    (User)    (Generate)   (Similarity)   (Retrieve)│     │
│  └────────────────────────────────────────────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 Document Ingestion Process

#### 9.3.1 Document Sources

**Policy Documents to Ingest**:
- Policy brochures and fact sheets
- Terms and conditions documents
- Policy comparison charts
- Premium calculation guides
- Benefits and features documentation
- Eligibility requirements
- Claim process documents
- FAQ documents

**Document Formats Supported**:
- PDF files
- Markdown/text files
- Structured JSON/CSV (policy metadata)
- Web pages (scraped content)

#### 9.3.2 Document Processing Pipeline

1. **Document Loading**: Load policy documents from source (file system, API, database)
2. **Text Extraction**: Extract text from PDFs, web pages, etc.
3. **Chunking**: Split documents into smaller chunks (500-1000 tokens) with overlap
4. **Metadata Extraction**: Extract metadata (policy name, type, coverage range, etc.)
5. **Embedding Generation**: Generate vector embeddings for each chunk
6. **Vector Storage**: Store embeddings and metadata in vector database

**Chunking Strategy**:
- **Size**: 500-1000 tokens per chunk
- **Overlap**: 100-200 tokens between chunks (to preserve context)
- **Boundaries**: Split at sentence or paragraph boundaries when possible
- **Metadata**: Each chunk includes reference to source document and position

### 9.4 Retrieval Process

#### 9.4.1 Query Construction

When a customer asks about policies, the system constructs a semantic query:

```
Base Query: Customer's original message/question
+ Customer Profile Context: Age, needs, family situation
+ Conversation Context: Previously discussed policies/interests
= Enhanced Query for Retrieval
```

**Example**:
- Customer: "What policies do you have for young families?"
- Enhanced Query: "life insurance policies for young families with children, term life insurance, family protection coverage, affordable premiums"

#### 9.4.2 Semantic Search Process

1. **Query Embedding**: Convert enhanced query to vector embedding
2. **Similarity Search**: Find top-k most similar policy document chunks (k=3-5)
3. **Re-ranking** (Optional): Re-rank results using metadata filters (age eligibility, etc.)
4. **Context Assembly**: Combine retrieved chunks with metadata into context

#### 9.4.3 Retrieval Parameters

- **Top-K**: Retrieve 3-5 most relevant policy chunks per query
- **Similarity Threshold**: Minimum similarity score (e.g., 0.7) to include result
- **Metadata Filtering**: Filter by policy type, age eligibility, active status
- **Diversity**: Ensure retrieved chunks represent different policies when relevant

### 9.5 RAG Integration with LLM

#### 9.5.1 Context Injection

Retrieved policy context is injected into the LLM prompt:

```
System Prompt:
You are an AI life insurance sales agent for [Company Name].
You have access to the following policy information:

[Retrieved Policy Context - 1]
Policy: Term Life 20 Year
Coverage: $50,000 - $1,000,000
Premium Range: $50-$200/month
Benefits: ...
...

[Retrieved Policy Context - 2]
...

Customer Profile: {customer_profile}
Conversation History: {recent_messages}

Answer the customer's question using ONLY the information from the retrieved policies above.
If the information is not in the retrieved context, say you don't have that information.
```

#### 9.5.2 Response Generation

- LLM generates response based on retrieved policy context
- Response is grounded in actual policy documents (reduces hallucinations)
- LLM can cite specific policies and reference retrieved information
- Response includes relevant policy details from knowledge base

### 9.6 Knowledge Base Management

#### 9.6.1 Adding New Policies

**Process**:
1. Admin uploads policy document (PDF, text, etc.)
2. Document goes through ingestion pipeline
3. New embeddings generated and stored
4. Metadata updated in database
5. Knowledge base version incremented

#### 9.6.2 Updating Existing Policies

**Process**:
1. Identify policy document(s) to update
2. Mark old chunks as deprecated (don't delete immediately)
3. Ingest updated document as new version
4. Update metadata with version timestamp
5. Gradually deprecate old versions after verification

#### 9.6.3 Version Control

- Maintain version history of policy documents
- Track when policies were added/updated
- Enable rollback if needed
- Audit trail for policy changes

### 9.7 Knowledge Base Quality Assurance

#### 9.7.1 Quality Checks

- **Coverage**: Ensure all active policies are in knowledge base
- **Accuracy**: Verify retrieved information matches source documents
- **Completeness**: Check that policy details are not fragmented across chunks
- **Freshness**: Regular updates when policies change

#### 9.7.2 Testing

- **Retrieval Testing**: Test queries to ensure relevant policies are retrieved
- **Accuracy Testing**: Verify LLM responses match policy documents
- **Coverage Testing**: Ensure all policy types are retrievable
- **Performance Testing**: Measure retrieval latency (target: <200ms)

### 9.8 Implementation Options

#### Option 1: Chroma (Development/Simple Production)

**Setup**:
```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("policy_knowledge_base")

# Store embeddings
collection.add(
    embeddings=policy_embeddings,
    documents=policy_chunks,
    metadatas=policy_metadata,
    ids=policy_ids
)

# Query
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)
```

**Pros**: Simple, Python-native, good for development
**Cons**: Limited scalability

#### Option 2: Pinecone (Production/Managed)

**Setup**:
- Managed service, no infrastructure to maintain
- Highly scalable, fast retrieval
- Pay-per-use pricing

**Pros**: Production-ready, scalable, managed
**Cons**: External dependency, cost

#### Option 3: Qdrant (Self-Hosted Production)

**Setup**:
- Self-hosted vector database
- Docker deployment
- Good performance and scalability

**Pros**: Self-hosted, open source, scalable
**Cons**: Requires infrastructure management

**Recommendation**: Start with Chroma for development, migrate to Pinecone or Qdrant for production based on scale requirements.

---

## Integration Architecture

### 9.1 LLM Integration

#### 9.1.1 Provider Abstraction

**Design Pattern**: Adapter Pattern

```python
# Abstract LLM Provider Interface
class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[Message],
        config: LLMConfig
    ) -> LLMResponse
    
    @abstractmethod
    async def classify_intent(self, message: str) -> Intent
    
    @abstractmethod
    async def extract_entities(self, message: str) -> Dict[str, Any]

# Concrete Implementations
class OpenAIProvider(LLMProvider): ...
class AnthropicProvider(LLMProvider): ...
class LocalLLMProvider(LLMProvider): ...
```

#### 9.1.2 Prompt Management

**System Prompt Structure**:
```
You are an AI life insurance sales agent for [Company Name].
Your role is to:
1. Help customers understand life insurance options
2. Provide information about policies
3. Build rapport and trust
4. Identify interested prospects
5. Collect information from interested customers

Guidelines:
- Be professional, friendly, and empathetic
- Use persuasive techniques naturally
- Be transparent that you're an AI
- Respect customer's decisions
- Follow conversation stages: introduction → qualification → information → persuasion → collection

Current customer profile:
{customer_profile}

Available policies:
{available_policies}
```

**Context Window Management**:
- Maximum context: 50-100 previous messages (depending on LLM)
- Summarization strategy for long conversations
- Key information preservation (customer profile, collected data)

#### 9.1.3 Error Handling

- Retry logic: 3 attempts with exponential backoff
- Fallback responses if LLM unavailable
- Rate limiting handling
- Timeout management (10-30 seconds)

### 9.2 Database Integration

#### 9.2.1 Connection Management

- Connection pooling for PostgreSQL
- Transaction management
- Migration strategy (Alembic for SQLAlchemy)

#### 9.2.2 Data Models

- Lead model
- Conversation model
- Message model
- Policy model

### 9.3 External API Integration

#### 9.3.1 API Client Pattern

```python
class APIClient:
    def __init__(self, base_url: str, api_key: str)
    async def request(self, method: str, endpoint: str, **kwargs)
    def handle_retry(self, response)
    def handle_rate_limit(self, response)
```

---

## Scalability and Performance

### 10.1 Scalability Strategy

#### 10.1.1 Horizontal Scaling

**Approach**: Stateless application design
- Sessions stored in Redis (external to app)
- Database shared across instances
- Load balancer distributes requests

**Scaling Triggers**:
- CPU usage > 70%
- Response time > 2 seconds
- Queue depth increasing

#### 10.1.2 Vertical Scaling

- Increase instance size for initial scaling
- Database scaling (read replicas if needed)

#### 10.1.3 Caching Strategy

- **Policy data**: Cache in Redis (TTL: 1 hour)
- **Session data**: Redis
- **LLM responses**: Optional caching (not recommended for personalized responses)

### 10.2 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time | < 2 seconds | 95th percentile |
| LLM API Call Time | < 5 seconds | Per request |
| Database Query Time | < 100ms | Average |
| Concurrent Conversations | 100+ | Per instance |
| System Uptime | 99% | Monthly |

### 10.3 Performance Optimization

1. **Async Operations**: Use async/await for LLM API calls
2. **Connection Pooling**: Database connection pooling
3. **Caching**: Redis for frequently accessed data
4. **Database Indexing**: Indexes on phone, NID, session_id
5. **Query Optimization**: Efficient queries, avoid N+1 problems
6. **Response Streaming**: Consider streaming LLM responses (Phase 2)

---

## Security Architecture

### 11.1 Security Layers

```
┌─────────────────────────────────────┐
│     Transport Security (HTTPS)     │
├─────────────────────────────────────┤
│     Authentication (JWT)            │
├─────────────────────────────────────┤
│     Authorization (RBAC)             │
├─────────────────────────────────────┤
│     Data Encryption (At Rest)       │
├─────────────────────────────────────┤
│     Input Validation & Sanitization │
├─────────────────────────────────────┤
│     Rate Limiting                   │
└─────────────────────────────────────┘
```

### 11.2 Authentication and Authorization

**Customer Access**:
- Session-based (no login required for chat)
- Optional: Rate limiting by IP

**Admin Access**:
- JWT token authentication
- Role-based access control (RBAC)
- Admin role required for sensitive operations

### 11.3 Data Protection

**Encryption**:
- **In Transit**: TLS 1.2+ (HTTPS)
- **At Rest**: Database encryption for sensitive fields (NID, phone)
- **Sensitive Fields**: Encrypt before storing (AES-256)

**Data Masking**:
- Mask phone numbers in admin list view
- Full details only in detail view with proper permissions

### 11.4 Input Validation and Sanitization

- Validate all inputs
- Sanitize user messages before LLM processing
- SQL injection prevention (use ORM)
- XSS prevention in web interface

### 11.5 Security Best Practices

- Environment variables for secrets (API keys, DB credentials)
- No secrets in code or configuration files
- Regular security updates
- Security audit logging
- Rate limiting on API endpoints
- CORS configuration for web interface

---

## Deployment Architecture

### 12.1 Deployment Options

#### 12.1.1 Phase 1: Simple Deployment

```
┌──────────────────────────────────────┐
│         Docker Compose               │
│  ┌────────────┐  ┌────────────┐     │
│  │  Backend   │  │  Frontend  │     │
│  │  (FastAPI) │  │  (React)   │     │
│  └────────────┘  └────────────┘     │
│  ┌────────────┐  ┌────────────┐     │
│  │ PostgreSQL │  │   Redis    │     │
│  └────────────┘  └────────────┘     │
└──────────────────────────────────────┘
```

**Environment**: Single server or cloud VM

**Benefits**:
- Simple setup
- Easy local development
- Cost-effective for Phase 1

#### 12.1.2 Future: Production Deployment

```
┌──────────────────────────────────────┐
│        Load Balancer (Nginx)         │
└──────────────────────────────────────┘
           │         │
      ┌────┘         └────┐
      ▼                   ▼
┌────────────┐      ┌────────────┐
│  Backend   │      │  Backend   │
│ Instance 1 │      │ Instance 2 │
└────────────┘      └────────────┘
      │                   │
      └─────────┬─────────┘
                ▼
    ┌──────────────────────┐
    │   Database          │
    │  (PostgreSQL)       │
    └──────────────────────┘
    ┌──────────────────────┐
    │   Redis Cluster     │
    └──────────────────────┘
```

### 12.2 Containerization

**Docker Strategy**:
- Multi-stage builds for optimization
- Separate containers: backend, frontend, database, redis
- Docker Compose for orchestration (Phase 1)
- Kubernetes-ready (future)

### 12.3 Environment Configuration

**Environments**:
- Development (local)
- Staging (testing)
- Production

**Configuration Management**:
- Environment variables
- Configuration files (non-sensitive)
- Secrets management (environment variables or secret manager)

---

## Infrastructure Requirements

### 13.1 Phase 1 Infrastructure

**Minimum Requirements**:
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 20 GB
- **Network**: Stable internet connection for LLM API calls

**Recommended**:
- **CPU**: 4 cores
- **RAM**: 8 GB
- **Storage**: 50 GB (SSD)
- **Network**: High-speed, low-latency connection

### 13.2 Database Requirements

**PostgreSQL**:
- Version: 13+ (or SQLite for development)
- Storage: Based on expected lead volume
- Backup: Daily automated backups

**Vector Database (Knowledge Base)**:
- **Chroma** (Development): Local file-based, minimal setup required
- **Pinecone** (Production): Managed service, no infrastructure needed
- **Qdrant** (Self-hosted): Docker container, 2-4 GB RAM recommended
- **Storage**: Depends on policy document volume (typically 100MB-1GB for small to medium policy sets)
- **Embedding Model**: OpenAI API or local model (sentence-transformers)

**Redis**:
- Version: 6+
- Memory: 1-2 GB (depends on session count)
- Persistence: Optional (RDB snapshots)

### 13.3 Network Requirements

- HTTPS endpoint (port 443)
- HTTP endpoint (port 80) redirects to HTTPS
- WebSocket support (optional, for real-time)
- Outbound access to LLM API providers

### 13.4 Monitoring and Logging

**Logging**:
- Application logs (structured JSON)
- Error logs
- Access logs
- LLM API call logs

**Monitoring** (Optional Phase 1):
- Application health endpoints
- Database connection monitoring
- LLM API response time tracking
- Error rate tracking

---

## Architecture Decisions

### 14.1 Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture Style | Layered Monolith (Phase 1) | Simpler, easier to develop, can split later |
| Backend Framework | FastAPI (Python) | Async support, LLM integration, fast development |
| Database | PostgreSQL | Production-ready, JSON support |
| Session Storage | Redis | Fast, scalable, persistent |
| LLM Provider | OpenAI/Anthropic | Best quality, can abstract for flexibility |
| Frontend | React | Rich ecosystem, good performance |
| Deployment | Docker Compose (Phase 1) | Simple, containerized, portable |

### 14.2 Trade-offs

1. **Monolith vs Microservices**
   - **Chosen**: Monolith (Phase 1)
   - **Trade-off**: Simpler now, may need to split later if scale requires

2. **SQLite vs PostgreSQL**
   - **Chosen**: PostgreSQL for production, SQLite for dev
   - **Trade-off**: More setup complexity, but production-ready

3. **In-Memory vs Redis Sessions**
   - **Chosen**: Redis
   - **Trade-off**: Additional infrastructure, but enables scaling

4. **Local LLM vs Cloud LLM**
   - **Chosen**: Cloud LLM (OpenAI/Anthropic)
   - **Trade-off**: Cost and dependency, but best quality

---

## Future Considerations

### 15.1 Phase 2 Enhancements

- **Voice Integration**: Add voice-to-text, text-to-speech
- **Multi-language Support**: Internationalization
- **Advanced Analytics**: Conversation analytics, conversion optimization
- **Microservices**: Split into services if needed
- **Message Queue**: Async processing with RabbitMQ/Kafka
- **Caching Layer**: More aggressive caching strategy

### 15.2 Scalability Path

1. **Phase 1**: Single instance, vertical scaling
2. **Phase 2**: Horizontal scaling with load balancer
3. **Phase 3**: Microservices architecture if needed
4. **Phase 4**: Multi-region deployment if global

---

## Appendix

### A.1 Glossary

- **LLM**: Large Language Model
- **NID**: National ID
- **PII**: Personally Identifiable Information
- **RBAC**: Role-Based Access Control
- **ORM**: Object-Relational Mapping

### A.2 References

- Requirements Document: `/requirements/requirements.md`
- User Stories: `/requirements/user-stories/`
- FastAPI Documentation: https://fastapi.tiangolo.com/
- OpenAI API Documentation: https://platform.openai.com/docs

### A.3 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Date] | Architecture Team | Initial version |

---

**Document Status**: Draft - Pending Review  
**Next Review**: [Date]  
**Approvers**: [Technical Lead, CTO]

