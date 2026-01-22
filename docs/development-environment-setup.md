# Development Environment Setup Guide
## AI Life Insurance Sales Agent Application

**Version**: 1.0  
**Last Updated**: [Date]  
**Target Audience**: Developers setting up local development environment

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Guide](#quick-start-guide)
3. [Detailed Setup Instructions](#detailed-setup-instructions)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Redis Setup](#redis-setup)
7. [Running the Application](#running-the-application)
8. [Verifying Setup](#verifying-setup)
9. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
10. [IDE Setup](#ide-setup)

---

## Prerequisites

### Required Software

Before starting, ensure you have the following installed:

1. **Python 3.11 or higher**
   - Check version: `python3 --version`
   - Download: https://www.python.org/downloads/

2. **PostgreSQL 13+** (or SQLite for minimal setup)
   - PostgreSQL: https://www.postgresql.org/download/
   - Or use SQLite (included with Python)

3. **Redis 6+**
   - macOS: `brew install redis`
   - Linux: `sudo apt-get install redis-server` (Ubuntu/Debian)
   - Windows: https://redis.io/docs/getting-started/installation/install-redis-on-windows/
   - Docker alternative: `docker run -d -p 6379:6379 redis:latest`

4. **Ollama** (Recommended for Local Development)
   - macOS/Linux: `curl -fsSL https://ollama.com/install.sh | sh`
   - Windows: Download from https://ollama.com/download
   - Alternative: Docker: `docker run -d -p 11434:11434 ollama/ollama`

5. **Git**
   - Check version: `git --version`
   - Download: https://git-scm.com/downloads

6. **Docker & Docker Compose** (Recommended for Easy Setup)
   - Docker Desktop: https://www.docker.com/products/docker-desktop/
   - **Note**: Using Docker Compose eliminates need to install PostgreSQL, Redis, and Ollama locally

7. **LLM API Key** (Optional - only if using cloud providers)
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com/
   - **Note**: For local development, Ollama doesn't require API keys

8. **LangGraph Tooling (Optional - Preview)**
   - Install with: `pip install langgraph langchain`
   - Used by the new agent orchestration layer found under `apps/`, `graph/`, and `chains/`

### Recommended Tools

- **IDE/Editor**: VS Code, PyCharm, or your preferred Python IDE
- **Database Client**: pgAdmin, DBeaver, or psql command line
- **Redis Client**: RedisInsight or redis-cli
- **API Testing**: Postman or curl

---

## Quick Start Guide

### Option A: Docker Compose (Recommended for Easy Setup)

```bash
# 1. Clone repository
git clone <repository-url>
cd lic-agent

# 2. Start all services (PostgreSQL, Redis, Ollama)
docker-compose up -d

# 3. Download Ollama model (first time only)
docker exec -it lic-agent-ollama ollama pull llama3.1

# 4. Create virtual environment for Python app
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Copy and configure environment
cp .env.docker.example .env
# Edit .env - Docker services are already configured!

# 7. Run database migrations
alembic upgrade head

# 8. Run application
uvicorn apps.api.main:app --reload --port 8000
```

**Benefits:**
- ✅ No need to install PostgreSQL, Redis, or Ollama locally
- ✅ All services start with one command
- ✅ Consistent environment
- ✅ Easy cleanup: `docker-compose down`

### Option B: Manual Setup (For Experienced Developers)

```bash
# 1. Clone repository
git clone <repository-url>
cd lic-agent

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp .env.example .env

# 5. Edit .env with your settings (especially API keys)

# 6. Setup database (SQLite for quick start)
# Or run PostgreSQL setup (see Database Setup section)

# 7. Run migrations (if using PostgreSQL)
alembic upgrade head

# 8. Start Redis (or use Docker)
redis-server  # Or: docker run -d -p 6379:6379 redis

# 9. Start Ollama
ollama serve  # Or use Docker: docker run -d -p 11434:11434 ollama/ollama
ollama pull llama3.1

# 10. Run application
uvicorn apps.api.main:app --reload --port 8000
```

---

## Detailed Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd lic-agent
```

### Step 2: Python Virtual Environment Setup

#### macOS/Linux

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
which python
# Should show: .../lic-agent/venv/bin/python
```

#### Windows

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation
where python
# Should show: ...\lic-agent\venv\Scripts\python.exe
```

### Step 3: Install Python Dependencies

```bash
# Ensure you're in the virtual environment
# Upgrade pip first
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# If requirements.txt doesn't exist yet, install manually:
pip install fastapi uvicorn[standard] sqlalchemy asyncpg aiosqlite
pip install redis pydantic python-dotenv
pip install ollama  # For local LLM (Ollama)
# pip install openai anthropic  # Only if using cloud providers
pip install alembic  # For database migrations
pip install cryptography  # For encryption
pip install pytest pytest-asyncio  # For testing
```

### Step 4: Environment Configuration

#### 4.1 Create .env File

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Or create manually:
touch .env
```

#### 4.2 Configure .env File

Edit `.env` with your local settings:

```bash
# Application
APP_NAME=AI Life Insurance Sales Agent
ENVIRONMENT=development
DEBUG=true

# Database (SQLite for development - simplest)
DATABASE_URL=sqlite+aiosqlite:///./data/lic_agent.db
# OR PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/lic_agent_dev

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=
SESSION_TTL=3600

# LLM Configuration (Local Development with Ollama)
LLM_PROVIDER=ollama  # Options: ollama, openai, anthropic
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3  # or llama3.1, mistral, mixtral, etc.

# For Cloud Providers (optional - only if not using Ollama)
# OPENAI_API_KEY=sk-your-api-key-here
# OPENAI_MODEL=gpt-4
# ANTHROPIC_API_KEY=your-api-key-here
# ANTHROPIC_MODEL=claude-3-opus-20240229

# Embedding Configuration (FREE for development, Voyage AI for production)
EMBEDDING_PROVIDER=sentence_transformers  # Options: sentence_transformers (free), voyage (production), openai (production)
EMBEDDING_MODEL=all-MiniLM-L6-v2  # For sentence_transformers (free)
# For production with Voyage AI (recommended):
# EMBEDDING_PROVIDER=voyage
# EMBEDDING_MODEL=voyage-3.5-lite
# VOYAGE_API_KEY=your-voyage-api-key-here
# For production with OpenAI (alternative):
# EMBEDDING_PROVIDER=openai
# EMBEDDING_MODEL=text-embedding-3-small
# OPENAI_API_KEY=sk-your-api-key-here  # Already listed above

LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=500
LLM_TIMEOUT=30

# Security (Generate these - see below)
ENCRYPTION_KEY=your-encryption-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# File Storage
FILE_STORAGE_PATH=./data
ENABLE_FILE_STORAGE=true

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json
```

#### 4.3 Generate Security Keys

```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate JWT secret key (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the generated keys to your `.env` file.

### Step 5: Docker Compose Setup (Recommended)

#### 5.1 Using Docker Compose for All Services

**Benefits:**
- Single command to start PostgreSQL, Redis, and Ollama
- No local installation needed
- Isolated from your system
- Easy to reset and clean up
- Consistent across team

**Setup:**

```bash
# Start all services
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

**Services Provided:**
- **PostgreSQL**: `localhost:5432`
  - User: `lic_agent`
  - Password: `lic_agent_password`
  - Database: `lic_agent_dev`
- **Redis**: `localhost:6379`
- **Ollama**: `localhost:11434`

**Configure .env for Docker:**
```bash
# .env configuration for Docker Compose
DATABASE_URL=postgresql+asyncpg://lic_agent:lic_agent_password@localhost:5432/lic_agent_dev
REDIS_URL=redis://localhost:6379
OLLAMA_BASE_URL=http://localhost:11434
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
```

**First Time Setup:**
```bash
# 1. Start services
docker-compose up -d

# 2. Wait for services to be healthy (30 seconds)
docker-compose ps

# 3. Download Ollama model
docker exec -it lic-agent-ollama ollama pull llama3.1

# 4. Verify Ollama model
docker exec -it lic-agent-ollama ollama list

# 5. Run database migrations
alembic upgrade head
```

**Useful Commands:**
```bash
# View PostgreSQL logs
docker-compose logs postgres

# Access PostgreSQL CLI
docker exec -it lic-agent-postgres psql -U lic_agent -d lic_agent_dev

# Access Redis CLI
docker exec -it lic-agent-redis redis-cli

# Access Ollama CLI
docker exec -it lic-agent-ollama ollama list
docker exec -it lic-agent-ollama ollama run llama3.1 "Hello"

# Restart a specific service
docker-compose restart redis

# View resource usage
docker stats
```

#### 5.2 Database Migrations with Docker

```bash
# Run migrations (from your local machine, connecting to Docker PostgreSQL)
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Migration description"

# Check migration status
alembic current
```

---

### Step 6: Database Setup (Manual Alternative)

#### Option A: SQLite (Simplest for Development)

SQLite requires no additional setup - it's included with Python. Just ensure the data directory exists:

```bash
mkdir -p data
```

The application will automatically create the database file at `./data/lic_agent.db`.

#### Option B: PostgreSQL (Recommended for Production-like Environment)

**5.1 Install PostgreSQL**

**macOS:**
```bash
brew install postgresql@13
brew services start postgresql@13
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from: https://www.postgresql.org/download/windows/

**5.2 Create Database**

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql prompt:
CREATE DATABASE lic_agent_dev;
CREATE USER lic_agent_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE lic_agent_dev TO lic_agent_user;
\q
```

**5.3 Update .env**

```bash
DATABASE_URL=postgresql+asyncpg://lic_agent_user:your_password@localhost:5432/lic_agent_dev
```

**5.4 Run Database Migrations**

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

#### Option C: Docker PostgreSQL (Easiest)

```bash
# Run PostgreSQL in Docker
docker run -d \
  --name lic-agent-postgres \
  -e POSTGRES_USER=lic_agent \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=lic_agent_dev \
  -p 5432:5432 \
  postgres:13

# Then update .env:
DATABASE_URL=postgresql+asyncpg://lic_agent:password@localhost:5432/lic_agent_dev
```

### Step 7: Ollama Setup (Manual Alternative)

**Note**: If using Docker Compose, skip this section - Ollama is already running in Docker.

#### 7.1 Install Ollama Locally (if not using Docker)

**macOS:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download installer from: https://ollama.com/download

**Docker (Alternative):**
```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama
```

#### 6.2 Verify Ollama Installation

```bash
# Check if Ollama is running
ollama --version

# Test Ollama service
curl http://localhost:11434/api/tags
# Should return list of available models
```

#### 6.3 Download Recommended Models

For local development, download one of these models:

```bash
# Llama 3.1 (8B) - Good balance of quality and speed, ~4.7GB
ollama pull llama3.1

# Llama 3 (8B) - Alternative, ~4.7GB
ollama pull llama3

# Mistral (7B) - Fast and efficient, ~4.1GB
ollama pull mistral

# Mixtral (8x7B) - Higher quality, ~26GB (requires more RAM)
ollama pull mixtral
```

**Recommendation for Development:**
- **Start with**: `llama3.1` (best balance)
- **Faster**: `mistral` (if you need speed)
- **Better Quality**: `mixtral` (if you have 16GB+ RAM)

#### 6.4 Test Model

```bash
# Test the model
ollama run llama3.1 "Hello, can you introduce yourself as an AI insurance agent?"

# Should respond appropriately
```

#### 6.5 Configure Application

Update your `.env` file:
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1  # or whichever model you downloaded
```

#### 6.6 Start Ollama Service

Ollama runs as a background service. Ensure it's running:

```bash
# Check if running
curl http://localhost:11434/api/tags

# If not running, start it:
# macOS/Linux: Service starts automatically after install
# Or manually: ollama serve

# Windows: Ollama runs as a service automatically
```

#### 6.7 Verify Integration

```bash
# Test from Python
python -c "
from ollama import Client
client = Client(host='http://localhost:11434')
response = client.generate(model='llama3.1', prompt='Hello')
print(response['response'])
"
```

---

### Step 8: Redis Setup (Manual Alternative)

**Note**: If using Docker Compose, skip this section - Redis is already running in Docker.

#### Option A: Install Redis Locally

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis-server
```

**Windows:**
Download from: https://github.com/microsoftarchive/redis/releases
Or use Docker (see Option B)

**Verify Redis is running:**
```bash
redis-cli ping
# Should respond: PONG
```

#### Option B: Docker Redis (Easiest)

```bash
docker run -d \
  --name lic-agent-redis \
  -p 6379:6379 \
  redis:latest

# Verify
docker exec -it lic-agent-redis redis-cli ping
```

#### Option C: In-Memory (Development Only)

For minimal setup during development, you can use in-memory session storage (not recommended for production). Update code to use in-memory storage instead of Redis.

### Step 9: Initialize Application Data

#### 9.1 Create Required Directories

```bash
mkdir -p data/leads
mkdir -p data/conversations
mkdir -p logs
```

#### 7.2 Seed Initial Data (Optional)

Create a script to seed test policies:

```bash
# Create seed script: scripts/seed_policies.py
python scripts/seed_policies.py
```

Or manually insert via database client.

---

## Running the Application

### Development Server

```bash
# Activate virtual environment first
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run with auto-reload (recommended for development)
make run
# Or manually
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

# Or use FastAPI CLI
fastapi dev src/main.py
```

The application will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Running with Docker Compose (If Available)

```bash
docker-compose up -d
```

### Running Tests

```bash
# Run all checks via Makefile
make format lint type-check test

# Windows helper (PowerShell)
pwsh ./scripts/run_checks.ps1

# Run individual steps
make lint
make type-check
make test
pytest --cov=src --cov-report=html
# Run specific test file
pytest tests/test_health.py

# Run with verbose output
pytest -v
```

### LangGraph Preview Commands

The LangGraph-based agent scaffolding lives under `apps/`, `graph/`, and related packages.
While the graph is still under construction, you can run placeholder checks:

```bash
pytest tests/test_graph.py
python scripts/bootstrap.sh  # placeholder scaffold
```

Install optional dependencies if you plan to experiment early:

```bash
pip install langgraph langchain
```

---

## Verifying Setup

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### 2. Test API Endpoints

```bash
# Start a conversation
curl -X POST http://localhost:8000/api/conversation/start \
  -H "Content-Type: application/json"

# Should return session_id and conversation_id
```

### 3. Check Database Connection

```bash
# For PostgreSQL
psql -U lic_agent_user -d lic_agent_dev -c "SELECT version();"

# For SQLite
sqlite3 data/lic_agent.db ".tables"
```

### 4. Check Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### 5. Verify LLM Connection

**For Ollama (Local Development):**
```bash
# Test Ollama is running and model is available
curl http://localhost:11434/api/tags
ollama list

# Test model directly
ollama run llama3.1 "Hello, introduce yourself as an insurance agent"
```

**For Cloud Providers:**
Check application logs for successful LLM API calls when sending a message.

---

## Common Issues and Troubleshooting

### Issue: Python version incompatible

**Error**: `Python 3.11+ is required`

**Solution**:
```bash
# Check Python version
python3 --version

# Install Python 3.11+ if needed
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
```

### Issue: Module not found errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Database connection failed

**Error**: `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions**:
1. **PostgreSQL not running:**
   ```bash
   # Check if PostgreSQL is running
   # macOS: brew services list
   # Linux: sudo systemctl status postgresql
   # Start it if needed
   ```

2. **Wrong connection string:**
   - Verify DATABASE_URL in .env matches your setup
   - Check username, password, host, port, database name

3. **Firewall blocking:**
   - Ensure PostgreSQL is accessible on port 5432

### Issue: Redis connection failed

**Error**: `redis.exceptions.ConnectionError`

**Solutions**:
1. **Redis not running:**
   ```bash
   # Check if Redis is running
   redis-cli ping
   # If fails, start Redis:
   redis-server  # or brew services start redis
   ```

2. **Wrong Redis URL:**
   - Verify REDIS_URL in .env
   - Default: `redis://localhost:6379`

3. **Use Docker if local install fails:**
   ```bash
   docker run -d -p 6379:6379 redis
   ```

### Issue: Ollama Connection Errors

**Error**: `Connection refused` or `Cannot connect to Ollama`

**Solutions**:
1. **Ollama not running:**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # If fails, start Ollama:
   # macOS/Linux: ollama serve (in separate terminal)
   # Or restart service: brew services restart ollama
   ```

2. **Wrong port or URL:**
   - Verify OLLAMA_BASE_URL in .env: `http://localhost:11434`
   - Check if port 11434 is available: `lsof -i :11434`

3. **Model not downloaded:**
   ```bash
   # List available models
   ollama list
   
   # Download model if missing
   ollama pull llama3.1
   ```

4. **Insufficient resources:**
   - Check available RAM (models need 4-8GB minimum)
   - Try smaller model (mistral instead of mixtral)
   - Close other applications

### Issue: Ollama Slow Responses

**Error**: Very slow responses (30+ seconds)

**Solutions**:
1. **Use smaller model:**
   ```bash
   ollama pull mistral  # Smaller, faster
   # Update OLLAMA_MODEL in .env
   ```

2. **Check system resources:**
   - Ensure sufficient RAM (8GB+ recommended)
   - Close other applications

3. **Use GPU if available:**
   - Ollama automatically uses GPU if available
   - Check: `ollama ps` should show GPU usage

4. **Reduce context window:**
   - Limit conversation history in code
   - Reduce max_tokens in LLM config

### Issue: LLM API errors (Cloud Providers)

**Error**: `openai.error.AuthenticationError` or `401 Unauthorized`

**Solutions**:
1. **Invalid API key:**
   - Verify API key in .env file
   - Check key has proper format (starts with `sk-` for OpenAI)
   - Ensure no extra spaces or quotes

2. **API quota exceeded:**
   - Check your OpenAI/Anthropic account quota
   - Verify billing is set up

3. **Wrong provider configured:**
   - Verify LLM_PROVIDER matches your API key
   - Check model name is correct

### Issue: Docker Compose Problems

**Error**: `Cannot connect to Docker daemon` or `docker-compose: command not found`

**Solutions**:
1. **Docker not running:**
   ```bash
   # macOS/Windows: Start Docker Desktop application
   # Linux: sudo systemctl start docker
   # Verify: docker ps
   ```

2. **Docker Compose not installed:**
   ```bash
   # Most Docker Desktop includes docker-compose
   # Verify: docker-compose --version
   # Install if missing: pip install docker-compose
   ```

3. **Port conflicts:**
   ```bash
   # If ports 5432, 6379, or 11434 are in use
   # Check what's using them:
   lsof -i :5432
   lsof -i :6379
   lsof -i :11434
   
   # Stop conflicting services or modify docker-compose.yml ports
   ```

4. **Services not starting:**
   ```bash
   # Check logs
   docker-compose logs
   
   # Restart services
   docker-compose restart
   
   # Rebuild if needed
   docker-compose up -d --build
   ```

5. **Ollama model not downloading in Docker:**
   ```bash
   # Access Ollama container
   docker exec -it lic-agent-ollama ollama pull llama3.1
   
   # Check disk space (models need 4-8GB)
   docker system df
   ```

### Issue: Port already in use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
uvicorn apps.api.main:app --reload --port 8001
```

### Issue: Migration errors

**Error**: `alembic.util.exc.CommandError: Target database is not up to date`

**Solutions**:
```bash
# Show current revision
alembic current

# Upgrade to head
alembic upgrade head

# If conflicts, resolve manually or reset:
# WARNING: This will delete all data
alembic downgrade base
alembic upgrade head
```

### Issue: Import errors in code

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Ensure you're running from project root
pwd  # Should show .../lic-agent

# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # macOS/Linux
set PYTHONPATH=%PYTHONPATH%;%CD%  # Windows

# Or install in development mode
pip install -e .
```

---

## IDE Setup

### VS Code

#### Recommended Extensions

1. **Python** (Microsoft)
2. **Pylance** (Microsoft)
3. **Python Docstring Generator**
4. **SQLTools** (for database queries)
5. **REST Client** (for API testing)

#### VS Code Settings (.vscode/settings.json)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    ".pytest_cache": true
  }
}
```

#### Launch Configuration (.vscode/launch.json)

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "apps.api.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### PyCharm

1. **Open Project**: File → Open → Select project directory
2. **Configure Python Interpreter**:
   - File → Settings → Project → Python Interpreter
   - Select existing interpreter: `venv/bin/python`
   - Or create new: Click gear → Add → Existing environment → Select `venv/bin/python`

3. **Configure Run Configuration**:
   - Run → Edit Configurations
   - Add New → Python
   - Script path: Select `src/main.py` or use module: `uvicorn`
   - Parameters: `apps.api.main:app --reload`
   - Working directory: Project root
   - Environment variables: Load from `.env` file

---

## Project Structure

After setup, your project should look like:

```
lic-agent/
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Template for .env
├── .gitignore
├── README.md
├── requirements.txt
├── alembic.ini              # Database migrations config
├── pyproject.toml           # Project metadata (optional)
├── venv/                    # Virtual environment (gitignored)
├── data/                    # Application data (gitignored)
│   ├── lic_agent.db        # SQLite database (if using SQLite)
│   ├── leads/
│   └── conversations/
├── src/                     # Source code
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry
│   ├── api/
│   ├── services/
│   ├── models/
│   ├── repositories/
│   ├── llm/
│   └── utils/
├── tests/                   # Test files
├── alembic/                 # Database migrations
│   └── versions/
├── docs/                    # Documentation
└── scripts/                 # Utility scripts
```

---

## Next Steps

After completing setup:

1. **Verify Installation**: Run health check endpoint
2. **Review Documentation**: Read Technical Design Document
3. **Run Tests**: Ensure test suite passes
4. **Start Development**: Pick a user story to implement
5. **Set Up Git**: Configure git hooks, branching strategy

---

## Additional Resources

### Documentation
- Technical Design Document: `/architecture-and-design/technical-design.md`
- System Architecture: `/architecture-and-design/system-architecture.md`
- User Stories: `/requirements/user-stories/`

### External Resources
- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- OpenAI API Documentation: https://platform.openai.com/docs
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Redis Documentation: https://redis.io/docs/

---

## Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Review application logs: `logs/app.log`
3. Check GitHub issues (if repository exists)
4. Ask team members or technical lead
5. Review error messages carefully - they often contain helpful information

---

**Setup Complete!** 🎉

You should now be able to:
- ✅ Run the application locally
- ✅ Connect to database
- ✅ Use Redis for sessions
- ✅ Make API calls to LLM providers
- ✅ Run tests
- ✅ Develop new features

Happy coding!

