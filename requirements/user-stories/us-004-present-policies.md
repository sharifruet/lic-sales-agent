# US-004: Present Company Policies

## User Story
As a **potential customer**
I want to **see information about available life insurance policies**
So that **I can understand my options and make an informed decision**

## Acceptance Criteria

### AC-004.1: Policy Database Access
- Given the system has customer qualifying information
- When presenting policies
- Then the system accesses a comprehensive database of company policies
- And the system presents policies in order of relevance to customer needs
- And policy information is up-to-date and accurate

### AC-004.2: Initial Policy Presentation
- Given the system is ready to present policies
- When showing policies to customer
- Then the system highlights 2-3 most suitable policies initially
- And the system avoids information overload
- And the system provides option to see more policies if needed

### AC-004.3: Structured Policy Information
- Given a policy is being presented
- When showing policy details
- Then the system presents information in structured format including:
  - Policy name and type (term, whole life, universal, etc.)
  - Key features and benefits (as bullet points)
  - Coverage amount range (minimum and maximum)
  - Premium range (monthly/yearly) with factors affecting cost
  - Policy duration/term options
  - Age eligibility requirements
  - Medical examination requirements
  - Claim processing information
- And information is clear and jargon-free

### AC-004.4: Simple Language
- Given policy information includes technical terms
- When presenting to customer
- Then the system uses clear, simple language
- And technical terms are defined when first introduced
- And the system avoids excessive insurance jargon

### AC-004.5: Relevance-Based Presentation
- Given customer has provided qualifying information
- When presenting policies
- Then the system prioritizes policies most relevant to customer's situation
- And the system considers: age, family situation, coverage needs, budget
- And the system explains why each policy might be suitable

### AC-004.6: Examples and Scenarios
- Given a policy is being presented
- When explaining benefits
- Then the system provides real examples relevant to customer's situation
- And examples use customer's age, coverage amount, and circumstances
- And examples help customer understand value proposition

### AC-004.7: Unique Selling Points
- Given company policies are being presented
- When explaining policy benefits
- Then the system emphasizes unique selling points compared to competitors
- And competitive advantages are highlighted naturally
- And comparisons are fact-based

## Detailed Scenarios

### Scenario 1: New Parent Seeking Coverage
**Given**: Customer is 30, has newborn child, needs family protection  
**When**: System presents policies  
**Then**: System prioritizes term life policies with family protection benefits, shows coverage examples for child's education, emphasizes affordability

### Scenario 2: Middle-Aged Professional
**Given**: Customer is 45, has mortgage, wants debt coverage  
**When**: System presents policies  
**Then**: System shows term life matching mortgage duration, explains coverage amounts for debt payoff, presents premium options

### Scenario 3: Senior Seeking Estate Planning
**Given**: Customer is 60, high net worth, wants estate planning  
**When**: System presents policies  
**Then**: System prioritizes whole life/universal life with cash value, explains estate tax benefits, shows long-term value

### Scenario 4: Request More Policies
**Given**: Customer has seen 2-3 policies  
**When**: Customer asks to see more options  
**Then**: System presents additional policies with explanation of differences
- And system provides full policy catalog if requested

## Technical Notes

- Policy database via `PolicyService` and `PolicyRepository`
- Policy matching based on customer profile (age, purpose, dependents)
- Policy information formatted via `PromptManager` and `ContextManager`
- Dynamic example generation based on customer data via LLM
- Policy eligibility checking based on customer age
- Policies included in LLM context for natural presentation

## API Implementation

**Endpoint**: `GET /api/policies/` (public)
**Endpoint**: `GET /api/policies/{policy_id}` (public)

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

**Conversation Integration**:
- Policies retrieved via `PolicyService.list_policies()`
- Top 5 policies included in LLM context
- Policies formatted in system prompts
- LLM presents policies naturally based on customer profile

**Implementation Details**:
- Policy CRUD operations via `PolicyService`
- Policy data stored in PostgreSQL
- Policies included in conversation context
- LLM generates natural policy presentations
- Relevance determined by customer profile matching

## Related Requirements
- **FR-2.1.1**: Comprehensive policy database
- **FR-2.1.2**: Relevance-based ordering
- **FR-2.1.3**: Initial policy count (2-3)
- **FR-2.1.4**: Structured format
- **FR-2.1.5**: Clear, jargon-free language
- **FR-2.1.6**: Unique selling points
- **FR-2.1.7**: Real examples
- **FR-9.1**: Maintain policy database

## Dependencies
- **Depends on**: US-003 (qualifying information)
- **Blocks**: US-006 (policy comparison), US-010 (collect information - needs policy selection)

## Story Points
**Estimate**: 8 points

## Priority
**High** - Core functionality for sales process

## Implementation Status
- **Status**: ✅ Done
- **API Endpoints**: 
  - `GET /api/policies/` - List all policies
  - `GET /api/policies/{id}` - Get policy details
  - `POST /api/policies/` - Create policy (admin)
- **Implementation Notes**: 
  - Policy service and repository implemented
  - Policy CRUD operations
  - Policies included in conversation context
  - LLM-based natural policy presentation
  - Relevance-based selection via customer profile

---

## Implementation Considerations

- ✅ Policy database schema designed and implemented (`Policy` model)
- ✅ Policy matching/recommendation via customer profile
- ✅ Policy presentation via LLM with context
- ✅ Policy eligibility checking (age-based)
- ✅ Dynamic example generation via LLM
- ✅ Policy information caching (can be added for performance)
