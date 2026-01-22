# US-002: Agent Introduction & Rapport Building

## User Story
As a **potential customer**
I want to **know that I'm talking to an AI agent and understand its purpose**
So that **I can trust the interaction and understand what to expect**

## Acceptance Criteria

### AC-002.1: AI Agent Identification
- Given a conversation has started
- When the system sends its first few messages (within first 2-3 messages)
- Then the system clearly identifies itself as an AI-powered sales agent
- And the system states its purpose (helping customers understand and choose life insurance)
- And the agent maintains a consistent identity (name, role) throughout

### AC-002.2: Transparency About AI Nature
- Given the agent has identified itself
- When customer directly asks if it's a bot/AI
- Then the system honestly confirms it is an AI agent
- And the system does not misrepresent itself as human
- And the system explains how it can help despite being AI

### AC-002.3: Data Privacy Reassurance
- Given the agent has introduced itself
- When explaining its purpose
- Then the system provides reassurance about data privacy
- And the system explains how customer information will be used
- And the system builds initial trust

### AC-002.4: Name Usage
- Given customer provides their name during conversation
- When the system addresses the customer
- Then the system uses the customer's name appropriately
- And the system doesn't overuse the name (appears natural)
- And the system remembers the name throughout the conversation

### AC-002.5: Empathy and Active Listening
- Given the customer makes a statement or shares concern
- When the system responds
- Then the system acknowledges the customer's statements
- And the system shows empathy (e.g., "I understand that can be a concern...")
- And the system demonstrates active listening by referencing previous statements

### AC-002.6: Positive Reinforcement
- Given customer provides information
- When the system receives the information
- Then the system provides positive acknowledgment
- And the system explains how the information helps
- And the system maintains encouraging, supportive tone

## Detailed Scenarios

### Scenario 1: Standard Introduction
**Given**: New conversation started  
**When**: Agent sends introduction  
**Then**: Customer knows it's AI, understands purpose, feels reassured about privacy

### Scenario 2: Direct Question About AI Nature
**Given**: Conversation in progress  
**When**: Customer asks "Are you a robot?"  
**Then**: Agent honestly confirms it's AI and explains how it can help

### Scenario 3: Name Collection and Usage
**Given**: Customer provides name "John"  
**When**: Agent responds in subsequent messages  
**Then**: Agent uses "John" naturally, not excessively

### Scenario 4: Building Rapport Through Empathy
**Given**: Customer shares concern about cost  
**When**: Agent responds  
**Then**: Agent acknowledges concern empathetically and offers to help find affordable options

## Technical Notes

- Agent persona configured in `PromptManager` (agent_name, company_name)
- System prompts include identity and transparency requirements
- Name extraction via `InformationExtractionService` and stored in `CustomerProfile`
- Empathy and active listening via LLM with context awareness
- Privacy reassurance in system prompts and welcome messages

## API Implementation

**Endpoint**: `POST /api/conversation/start`

**Response** includes welcome message that:
- Identifies agent as AI
- States purpose clearly
- Provides privacy reassurance
- Uses time-appropriate greeting

**Implementation Details**:
- Welcome message generated via `PromptManager.get_welcome_message()`
- Time-based templates (morning/afternoon/evening)
- System prompts enforce AI transparency
- Name extraction and storage in session state
- Context-aware responses via `ContextManager`

## Related Requirements
- **FR-1.2.1**: Clear AI identification within first 2-3 messages
- **FR-1.2.2**: State purpose
- **FR-1.2.3**: Consistent agent identity
- **FR-1.2.4**: No misrepresentation
- **FR-1.2.5**: Data privacy reassurance
- **FR-1.4.1**: Use customer name appropriately
- **FR-1.4.2**: Acknowledge and empathize
- **FR-1.4.3**: Positive reinforcement
- **FR-1.4.4**: Conversational tone
- **FR-1.4.5**: Active listening

## Dependencies
- **Depends on**: US-001
- **Blocks**: US-003, US-008

## Story Points
**Estimate**: 5 points

## Priority
**High** - Critical for trust building and customer experience

## Implementation Status
- **Status**: ✅ Done
- **Implementation Notes**: 
  - Agent introduction in welcome message
  - AI transparency in system prompts
  - Name extraction and usage
  - Empathy via LLM context awareness
  - Privacy reassurance in prompts

---

## Implementation Considerations

- ✅ Agent persona defined in `PromptManager` configuration
- ✅ Name extraction using `InformationExtractionService` (LLM + regex)
- ✅ Customer information stored in conversation context (`SessionState`)
- ✅ Empathy templates in system prompts
- ✅ Privacy policy can be referenced in responses
