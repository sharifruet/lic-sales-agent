# US-006: Compare Policy Options

## User Story
As a **potential customer**
I want to **compare different policy options side-by-side**
So that **I can easily see differences and choose the best option for my needs**

## Acceptance Criteria

### AC-006.1: Comparison Request Handling
- Given customer wants to compare policies
- When customer requests comparison
- Then the system enables side-by-side comparison
- And the system can compare 2-4 policies at once
- And the system presents comparison in clear, structured format

### AC-006.2: Consistent Comparison Criteria
- Given policies are being compared
- When presenting comparison
- Then the system uses consistent criteria for all policies:
  - Coverage amounts and flexibility
  - Premium costs (with factors affecting cost)
  - Policy duration/term
  - Benefits and features
  - Eligibility requirements
  - Cash value/returns (if applicable)
- And all policies are evaluated on same criteria

### AC-006.3: Clear Difference Highlighting
- Given policies are being compared
- When showing differences
- Then the system highlights differences clearly
- And the system explains which policy might be better for specific needs
- And differences are explained in simple language

### AC-006.4: Recommendation Based on Comparison
- Given comparison is complete
- When presenting results
- Then the system provides recommendation based on comparison
- And the system explains reasoning for recommendation
- And recommendation considers customer's stated needs and profile

### AC-006.5: Company vs Competitor Comparison
- Given customer wants to compare company and competitor policies
- When performing comparison
- Then the system handles both company and competitor policies
- And the system maintains fairness in comparison
- And the system highlights company advantages where appropriate

### AC-006.6: Comparison Format
- Given policies are being compared
- When presenting comparison
- Then the system uses clear format (table, structured text, or visual)
- And the format is easy to understand
- And important differences stand out

## Detailed Scenarios

### Scenario 1: Compare 2 Company Policies
**Given**: Customer is considering Term Life vs Whole Life  
**When**: Customer requests comparison  
**Then**: System shows side-by-side comparison table with all criteria, highlights key differences, provides recommendation based on customer profile

### Scenario 2: Compare Company vs Competitor
**Given**: Customer wants to compare company policy with competitor  
**When**: Customer requests comparison  
**Then**: System provides fair comparison, highlights company advantages naturally, explains which might be better for customer's situation

### Scenario 3: Multiple Policy Comparison
**Given**: Customer wants to compare 3-4 policies  
**When**: Customer requests comparison  
**Then**: System presents all policies with consistent criteria, summarizes key differences, recommends top 1-2 options

### Scenario 4: Feature-Based Comparison
**Given**: Customer asks "What's the difference between these policies?"  
**When**: System responds  
**Then**: System focuses on differences most relevant to customer's needs, explains practical impact of differences

## Technical Notes

- **RAG-Based Comparison**: Policies retrieved from knowledge base using semantic search
- Policy data retrieved via `PolicyService.search_policies()` from vector database
- Comparison uses retrieved policy context from knowledge base
- Comparison criteria included in LLM prompts with retrieved context
- Recommendation via LLM with customer profile and retrieved policy information
- Structured comparison format via LLM response using retrieved policy details
- All comparison information grounded in knowledge base documents

## API Implementation

**Current Implementation**:
- Policies retrieved via `GET /api/policies/`
- LLM can compare policies when customer asks in conversation
- Comparison handled via conversation flow

**Future Enhancement**:
- Explicit comparison API endpoint
- Structured comparison response format
- Comparison templates

**Implementation Details (RAG-Based)**:
- Policy data retrieved via semantic search from knowledge base (`PolicyService.search_policies()`)
- Top-k relevant policy documents retrieved from vector database
- Retrieved policy context injected into LLM prompt for comparison
- LLM compares policies using ONLY retrieved knowledge base information
- Customer profile included for personalized recommendations
- Comparison handled naturally via conversation using RAG-augmented responses
- All comparison details grounded in actual policy documents from knowledge base

## Related Requirements
- **FR-2.4.1**: Side-by-side comparison (2-4 policies)
- **FR-2.4.2**: Consistent comparison criteria
- **FR-2.4.3**: Highlight differences and provide recommendations
- **FR-2.4.4**: Company vs competitor comparison

## Dependencies
- **Depends on**: US-004, US-005
- **Blocks**: US-010 (customer needs to select policy of interest)

## Story Points
**Estimate**: 6 points

## Priority
**Medium-High** - Helps customers make informed decisions

## Implementation Status
- **Status**: ✅ Mostly Implemented (Core functionality complete, structured format enhancement available)
- **Current State**: 
  - ✅ Policy data available via `PolicyService` and `GET /api/policies/`
  - ✅ LLM can handle comparison requests in conversation flow
  - ✅ Intent detection includes `POLICY_COMPARISON` intent
  - ✅ System prompts guide policy comparisons
  - ✅ Customer profile included in LLM context for personalized recommendations
  - ✅ Multiple policies can be compared (up to 5 policies in context)
  - ⚠️ Comparison is conversational (LLM-generated), not structured format
  - ⚠️ No dedicated comparison API endpoint with structured response
  - ⚠️ No comparison templates for consistent formatting

- **Implementation Details**: 
  - **Policy Retrieval**: `PolicyService.list_policies()` returns all policies, filtered by relevance
  - **LLM Context**: Up to 5 policies included in `ContextManager.build_context()` for LLM
  - **Intent Detection**: `LLMProvider.classify_intent()` detects `POLICY_COMPARISON` intent
  - **System Prompts**: `PromptManager.INFORMATION_PROMPT` includes "Compare options when asked"
  - **Customer Profile**: Customer profile (age, dependents, purpose) included in context for personalized recommendations
  - **Policy Formatting**: `PromptManager._format_policies()` formats policies for LLM context
  - **Conversation Flow**: Comparison handled naturally in `ConversationService.process_message()` when intent is detected

- **Enhancement Opportunities**:
  1. **Structured Comparison Format**: Add `PromptManager.get_comparison_template()` for consistent side-by-side comparisons
  2. **Comparison API Endpoint**: Add `POST /api/policies/compare` with structured JSON response:
     ```json
     {
       "policies": [...],
       "comparison": {
         "coverage": {...},
         "premium": {...},
         "features": {...},
         "recommendation": "..."
       }
     }
     ```
  3. **Comparison Criteria**: Add explicit comparison criteria (coverage, premium, term, features) to prompts
  4. **Visual Comparison**: Add markdown/table formatting for better readability
  5. **Comparison History**: Track which policies were compared for analytics

---

## Implementation Considerations

- ✅ **Core Functionality Complete**: LLM handles policy comparisons naturally in conversation
- ✅ **Personalization**: Customer profile used for relevant recommendations
- ✅ **Multiple Policies**: System can compare multiple policies (up to 5 in context)
- ⚠️ **Structured Format**: Current comparison is conversational; structured format would improve clarity
- ⚠️ **API Endpoint**: Dedicated comparison endpoint would enable programmatic access
- ⚠️ **Consistency**: Comparison templates would ensure consistent comparison criteria across all comparisons
