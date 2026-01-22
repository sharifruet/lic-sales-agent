# Free Embedding Models Setup Guide

## Overview

For local development, you can use **completely FREE** embedding models that run locally on your machine. No API keys, no usage limits, no costs!

## Recommended: Sentence Transformers (100% FREE)

**Sentence Transformers** is an open-source library that provides high-quality embedding models that run entirely on your local machine.

### Why Use Free Embeddings for Development?

✅ **$0 Cost** - No API fees, no usage limits  
✅ **Complete Privacy** - Data never leaves your machine  
✅ **Works Offline** - No internet required after initial download  
✅ **Fast** - Quick inference on modern CPUs  
✅ **Good Quality** - Excellent for development and testing  
✅ **Easy Setup** - Single `pip install` command  

---

## Installation

### Step 1: Install Sentence Transformers

```bash
pip install sentence-transformers
```

That's it! The library will automatically download the model on first use.

### Step 2: Verify Installation

```python
from sentence_transformers import SentenceTransformer

# Load model (downloads automatically on first use, ~80MB)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Test embedding generation
text = "This is a test insurance policy document"
embedding = model.encode(text)

print(f"Embedding dimension: {embedding.shape[0]}")  # Should be 384
print(f"Embedding sample: {embedding[:5]}")  # First 5 values
```

---

## Recommended Models

### 1. all-MiniLM-L6-v2 (Recommended - Default)

**Best for: General development**

- **Size**: ~80MB
- **Dimensions**: 384
- **Speed**: Very fast on CPU
- **Quality**: Good for semantic search
- **Use Case**: Default choice for most scenarios

```python
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### 2. all-mpnet-base-v2 (Better Quality)

**Best for: When you need higher quality**

- **Size**: ~420MB
- **Dimensions**: 768
- **Speed**: Slower than all-MiniLM-L6-v2
- **Quality**: Higher quality embeddings
- **Use Case**: When quality is more important than speed

```python
model = SentenceTransformer('all-mpnet-base-v2')
```

### 3. multi-qa-MiniLM-L6-cos-v1 (Optimized for Q&A)

**Best for: RAG/Question-Answering scenarios**

- **Size**: ~80MB
- **Dimensions**: 384
- **Speed**: Very fast
- **Quality**: Optimized specifically for question-answering
- **Use Case**: Perfect for RAG retrieval scenarios

```python
model = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
```

---

## Integration with RAG System

### Update Embedding Service

```python
# rag/services/embedding_service.py
from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service with FREE local model.
        
        Args:
            model_name: Sentence Transformers model name
                - "all-MiniLM-L6-v2" (default, recommended)
                - "all-mpnet-base-v2" (better quality)
                - "multi-qa-MiniLM-L6-cos-v1" (optimized for Q&A)
        """
        print(f"Loading embedding model: {model_name} (FREE, local)")
        self.model = SentenceTransformer(model_name)
        print(f"Model loaded successfully! Dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text (FREE, local)"""
        embedding = self.model.encode(text, show_progress_bar=False)
        return embedding.tolist()
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (FREE, local)"""
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()
```

### Environment Configuration

```bash
# .env
# Embedding Configuration (FREE for development)
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=all-MiniLM-L6-v2

# No API key needed! Works completely locally.
```

### Usage Example

```python
from rag.services.embedding_service import EmbeddingService

# Initialize (FREE, downloads model on first use)
service = EmbeddingService(model_name="all-MiniLM-L6-v2")

# Generate single embedding
query = "policies for young families"
embedding = service.embed(query)
print(f"Query embedding: {len(embedding)} dimensions")  # 384

# Generate batch embeddings (very fast)
documents = [
    "Term Life 20-Year policy with family protection benefits",
    "Whole Life policy with cash value accumulation",
    "Universal Life policy with flexible premiums"
]
embeddings = service.embed_batch(documents)
print(f"Generated {len(embeddings)} embeddings")
```

---

## Performance Comparison

| Model | Size | Dimensions | Speed | Quality | Best For |
|-------|------|-----------|-------|---------|----------|
| all-MiniLM-L6-v2 | 80MB | 384 | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | **Development (Recommended)** |
| all-mpnet-base-v2 | 420MB | 768 | ⚡⚡ Medium | ⭐⭐⭐⭐ Better | Higher quality needs |
| multi-qa-MiniLM-L6-cos-v1 | 80MB | 384 | ⚡⚡⚡ Fast | ⭐⭐⭐⭐ Good for Q&A | RAG/Retrieval |

**Speed Test (on modern CPU):**
- all-MiniLM-L6-v2: ~1000 sentences/second
- all-mpnet-base-v2: ~200 sentences/second
- multi-qa-MiniLM-L6-cos-v1: ~1000 sentences/second

---

## Cost Comparison

### Development Phase

**Using OpenAI Embeddings (Paid):**
- Cost: ~$0.02 per 1M tokens
- For 10,000 policy chunks: ~$0.20 per ingestion
- Monthly development usage: ~$50-100/month

**Using Sentence Transformers (FREE):**
- Cost: **$0/month** ✅
- Same functionality
- No usage limits
- Perfect for development!

### Production Phase

You have options:

1. **Continue with Sentence Transformers** (FREE)
   - Cost: $0/month
   - Quality: Good for most use cases
   - Recommended if quality is acceptable

2. **Upgrade to OpenAI Embeddings** (Paid)
   - Cost: ~$100-300/month (depending on usage)
   - Quality: Excellent
   - Use if quality improvements justify cost

---

## Migration Path

### Development → Production

**Phase 1: Development (FREE)**
```python
# Use FREE local model
service = EmbeddingService(
    provider="sentence_transformers",
    model="all-MiniLM-L6-v2"
)
```

**Phase 2: Production Testing (Compare)**
```python
# Test both options
free_service = EmbeddingService(provider="sentence_transformers")
paid_service = EmbeddingService(provider="openai")  # If needed

# Compare quality and choose
```

**Phase 3: Production (Your Choice)**
- Option A: Continue with Sentence Transformers (FREE)
- Option B: Upgrade to OpenAI (if quality justifies cost)

---

## Best Practices

### 1. Model Selection

**For Development:**
- Use `all-MiniLM-L6-v2` (default, fastest, good quality)

**For Production:**
- Start with `all-MiniLM-L6-v2` 
- Evaluate quality
- Upgrade to `all-mpnet-base-v2` if needed (still FREE!)
- Consider OpenAI only if quality still insufficient

### 2. Batch Processing

Always use batch embedding for multiple texts (much faster):

```python
# ✅ Good: Batch processing
embeddings = service.embed_batch(documents)  # Fast

# ❌ Slow: Individual embeddings
embeddings = [service.embed(doc) for doc in documents]  # Slow
```

### 3. Model Caching

Sentence Transformers automatically caches models:
- First use: Downloads model (~80MB)
- Subsequent uses: Uses cached model (instant)

Model location: `~/.cache/torch/sentence_transformers/`

### 4. Memory Considerations

- **all-MiniLM-L6-v2**: ~150MB RAM
- **all-mpnet-base-v2**: ~600MB RAM
- Both work fine on most development machines

---

## Troubleshooting

### Model Download Issues

If model download fails:

```bash
# Download manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Performance Issues

If embeddings are slow:

1. Use `all-MiniLM-L6-v2` (fastest option)
2. Process in batches (not individual texts)
3. Consider GPU acceleration (optional):
   ```python
   model = SentenceTransformer('all-MiniLM-L6-v2')
   # Automatically uses GPU if available
   ```

### Memory Issues

If you run out of memory:

1. Use smaller model (`all-MiniLM-L6-v2` instead of `all-mpnet-base-v2`)
2. Process documents in smaller batches
3. Clear model from memory after use (if needed)

---

## Example: Complete Setup

```python
# 1. Install (one time)
# pip install sentence-transformers

# 2. Initialize service
from rag.services.embedding_service import EmbeddingService

service = EmbeddingService(model_name="all-MiniLM-L6-v2")

# 3. Generate embeddings for policy documents
policy_documents = [
    "Term Life 20-Year: Coverage $50K-$1M, Premium $30-$200/month...",
    "Whole Life: Permanent coverage with cash value, Premium varies...",
    # ... more policy documents
]

# Batch embedding generation (fast and FREE)
embeddings = service.embed_batch(policy_documents)

# 4. Store in vector database
# ... vector database storage code

# 5. Query embeddings (also FREE)
query = "affordable life insurance for young families"
query_embedding = service.embed(query)

# 6. Search vector database with query embedding
# ... semantic search code
```

---

## Resources

- **Sentence Transformers Documentation**: https://www.sbert.net/
- **Model Hub**: https://huggingface.co/models?library=sentence-transformers
- **All-MiniLM-L6-v2 Model**: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- **Model Comparison**: https://www.sbert.net/docs/pretrained_models.html

---

## Summary

✅ **FREE embedding models available for local development**  
✅ **Sentence Transformers recommended** (all-MiniLM-L6-v2)  
✅ **$0 cost** - No API fees or usage limits  
✅ **Easy setup** - Single pip install  
✅ **Good quality** - Perfect for development and many production scenarios  
✅ **Fast** - Quick inference on CPU  

**For local development, you don't need to pay for embeddings!**

---

**Next Steps:**
1. Install: `pip install sentence-transformers`
2. Test: Run the example code above
3. Integrate: Update your `EmbeddingService` to use Sentence Transformers
4. Enjoy: Zero-cost embedding generation! 🎉

