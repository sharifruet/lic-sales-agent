# US-005: Provide Competitor Policy Information

## User Story
As a **potential customer**
I want to **learn about competitor policies for comparison**
So that **I can make an informed decision by understanding all available options**

## Acceptance Criteria

### AC-005.1: Accurate Competitor Information
- Given customer asks about competitor policies
- When providing competitor information
- Then the system provides accurate, factual information
- And the system maintains fairness (no false claims)
- And the system acknowledges when information may not be current

### AC-005.2: Strategic Comparison
- Given competitor policies are being discussed
- When presenting competitor information
- Then the system uses competitor information strategically
- And the system highlights company policy advantages naturally
- And comparisons are fair and honest

### AC-005.3: On-Demand Provision
- Given competitor information is available
- When presenting information
- Then the system only discusses competitors when:
  - Customer explicitly asks about competitor
  - Customer requests comparison
  - Customer shows interest in competitor offerings
- And the system doesn't proactively mention competitors unless strategically beneficial

### AC-005.4: Limited Information Handling
- Given customer asks about specific competitor policy
- When system doesn't have detailed information
- Then the system acknowledges the limitation honestly
- And the system offers to help with what is known
- And the system may suggest speaking with sales team for detailed competitor analysis

### AC-005.5: Competitor Policy Information (Optional/Limited)
- Given the system needs competitor information
- When accessing data
- Then the system **may** have limited competitor policy information in the knowledge base
- And competitor information is **optional** and not the primary focus
- And if competitor information exists in knowledge base, it includes: policy names, coverage ranges, typical premiums, key features
- And the system redirects focus to company's own policies when appropriate
- And if detailed competitor information is not available, system acknowledges limitation

## Detailed Scenarios

### Scenario 1: Direct Competitor Question
**Given**: Customer asks "How does your policy compare to Company X?"  
**When**: System responds  
**Then**: System provides accurate comparison, highlights company advantages, remains fair and factual

### Scenario 2: Proactive Mention for Strategic Advantage
**Given**: Customer mentions seeing better rates elsewhere  
**When**: System responds  
**Then**: System acknowledges competitor, explains company value proposition, addresses specific concern (rates) while highlighting other benefits

### Scenario 3: Limited Information
**Given**: Customer asks about niche competitor policy  
**When**: System doesn't have detailed information  
**Then**: System admits limitation, provides general comparison if possible, offers to connect with specialist

### Scenario 4: Unfair Comparison Request
**Given**: Customer asks system to criticize competitor  
**When**: System should respond  
**Then**: System declines to make negative claims, focuses on company strengths, maintains professional tone

## Technical Notes

- Competitor policies can be stored in same `Policy` model with different `provider` field
- Comparison via LLM with policy context
- Update mechanism for competitor data (same as company policies)
- Disclaimer handling for information accuracy
- Integration with company policy database for side-by-side comparison

## API Implementation

**Current Implementation**:
- Policies stored with `provider` field (can be company or competitor)
- `GET /api/policies/` returns all policies
- LLM can compare policies when customer asks
- Policy comparison can be handled via conversation flow

**Future Enhancement**:
- Explicit competitor policy management
- Comparison API endpoint
- Competitor-specific endpoints

**Implementation Details**:
- Policy model supports competitor policies via `provider` field
- LLM can handle competitor questions with policy context
- Fair comparison via system prompts
- Competitor information can be added to policy database

## Related Requirements
- **FR-2.2.1**: Optional/limited competitor information (may be available in knowledge base)
- **FR-2.2.2**: Fairness and accuracy (if competitor info exists)
- **FR-2.2.3**: Redirect focus to company policies
- **FR-2.2.4**: Prioritize company's own policies
- **FR-2.2.5**: Acknowledge when competitor information is not available
- **FR-2.2.6**: Competitor policy information is optional in knowledge base
- **FR-9.7**: Focus on company-specific policies (competitor info optional)

## Dependencies
- **Depends on**: US-004 (policy presentation)
- **Blocks**: US-006 (policy comparison)

## Story Points
**Estimate**: 5 points

## Priority
**Medium** - Important for competitive sales but secondary to company policy presentation

## Implementation Status
- **Status**: ✅ Mostly Implemented (Core functionality complete, enhancements available)
- **Current State**: 
  - ✅ Policy model supports competitor policies via `provider` field
  - ✅ LLM can handle competitor questions with policy context
  - ✅ Intent detection includes `POLICY_COMPARISON` intent
  - ✅ Objection handling includes "comparison" objection type with template
  - ✅ Response filter checks for competitor bashing
  - ✅ System prompts guide fair competitor discussions
  - ⚠️ No explicit competitor policy filtering in API (all policies returned)
  - ⚠️ No dedicated competitor comparison endpoint
  - ⚠️ No competitor-specific policy management UI/API

- **Implementation Details**: 
  - **Policy Model**: `Policy` model has `provider` field that can store company name or competitor name
  - **Intent Detection**: `LLMProvider.classify_intent()` can detect `POLICY_COMPARISON` intent
  - **Objection Handling**: `ConversationService._handle_objection()` handles "comparison" objections using `PromptManager.get_objection_response("comparison", context)`
  - **Response Filtering**: `ResponseFilter` checks for competitor bashing keywords
  - **LLM Context**: Competitor policies are included in LLM context when available
  - **System Prompts**: `PromptManager.INFORMATION_PROMPT` includes guidance to "Compare options when asked"

- **Enhancement Opportunities**:
  1. **Competitor Policy Filtering**: Add `GET /api/policies/?provider=<name>` to filter by provider
  2. **Competitor Comparison Endpoint**: Add `POST /api/policies/compare` with structured comparison response
  3. **Competitor Management**: Add admin endpoints to manage competitor policies separately
  4. **Comparison Templates**: Add structured comparison templates in `PromptManager` for side-by-side comparisons
  5. **Competitor Data Validation**: Add validation to ensure competitor information is accurate and up-to-date

---

## Implementation Considerations

- ✅ **Core Functionality Complete**: Competitor policies work through existing policy system
- ✅ **Fair Comparison**: System prompts and response filters ensure fair, factual comparisons
- ✅ **LLM Integration**: LLM handles competitor questions naturally in conversation flow
- ⚠️ **Enhancement Needed**: Explicit competitor filtering and comparison APIs would improve UX
- ⚠️ **Legal/Compliance**: Consider adding disclaimers for competitor information accuracy
- ⚠️ **Data Management**: Consider separate competitor policy management for easier updates
