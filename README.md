# AI Life Insurance Sales Agent Application

An AI-powered conversational application that engages potential customers in life insurance sales conversations, provides policy information, and collects qualified lead information for sales team follow-up.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Development](#development)
- [Contributing](#contributing)

---

## 🎯 Overview

### What This Application Does

The AI Life Insurance Sales Agent is a text-based conversational AI system that:

- **Engages customers** in natural, persuasive conversations about life insurance
- **Educates customers** about available insurance policies (company and competitors)
- **Identifies interested prospects** using advanced intent detection
- **Collects qualified lead information** from interested customers
- **Stores leads** for sales team follow-up

### Key Features

- 🤖 **AI-Powered Conversations**: Uses LLM (Ollama/OpenAI) for natural language understanding
- 💬 **Persuasive Sales Techniques**: Implements human-like sales conversation strategies
- 🎤 **Voice Support (Phase 2)**: Real-time voice conversations with STT/TTS
- 🌍 **Multi-Language Support**: Internationalization ready
- 📊 **Lead Management**: Collects and manages customer information
- 🔒 **Secure Data Storage**: Encrypts sensitive information (NID, phone numbers)
- 📝 **Conversation Logging**: Tracks all conversations for analysis
- 📈 **Analytics Dashboard**: Conversation metrics and lead analytics
- 👥 **Admin Dashboard**: View leads, conversations, and manage policies

### Current Phase

**Phase 1: Text-Based Application** ✅  
- Text-based conversations
- Basic lead collection
- Admin interface for lead management

**Phase 2: Voice-Based Application** ✅  
- Voice-to-text conversion (STT)
- Text-to-speech synthesis (TTS)
- Real-time voice conversations (WebSocket)
- Multi-language support (i18n)
- Conversation analytics and metrics

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (recommended)
- **Git**

### Setup with Docker (Recommended)

```bash
# 1. Clone repository
git clone <repository-url>
cd lic-agent

# 2. Start all services (PostgreSQL, Redis, Ollama)
docker-compose up -d

# 3. Download Ollama model (first time only)
docker exec -it lic-agent-ollama ollama pull llama3.1

# 4. Setup Python environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 5. Configure environment
cp .env.docker.example .env
# Edit .env and add encryption keys (see docs/development-environment-setup.md)

# 6. Run database migrations
cd app
alembic upgrade head

# 7. Start application
cd app
uvicorn src.main:app --reload --port 8000
# Or from root directory:
# PYTHONPATH=app uvicorn app.src.main:app --reload --port 8000
```

**Application will be available at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

See [Development Environment Setup Guide](./docs/development-environment-setup.md) for detailed manual setup instructions.

---

## 📁 Project Structure

```
lic-agent/
├── README.md                      # This file
├── docker-compose.yml            # Docker Compose configuration
├── requirements.txt              # Python dependencies
├── .env.docker.example           # Environment template for Docker
│
├── requirements/                 # Requirements Documentation
│   ├── requirements.md           # Business Requirements Document
│   └── user-stories/             # User Stories & Acceptance Criteria
│       ├── README.md             # User Stories Index
│       └── us-*.md               # Individual user stories (22 stories)
│
├── architecture-and-design/      # Architecture & Design Documents
│   ├── system-architecture.md   # High-level system architecture
│   ├── technical-design.md       # Detailed technical design & implementation
│   └── llm-integration-design.md # LLM integration & prompt engineering
│
├── docs/                         # Development Documentation
│   ├── development-environment-setup.md  # Local environment setup
│   └── docker-setup.md          # Docker-specific setup guide
│
├── app/                          # Application code
│   ├── src/                      # Source code
│   │   ├── api/                  # API routes
│   │   ├── services/             # Business logic
│   │   ├── models/               # Data models
│   │   ├── repositories/         # Data access layer
│   │   ├── llm/                  # LLM integration
│   │   └── utils/                # Utilities
│   ├── tests/                    # Test files
│   ├── alembic/                  # Database migrations
│   ├── alembic.ini               # Alembic configuration
│   └── scripts/                  # Utility scripts
│
├── data/                         # Application data (created at runtime)
│   ├── leads/                    # Lead data files
│   └── conversations/            # Conversation logs
```

---

## 📚 Documentation

### Requirements & Specifications

| Document | Description | Location |
|----------|-------------|----------|
| **Business Requirements** | Complete functional and non-functional requirements | [`requirements/requirements.md`](./requirements/requirements.md) |
| **User Stories** | 22 detailed user stories with acceptance criteria | [`requirements/user-stories/`](./requirements/user-stories/) |
| **User Stories Index** | Overview and index of all user stories | [`requirements/user-stories/README.md`](./requirements/user-stories/README.md) |

### Architecture & Design

| Document | Description | Location |
|----------|-------------|----------|
| **System Architecture** | High-level architecture, components, technology stack | [`architecture-and-design/system-architecture.md`](./architecture-and-design/system-architecture.md) |
| **Technical Design** | Detailed implementation specifications, algorithms, APIs | [`architecture-and-design/technical-design.md`](./architecture-and-design/technical-design.md) |
| **LLM Integration Design** | Prompts, conversation templates, LLM configuration | [`architecture-and-design/llm-integration-design.md`](./architecture-and-design/llm-integration-design.md) |

### Development Guides

| Document | Description | Location |
|----------|-------------|----------|
| **Development Environment Setup** | Complete local setup instructions | [`docs/development-environment-setup.md`](./docs/development-environment-setup.md) |
| **Docker Setup Guide** | Docker Compose setup and management | [`docs/docker-setup.md`](./docs/docker-setup.md) |

---

## 🛠️ Development

### Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL 13+ (SQLite for minimal dev setup)
- **Cache/Sessions**: Redis 6+
- **LLM**: Ollama (local dev) / OpenAI GPT-4 (production)
- **Frontend**: React + TypeScript (to be implemented)

### Development Workflow

1. **Setup Environment**
   ```bash
   # Start Docker services
   docker-compose up -d
   
   # Setup Python environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run Application**
   ```bash
   cd app
   uvicorn src.main:app --reload --port 8000
   ```

3. **Run Tests**
   ```bash
   cd app
   pytest
   ```

4. **Database Migrations**
   ```bash
   cd app
   # Create migration
   alembic revision --autogenerate -m "Description"
   
   # Apply migrations
   alembic upgrade head
   ```

### Key Development Documents

- **Architecture**: Start with [`architecture-and-design/system-architecture.md`](./architecture-and-design/system-architecture.md)
- **Implementation**: Reference [`architecture-and-design/technical-design.md`](./architecture-and-design/technical-design.md)
- **LLM Integration**: See [`architecture-and-design/llm-integration-design.md`](./architecture-and-design/llm-integration-design.md)

---

## 📖 Documentation Guide

### For New Developers

**Start Here:**
1. Read [Business Requirements](./requirements/requirements.md) to understand the project
2. Review [System Architecture](./architecture-and-design/system-architecture.md) for high-level design
3. Follow [Development Environment Setup](./docs/development-environment-setup.md) to set up locally
4. Browse [User Stories](./requirements/user-stories/README.md) to understand features

**Then:**
5. Study [Technical Design](./architecture-and-design/technical-design.md) for implementation details
6. Review [LLM Integration Design](./architecture-and-design/llm-integration-design.md) for AI-specific details

### For Product Owners / Stakeholders

- **Requirements**: [`requirements/requirements.md`](./requirements/requirements.md)
- **User Stories**: [`requirements/user-stories/`](./requirements/user-stories/)
- **System Overview**: [`architecture-and-design/system-architecture.md`](./architecture-and-design/system-architecture.md) (Sections 1-4)

### For Developers

- **Setup**: [`docs/development-environment-setup.md`](./docs/development-environment-setup.md)
- **Architecture**: [`architecture-and-design/system-architecture.md`](./architecture-and-design/system-architecture.md)
- **Implementation**: [`architecture-and-design/technical-design.md`](./architecture-and-design/technical-design.md)
- **LLM Details**: [`architecture-and-design/llm-integration-design.md`](./architecture-and-design/llm-integration-design.md)

### For QA / Testers

- **User Stories**: [`requirements/user-stories/`](./requirements/user-stories/) - Each story has acceptance criteria
- **Requirements**: [`requirements/requirements.md`](./requirements/requirements.md) - For test scenarios

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.docker.example`:

```bash
# LLM Configuration (Ollama for local dev)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Database
DATABASE_URL=postgresql+asyncpg://lic_agent:lic_agent_password@localhost:5432/lic_agent_dev

# Redis
REDIS_URL=redis://localhost:6379

# Security (Generate keys - see setup guide)
ENCRYPTION_KEY=your-key-here
JWT_SECRET_KEY=your-key-here

# Voice Configuration (Phase 2)
VOICE_ENABLED=true
STT_PROVIDER=openai
TTS_PROVIDER=openai
TTS_VOICE=alloy
DEFAULT_LANGUAGE=en
OPENAI_API_KEY=your-openai-key-here  # Required for voice features
```

See [`docs/development-environment-setup.md`](./docs/development-environment-setup.md) for complete configuration.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_conversation_service.py -v
```

---

## 📦 Docker Services

### Start Services

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **Ollama** on port 11434

### Manage Services

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Clean reset
docker-compose down -v
```

See [`docs/docker-setup.md`](./docs/docker-setup.md) for detailed Docker commands.

---

## 🔐 Security

- Sensitive data (NID, phone numbers) are encrypted at rest
- JWT authentication for admin endpoints
- HTTPS/TLS for production (configure in deployment)
- Data privacy compliance (GDPR-ready structure)

---

## 🚦 Current Status

### ✅ Completed

- [x] Business Requirements Document
- [x] User Stories (22 stories)
- [x] System Architecture Document
- [x] Technical Design Document
- [x] LLM Integration Design Document
- [x] Development Environment Setup Guide
- [x] Docker Compose Configuration

### 🚧 In Progress

- [ ] Implementation (starting soon)

### 📋 Planned

- [ ] Database Design Document
- [ ] API Specification Document (OpenAPI/Swagger)
- [ ] Test Strategy Document
- [ ] Deployment Plan

---

## 🤝 Contributing

### Development Workflow

1. Create a feature branch from `main`
2. Implement feature based on user stories
3. Write tests for your changes
4. Ensure all tests pass
5. Submit pull request

### Code Standards

- Follow Python PEP 8 style guide
- Write docstrings for all functions and classes
- Include type hints
- Write tests for new functionality

---

## 📞 Support

For questions or issues:

1. Check the documentation in this README
2. Review the specific document for your question
3. Check troubleshooting sections in setup guides
4. Contact the development team

---

## 📄 License

[Add your license information here]

---

## 🔗 Quick Links

### Setup
- [Development Environment Setup](./docs/development-environment-setup.md)
- [Docker Setup Guide](./docs/docker-setup.md)

### Documentation
- [Business Requirements](./requirements/requirements.md)
- [User Stories](./requirements/user-stories/README.md)
- [System Architecture](./architecture-and-design/system-architecture.md)
- [Technical Design](./architecture-and-design/technical-design.md)
- [LLM Integration Design](./architecture-and-design/llm-integration-design.md)

### Configuration
- `docker-compose.yml` - Docker services configuration
- `.env.docker.example` - Environment variables template

---

**Last Updated**: [Date]  
**Version**: 1.0.0  
**Status**: Pre-Implementation

