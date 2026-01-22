# Embedding Provider Configuration Guide

## Overview

The system supports multiple embedding providers with easy switching via configuration. This allows you to:
- Use **FREE** local models for development
- Use **Voyage AI voyage-3.5-lite** for production (recommended)
- Switch to **OpenAI** if needed
- Change providers without code changes

---

## Supported Providers

### 1. Sentence Transformers (FREE - Development)

**Best for**: Local development, testing, zero-cost scenarios

**Pros:**
- ✅ 100% FREE - No API costs
- ✅ Runs locally - Complete data privacy
- ✅ Works offline
- ✅ Fast inference on CPU
- ✅ No API keys needed

**Cons:**
- Requires local compute resources
- Lower quality than cloud APIs (but good for development)

**Model**: `all-MiniLM-L6-v2` (default, recommended)

### 2. Voyage AI (Recommended - Production)

**Best for**: Production environments requiring high-quality embeddings

**Pros:**
- ✅ **Best quality/cost ratio** - Outperforms OpenAI v3-large by 6.34%
- ✅ **Lower cost** - 6.5x cheaper than OpenAI
- ✅ Optimized for retrieval/RAG tasks
- ✅ Supports input_type ("document" vs "query") for better retrieval
- ✅ Multiple dimension options (256, 512, 1024, 2048)

**Cons:**
- Requires API key
- Requires internet connection
- Paid service (but cost-effective)

**Model**: `voyage-3.5-lite` (recommended for production)

### 3. OpenAI (Alternative - Production)

**Best for**: Production when Voyage AI not available

**Pros:**
- ✅ Excellent quality
- ✅ Widely available
- ✅ Good documentation

**Cons:**
- Higher cost than Voyage AI
- No input_type optimization

**Models**: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`

---

## Configuration

### Environment Variables

Configure embedding provider via environment variables:

```bash
# Provider selection
EMBEDDING_PROVIDER=sentence_transformers  # or "voyage" or "openai"

# Model selection (provider-specific)
EMBEDDING_MODEL=all-MiniLM-L6-v2  # For sentence_transformers
# EMBEDDING_MODEL=voyage-3.5-lite  # For voyage
# EMBEDDING_MODEL=text-embedding-3-small  # For openai

# API Keys (only needed for cloud providers)
# VOYAGE_API_KEY=your-voyage-api-key  # For Voyage AI
# OPENAI_API_KEY=sk-your-api-key  # For OpenAI
```

### Configuration Examples

#### Development (FREE)
```bash
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2
# No API key needed!
```

#### Production (Voyage AI - Recommended)
```bash
EMBEDDING_PROVIDER=voyage
EMBEDDING_MODEL=voyage-3.5-lite
VOYAGE_API_KEY=your-voyage-api-key-here
```

#### Production (OpenAI - Alternative)
```bash
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=sk-your-api-key-here
```

---

## Code Implementation

### EmbeddingService Usage

```python
from rag.services.embedding_service import EmbeddingService
import os

# Initialize based on environment configuration
provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

service = EmbeddingService(
    provider=provider,
    model=model,
    api_key=os.getenv("VOYAGE_API_KEY") or os.getenv("OPENAI_API_KEY")
)

# Use the same interface regardless of provider
embedding = service.embed("policy document text")
embeddings = service.embed_batch(["doc1", "doc2", "doc3"])
```

### Voyage AI Specific Features

Voyage AI supports `input_type` parameter for better retrieval:

```python
# For document embeddings (when ingesting policies)
document_embeddings = service.embed_batch(
    policy_documents,
    input_type="document"  # Voyage AI specific
)

# For query embeddings (when searching)
query_embedding = service.embed(
    user_query,
    input_type="query"  # Voyage AI specific
)
```

**Note**: `input_type` is optional and only used by Voyage AI. Other providers ignore it.

---

## Provider Switching

### Switching Between Providers

**No code changes needed!** Just update environment variables:

```bash
# Switch from development to production (Voyage AI)
export EMBEDDING_PROVIDER=voyage
export EMBEDDING_MODEL=voyage-3.5-lite
export VOYAGE_API_KEY=your-key

# Or switch to OpenAI
export EMBEDDING_PROVIDER=openai
export EMBEDDING_MODEL=text-embedding-3-small
export OPENAI_API_KEY=your-key

# Or back to free local model
export EMBEDDING_PROVIDER=sentence_transformers
export EMBEDDING_MODEL=all-MiniLM-L6-v2
# No API key needed
```

### Migration Path

**Development → Production:**

1. **Development**: Use Sentence Transformers (FREE)
   ```bash
   EMBEDDING_PROVIDER=sentence_transformers
   ```

2. **Staging**: Test with Voyage AI
   ```bash
   EMBEDDING_PROVIDER=voyage
   EMBEDDING_MODEL=voyage-3.5-lite
   VOYAGE_API_KEY=your-key
   ```

3. **Production**: Use Voyage AI (recommended)
   ```bash
   EMBEDDING_PROVIDER=voyage
   EMBEDDING_MODEL=voyage-3.5-lite
   VOYAGE_API_KEY=your-production-key
   ```

---

## Cost Comparison

### Development Phase

| Provider | Cost | Notes |
|----------|------|-------|
| Sentence Transformers | **$0/month** | FREE, local |
| Voyage AI | ~$5-20/month | Testing usage |
| OpenAI | ~$50-100/month | Testing usage |

**Recommendation**: Use Sentence Transformers for development (FREE)

### Production Phase

| Provider | Cost (per 1M tokens) | Quality | Best For |
|----------|---------------------|---------|----------|
| Voyage AI voyage-3.5-lite | **Lowest** | **Best** | **Production (Recommended)** ✅ |
| OpenAI text-embedding-3-small | ~$0.02 | Excellent | Alternative |
| Sentence Transformers | $0 | Good | If quality acceptable |

**Recommendation**: Use Voyage AI voyage-3.5-lite for production

---

## Setup Instructions

### 1. Install Dependencies

```bash
# For development (FREE)
pip install sentence-transformers

# For production (Voyage AI - recommended)
pip install voyageai

# For production (OpenAI - alternative)
pip install openai  # May already be installed
```

### 2. Get API Keys

**Voyage AI:**
1. Sign up at https://www.voyageai.com/
2. Get API key from dashboard
3. Set `VOYAGE_API_KEY` environment variable

**OpenAI:**
1. Sign up at https://platform.openai.com/
2. Get API key from dashboard
3. Set `OPENAI_API_KEY` environment variable

### 3. Configure Environment

```bash
# .env file
EMBEDDING_PROVIDER=voyage  # or sentence_transformers or openai
EMBEDDING_MODEL=voyage-3.5-lite  # or all-MiniLM-L6-v2 or text-embedding-3-small
VOYAGE_API_KEY=your-key-here  # Only if using Voyage AI
```

### 4. Test Configuration

```python
from rag.services.embedding_service import EmbeddingService
import os

service = EmbeddingService(
    provider=os.getenv("EMBEDDING_PROVIDER", "sentence_transformers"),
    model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
)

# Test embedding
test_text = "This is a test policy document"
embedding = service.embed(test_text)
print(f"Embedding dimension: {len(embedding)}")
print(f"Provider: {service.provider}")
```

---

## Voyage AI voyage-3.5-lite Details

### Model Specifications

- **Model Name**: `voyage-3.5-lite`
- **Dimensions**: 256, 512, 1024, 2048 (configurable)
- **Context Length**: 32,000 tokens
- **Input Types**: "document" or "query" (optimizes for retrieval)
- **Quality**: Outperforms OpenAI v3-large by 6.34% on average
- **Cost**: 6.5x lower than OpenAI

### Usage Example

```python
from rag.services.embedding_service import EmbeddingService

# Initialize with Voyage AI
service = EmbeddingService(
    provider="voyage",
    model="voyage-3.5-lite",
    api_key=os.getenv("VOYAGE_API_KEY")
)

# Embed documents (use input_type="document")
policy_docs = [
    "Term Life 20-Year policy details...",
    "Whole Life policy with cash value...",
]
doc_embeddings = service.embed_batch(
    policy_docs,
    input_type="document"  # Optimized for document storage
)

# Embed query (use input_type="query")
user_query = "affordable life insurance for families"
query_embedding = service.embed(
    user_query,
    input_type="query"  # Optimized for search queries
)

# Use embeddings for semantic search
# ... vector database search code
```

### Best Practices for Voyage AI

1. **Use input_type**: Always specify "document" for policy documents and "query" for user queries
2. **Dimension Selection**: Use 1024 dimensions for good balance (default)
3. **Batch Processing**: Process documents in batches for efficiency
4. **Error Handling**: Handle API rate limits and errors gracefully

---

## Troubleshooting

### Voyage AI Issues

**Problem**: `VOYAGE_API_KEY` not found
- **Solution**: Set environment variable or pass api_key parameter

**Problem**: API rate limits
- **Solution**: Implement retry logic with exponential backoff

**Problem**: Dimension mismatch
- **Solution**: Ensure same dimension used for all embeddings in same vector database

### Provider Switching Issues

**Problem**: Embeddings from different providers have different dimensions
- **Solution**: Re-index vector database when switching providers (dimensions must match)

**Problem**: API key errors
- **Solution**: Verify API key is correct and has sufficient credits

---

## Migration Checklist

When switching embedding providers:

- [ ] Update environment variables
- [ ] Verify API keys are set (if using cloud providers)
- [ ] Test embedding generation
- [ ] **Important**: Re-index vector database (embeddings have different dimensions)
- [ ] Test retrieval quality
- [ ] Monitor costs (if using paid providers)
- [ ] Update documentation

---

## Summary

✅ **Development**: Use Sentence Transformers (FREE)  
✅ **Production**: Use Voyage AI voyage-3.5-lite (Recommended)  
✅ **Alternative**: OpenAI embeddings (if Voyage not available)  
✅ **Switching**: Easy via environment variables - no code changes  
✅ **Cost**: $0 for development, cost-effective for production with Voyage AI  

---

**Next Steps:**
1. Install dependencies: `pip install sentence-transformers voyageai`
2. Get Voyage AI API key (for production)
3. Configure environment variables
4. Test embedding generation
5. Start using in your RAG system!

