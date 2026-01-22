# Current Policy Retrieval System (Pre-RAG)

## Overview

Before implementing the RAG-based knowledge base, the system uses a **traditional relational database** approach to store and retrieve policy information. This document explains how policies are currently managed and retrieved.

---

## Current Architecture

### Database Storage

**Database**: PostgreSQL (or SQLite for development)  
**Storage Type**: Structured relational database  
**Table**: `policies`

### Policy Data Model

Policies are stored as structured records in a SQL database with the following schema:

```python
class Policy(Base):
    __tablename__ = "policies"
    
    id: int                          # Primary key, auto-increment
    name: str                        # Policy name (unique, max 120 chars)
    provider: str                    # Insurance company name (max 120 chars)
    coverage_amount: int             # Coverage amount in currency units
    monthly_premium: float          # Monthly premium amount
    term_years: int                 # Policy term in years
    medical_exam_required: bool     # Whether medical exam is required
    created_at: datetime            # Creation timestamp
    updated_at: datetime            # Last update timestamp
```

**Example Policy Record:**
```python
Policy(
    id=1,
    name="Term Life 20-Year",
    provider="AcmeLife Insurance",
    coverage_amount=500000,
    monthly_premium=50.00,
    term_years=20,
    medical_exam_required=False
)
```

---

## How Policies Are Retrieved

### 1. Direct Database Queries

Policies are retrieved using **SQL queries** through the repository pattern:

#### List All Policies
```python
# Via PolicyService
policies = await policy_service.list_policies()

# SQL Query (under the hood):
# SELECT * FROM policies ORDER BY created_at DESC
```

#### Filter by Provider
```python
# Get company policies
policies = await policy_service.list_company_policies(company_provider="AcmeLife")

# SQL Query:
# SELECT * FROM policies WHERE provider = 'AcmeLife' ORDER BY created_at DESC
```

#### Search by Name
```python
# Search for policies with "Term" in name
policies = await policy_service.list_policies(search="Term")

# SQL Query:
# SELECT * FROM policies WHERE name ILIKE '%Term%' ORDER BY created_at DESC
```

#### Get Single Policy
```python
# Get policy by ID
policy = await policy_service.get_policy(policy_id=1)

# SQL Query:
# SELECT * FROM policies WHERE id = 1
```

### 2. Policy Service Methods

The `PolicyService` provides the following methods for retrieving policies:

#### `list_policies(provider=None, search=None)`
- **Purpose**: List all policies with optional filtering
- **Parameters**:
  - `provider`: Filter by provider name (partial match, case-insensitive)
  - `search`: Search by policy name (partial match, case-insensitive)
- **Returns**: List of Policy objects
- **SQL**: Uses `ILIKE` for case-insensitive partial matching

#### `list_company_policies(company_provider=None)`
- **Purpose**: Get all policies from the company (not competitors)
- **Parameters**:
  - `company_provider`: Company name (defaults to `settings.company_name`)
- **Returns**: List of company policies
- **SQL**: Exact match on provider field

#### `list_competitor_policies(exclude_provider=None)`
- **Purpose**: Get all competitor policies (non-company policies)
- **Parameters**:
  - `exclude_provider`: Provider name to exclude (defaults to company name)
- **Returns**: List of competitor policies
- **SQL**: Filters out policies where provider contains company name

#### `get_policy(policy_id)`
- **Purpose**: Get a single policy by ID
- **Returns**: Policy object or None

#### `compare_policies(policy_ids)`
- **Purpose**: Compare multiple policies side-by-side
- **Returns**: Dictionary with comparison data (coverage ranges, premium ranges, etc.)

---

## How Policies Are Used in Conversations

### 1. Policy Context in LLM Prompts

When generating responses, the system includes policy information in the LLM context:

```python
# From conversation_service.py
if self.policy_service:
    policy_list = await self.policy_service.list_policies()
    policies = [
        {
            "name": p.name,
            "coverage_amount": p.coverage_amount,
            "monthly_premium": float(p.monthly_premium),
            "term_years": p.term_years,
            "medical_exam_required": p.medical_exam_required,
        }
        for p in policy_list[:5]  # Top 5 policies
    ]
    # Policies are included in LLM context
```

### 2. Policy Matching

The system attempts to match policies mentioned in conversations:

```python
# Extract policy names mentioned in recent messages
all_policies = await self.policy_service.list_policies()
for msg in recent_messages:
    if msg.get("role") == "assistant":
        content = msg.get("content", "").lower()
        for policy in all_policies[:5]:
            if policy.name.lower() in content:
                policies_discussed.append(policy.name)
```

### 3. Policy Selection

When a customer expresses interest, the system tracks the selected policy:

```python
# Customer selects a policy
collected_data.policy_of_interest = "Term Life 20-Year"
```

---

## API Endpoints

### Public Endpoints

#### `GET /api/policies/`
List all policies with optional filtering.

**Query Parameters:**
- `provider`: Filter by provider name (partial match)
- `search`: Search by policy name (partial match)

**Example:**
```bash
GET /api/policies/?provider=AcmeLife&search=Term
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Term Life 20-Year",
    "provider": "AcmeLife Insurance",
    "coverage_amount": 500000,
    "monthly_premium": 50.00,
    "term_years": 20,
    "medical_exam_required": false
  }
]
```

#### `GET /api/policies/{policy_id}`
Get a single policy by ID.

#### `GET /api/policies/company`
List all company policies (public endpoint).

#### `POST /api/policies/compare`
Compare multiple policies side-by-side.

**Request:**
```json
{
  "policy_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "policies": [...],
  "comparison_points": {
    "coverage_range": {"min": 100000, "max": 1000000},
    "premium_range": {"min": 30.00, "max": 100.00},
    "term_range": {"min": 10, "max": 30},
    "medical_exam_required_count": 1
  }
}
```

### Admin Endpoints

#### `POST /api/policies/`
Create a new policy (admin only).

**Request:**
```json
{
  "name": "Term Life 20-Year",
  "provider": "AcmeLife Insurance",
  "coverage_amount": 500000,
  "monthly_premium": 50.00,
  "term_years": 20,
  "medical_exam_required": false
}
```

#### `PUT /api/policies/{policy_id}`
Update a policy (admin only, supports partial updates).

#### `DELETE /api/policies/{policy_id}`
Delete or deactivate a policy (admin only).

#### `GET /api/policies/competitors`
List all competitor policies (admin only).

---

## Policy Data Population

### Initial Seeding

Policies are initially populated using a seed script:

**File**: `app/scripts/seed_policies.py`

```python
async def seed():
    items = [
        Policy(
            name="Basic Term 250k",
            provider="AcmeLife",
            coverage_amount=250_000,
            monthly_premium=29.99,
            term_years=20,
            medical_exam_required=False
        ),
        Policy(
            name="Family Term 500k",
            provider="AcmeLife",
            coverage_amount=500_000,
            monthly_premium=54.50,
            term_years=20,
            medical_exam_required=True
        ),
        # ... more policies
    ]
    # Insert into database
```

**Run seed script:**
```bash
python app/scripts/seed_policies.py
```

### Manual Creation

Policies can be created via:
1. **Admin API**: `POST /api/policies/` (requires authentication)
2. **Database directly**: SQL INSERT statements
3. **Admin UI**: (if implemented)

---

## Limitations of Current System

### 1. **Structured Data Only**
- Policies must fit into fixed schema (name, provider, coverage, premium, term, medical exam)
- Cannot store rich policy documents, detailed descriptions, or unstructured content
- Limited to basic attributes

### 2. **Keyword-Based Search**
- Only supports exact or partial string matching (`ILIKE`)
- No semantic understanding
- Cannot find policies based on meaning or intent
- Example: Cannot find "affordable family coverage" without exact keyword match

### 3. **No Contextual Retrieval**
- Policies are retrieved based on exact matches or simple filters
- Cannot retrieve policies based on customer needs or profile
- Example: Cannot find "policies suitable for 30-year-old with family" without manual filtering

### 4. **Limited Policy Information**
- Only stores basic attributes
- Cannot include:
  - Detailed policy descriptions
  - Terms and conditions
  - Exclusions and limitations
  - Benefits and features
  - FAQs
  - Comparison details

### 5. **Static Data**
- Policies are manually entered
- No support for document ingestion
- Updates require manual database changes
- No version control for policy changes

### 6. **No Semantic Understanding**
- LLM receives policy list but cannot understand policy details
- Cannot answer detailed questions about policies
- Cannot compare policies based on nuanced criteria

---

## Example: Current Policy Retrieval Flow

### Scenario: Customer asks "What policies do you have?"

**Current Flow:**

1. **User Query**: "What policies do you have?"

2. **System Retrieval**:
   ```python
   # Conversation service calls policy service
   policies = await policy_service.list_company_policies()
   # Returns: List of Policy objects from database
   ```

3. **SQL Query** (under the hood):
   ```sql
   SELECT * FROM policies 
   WHERE provider = 'AcmeLife Insurance'
   ORDER BY created_at DESC;
   ```

4. **Format for LLM**:
   ```python
   policy_context = [
       {
           "name": "Term Life 20-Year",
           "coverage_amount": 500000,
           "monthly_premium": 50.00,
           "term_years": 20,
           "medical_exam_required": false
       },
       # ... more policies
   ]
   ```

5. **LLM Response**:
   - LLM receives structured policy list
   - Generates natural language response
   - Can only mention policies from the list
   - Cannot provide detailed information beyond basic attributes

**Limitations:**
- ❌ Cannot answer "What's covered in the Term Life policy?"
- ❌ Cannot explain policy benefits in detail
- ❌ Cannot find policies based on customer needs (e.g., "policies for young families")
- ❌ Cannot compare policies based on nuanced criteria

---

## Migration to RAG-Based System

### What Changes with RAG

**Before (Current System):**
- Policies stored as structured records in SQL database
- Retrieved via SQL queries (exact/partial matching)
- Limited to basic attributes
- No semantic understanding

**After (RAG System):**
- Policies stored as documents in vector database
- Retrieved via semantic search (meaning-based)
- Can include full policy documents with rich details
- Semantic understanding of policy content

### Migration Path

1. **Phase 1**: Keep current system running
2. **Phase 2**: Ingest existing policies into vector database
3. **Phase 3**: Update retrieval to use RAG (semantic search)
4. **Phase 4**: Deprecate old SQL-based retrieval

### Backward Compatibility

The RAG system will maintain the same API interface:
- Same endpoints (`GET /api/policies/`)
- Same response format (initially)
- Gradual migration path

---

## Summary

### Current System (Pre-RAG)

✅ **Strengths:**
- Simple structured storage
- Fast SQL queries
- Easy to manage basic policy data
- Works well for simple policy listings

❌ **Limitations:**
- Only structured data (no rich documents)
- Keyword-based search only
- No semantic understanding
- Limited policy information
- Cannot answer detailed questions

### Future System (RAG-Based)

✅ **Improvements:**
- Rich policy documents with full details
- Semantic search (meaning-based retrieval)
- Can answer detailed policy questions
- Context-aware policy recommendations
- Natural language understanding

---

**Next Steps:**
1. Review current policy data structure
2. Prepare policy documents for ingestion
3. Implement RAG-based retrieval (see [Implementation Plan](./rag-knowledge-base-implementation-plan.md))
4. Migrate existing policies to knowledge base

