# Docker Setup Guide
## Quick Start with Docker Compose

This guide provides instructions for using Docker Compose to set up the development environment quickly.

---

## Why Docker Compose?

✅ **One Command Setup**: Start PostgreSQL, Redis, and Ollama with one command  
✅ **No Local Installation**: No need to install PostgreSQL, Redis, or Ollama  
✅ **Consistent Environment**: Same setup across all developers  
✅ **Easy Cleanup**: Remove everything with `docker-compose down -v`  
✅ **Isolated**: Doesn't affect your local system  

---

## Prerequisites

- **Docker Desktop** installed and running
  - macOS/Windows: https://www.docker.com/products/docker-desktop/
  - Linux: Install Docker and Docker Compose separately

Verify installation:
```bash
docker --version
docker-compose --version
```

---

## Quick Start

### 1. Start All Services

```bash
# Start PostgreSQL, Redis, and Ollama
docker-compose up -d

# Check services are running
docker-compose ps
```

Expected output:
```
NAME                   STATUS
lic-agent-postgres     Up (healthy)
lic-agent-redis        Up (healthy)
lic-agent-ollama       Up (healthy)
```

### 2. Download Ollama Model (First Time)

```bash
# Pull the recommended model
docker exec -it lic-agent-ollama ollama pull llama3.1

# Verify model is available
docker exec -it lic-agent-ollama ollama list
```

This will download ~4.7GB, so may take a few minutes depending on your internet speed.

### 3. Configure Environment

```bash
# Copy Docker environment template
cp .env.docker.example .env

# Edit .env and add your encryption keys (see development-environment-setup.md)
```

### 4. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
# Ensure services are running
docker-compose ps

# Run migrations
alembic upgrade head
```

### 6. Start Application

```bash
# Run the FastAPI application
uvicorn apps.api.main:app --reload --port 8000
```

Application will be available at: http://localhost:8000

---

## Service Details

### PostgreSQL
- **Host**: `localhost` (from your machine) or `postgres` (from other containers)
- **Port**: `5432`
- **User**: `lic_agent`
- **Password**: `lic_agent_password`
- **Database**: `lic_agent_dev`

**Connection String:**
```
postgresql+asyncpg://lic_agent:lic_agent_password@localhost:5432/lic_agent_dev
```

### Redis
- **Host**: `localhost` (from your machine) or `redis` (from other containers)
- **Port**: `6379`
- **Password**: None

**Connection String:**
```
redis://localhost:6379
```

### Ollama
- **Host**: `localhost` (from your machine) or `ollama` (from other containers)
- **Port**: `11434`
- **API URL**: `http://localhost:11434`

---

## Useful Docker Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f ollama

# Restart a service
docker-compose restart redis

# Check service status
docker-compose ps
```

### Database Access

```bash
# Access PostgreSQL CLI
docker exec -it lic-agent-postgres psql -U lic_agent -d lic_agent_dev

# Run SQL commands
docker exec -it lic-agent-postgres psql -U lic_agent -d lic_agent_dev -c "SELECT version();"

# Backup database
docker exec lic-agent-postgres pg_dump -U lic_agent lic_agent_dev > backup.sql
```

### Redis Access

```bash
# Access Redis CLI
docker exec -it lic-agent-redis redis-cli

# Test Redis
docker exec -it lic-agent-redis redis-cli ping
# Should return: PONG

# View all keys
docker exec -it lic-agent-redis redis-cli KEYS "*"
```

### Ollama Access

```bash
# List available models
docker exec -it lic-agent-ollama ollama list

# Pull a model
docker exec -it lic-agent-ollama ollama pull llama3.1

# Run a test query
docker exec -it lic-agent-ollama ollama run llama3.1 "Hello, introduce yourself"

# Test via API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Hello",
  "stream": false
}'
```

### System Information

```bash
# View resource usage
docker stats

# View disk usage
docker system df

# View all containers
docker ps -a

# Clean up unused resources
docker system prune
```

---

## Common Issues

### Issue: Services Not Starting

```bash
# Check logs for errors
docker-compose logs

# Check if ports are available
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :11434 # Ollama

# Restart Docker Desktop (macOS/Windows)
# Or restart Docker service (Linux): sudo systemctl restart docker
```

### Issue: Ollama Model Download Fails

```bash
# Check disk space
docker system df

# Try pulling again
docker exec -it lic-agent-ollama ollama pull llama3.1

# If still fails, check internet connection
docker exec -it lic-agent-ollama ping -c 3 8.8.8.8
```

### Issue: Database Connection Fails

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker exec -it lic-agent-postgres psql -U lic_agent -d lic_agent_dev -c "SELECT 1;"
```

### Issue: High Memory Usage

Ollama models can use significant RAM. If you have limited RAM:

```bash
# Use smaller model
docker exec -it lic-agent-ollama ollama pull mistral  # ~4GB instead of ~5GB

# Update .env
OLLAMA_MODEL=mistral

# Or stop Ollama when not needed
docker-compose stop ollama
docker-compose start ollama  # When needed again
```

---

## Docker Compose File Structure

The `docker-compose.yml` includes:

1. **postgres** - PostgreSQL 13 database
2. **redis** - Redis for session storage
3. **ollama** - Local LLM server

All services are connected via a Docker network and include health checks.

---

## Environment Variables for Docker

When using Docker Compose, your `.env` should include:

```bash
# Database (connect to Docker PostgreSQL)
DATABASE_URL=postgresql+asyncpg://lic_agent:lic_agent_password@localhost:5432/lic_agent_dev

# Redis (connect to Docker Redis)
REDIS_URL=redis://localhost:6379

# Ollama (connect to Docker Ollama)
OLLAMA_BASE_URL=http://localhost:11434
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
```

---

## Production Considerations

⚠️ **Note**: The Docker Compose setup is for **development only**.

For production:
- Use managed databases (AWS RDS, Azure Database, etc.)
- Use managed Redis (AWS ElastiCache, Azure Cache, etc.)
- Use cloud LLM providers (OpenAI, Anthropic) or self-hosted Ollama with proper infrastructure
- Implement proper secrets management
- Use environment-specific configurations

---

## Next Steps

After Docker services are running:

1. ✅ Verify all services are healthy: `docker-compose ps`
2. ✅ Test database connection
3. ✅ Test Redis connection
4. ✅ Test Ollama with a query
5. ✅ Run database migrations
6. ✅ Start the application
7. ✅ Test the API endpoints

See [Development Environment Setup Guide](./development-environment-setup.md) for complete setup instructions.

