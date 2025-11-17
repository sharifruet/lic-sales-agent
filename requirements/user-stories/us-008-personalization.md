# US-008: Personalize Conversation

## User Story
As a **potential customer**
I want the **conversation to be personalized to my situation**
So that **I receive relevant information and feel understood**

## Acceptance Criteria

### AC-008.1: Profile-Based Customization
- Given customer has provided qualifying information
- When conducting conversation
- Then the system customizes messaging based on:
  - Age group (young adults, middle-aged, seniors)
  - Family situation (single, married, with children, caring for parents)
  - Income level indicators (if mentioned)
  - Occupation or profession (if relevant)
  - Life stage (new parent, approaching retirement, career change)
- And personalization appears natural and relevant

### AC-008.2: Name Usage
- Given customer has provided their name
- When addressing customer
- Then the system uses customer's name appropriately
- And the system doesn't overuse the name
- And name usage feels natural in conversation

### AC-008.3: Reference Previous Statements
- Given customer has stated needs, concerns, or goals
- When discussing policies or benefits
- Then the system references previously stated information
- And references appear natural (e.g., "Earlier you mentioned...", "As we discussed...")
- And system demonstrates memory and attention

### AC-008.4: Communication Style Adaptation
- Given customer communicates in specific style
- When system responds
- Then the system adapts language style to match:
  - Formal vs informal tone
  - Detailed vs brief explanations
  - Technical vs simple language preference
- And adaptation feels natural, not forced

### AC-008.5: Policy Interest Memory
- Given customer has shown interest in specific policies
- When continuing conversation
- Then the system remembers and references specific policy interests
- And the system follows up on previously discussed policies
- And the system doesn't repeat entire policy descriptions unnecessarily

### AC-008.6: Personalized Benefits Emphasis
- Given customer has specific situation
- When presenting policy benefits
- Then the system emphasizes benefits most relevant to customer's situation:
  - Family protection for parents
  - Debt coverage for mortgage holders
  - Estate planning for high net worth
  - Business continuity for business owners
- And benefits are presented with customer's specific context

## Detailed Scenarios

### Scenario 1: New Parent Personalization
**Given**: Customer is 30, has newborn, mentioned family protection need  
**When**: System presents policies  
**Then**: System emphasizes child education protection, family security, uses examples with child's future in mind, references "your family" naturally

### Scenario 2: Formal Communication Style
**Given**: Customer uses formal language and detailed questions  
**When**: System responds  
**Then**: System matches formal tone, provides detailed explanations, uses professional language

### Scenario 3: Reference Previous Concerns
**Given**: Customer earlier mentioned mortgage concern  
**When**: System presents term life policy  
**Then**: System references mortgage, explains how coverage matches mortgage duration, addresses original concern

### Scenario 4: Style Adaptation
**Given**: Customer sends brief messages ("yes", "ok", "tell me more")  
**When**: System responds  
**Then**: System adapts to brief style, provides concise information, asks focused questions

## Technical Notes

- Customer profile stored in `SessionState.customer_profile` (age, name, purpose, dependents)
- Communication style detected via LLM context analysis
- Conversation memory via `ContextManager` (maintains message history)
- Personalized template generation via `PromptManager` with customer profile
- Profile-based recommendation via customer profile matching in policy selection
- Dynamic benefit emphasis via LLM with customer context

## API Implementation

**Endpoint**: `POST /api/conversation/message`

**Request**:
```json
{
  "session_id": "abc123...",
  "message": "I'm 35 and have two children"
}
```

**Response**:
```json
{
  "session_id": "abc123...",
  "response": "Since you mentioned you have two children, this policy would protect them...",
  "interest_detected": "medium",
  "conversation_stage": "information",
  "metadata": {
    "message_count": 5,
    "extracted_data": {
      "age": 35,
      "dependents": "two children"
    }
  }
}
```

**Implementation Details**:
- Customer profile maintained in `SessionState`
- Profile included in LLM context via `ContextManager`
- System prompts include customer profile for personalization
- LLM generates personalized responses based on context
- Name usage via profile.name in prompts

## Related Requirements
- **FR-3.3.1**: Customize based on customer profile
- **FR-3.3.2**: Name usage
- **FR-3.3.3**: Reference previous statements
- **FR-3.3.4**: Adapt communication style
- **FR-3.3.5**: Remember policy interests
- **FR-3.4.2**: Prioritize relevant benefits

## Dependencies
- **Depends on**: US-002, US-003
- **Blocks**: None (enhances all conversation features)

## Story Points
**Estimate**: 8 points

## Priority
**High** - Critical for customer experience and conversion

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `POST /api/conversation/message` (with personalization)
- **Implementation Notes**: 
  - Customer profile maintained in session state
  - Profile included in LLM context
  - Personalized responses via LLM
  - Name extraction and usage
  - Context-aware conversation flow

---

## Implementation Considerations

- ✅ Customer profile data model (`CustomerProfile` in `SessionState`)
- ✅ Style detection via LLM context analysis
- ✅ Profile-to-benefit mapping via LLM prompts
- ✅ Personalized response generation via LLM with context
- ✅ Balance between personalization and consistency
- ✅ Personalization feels natural via LLM
