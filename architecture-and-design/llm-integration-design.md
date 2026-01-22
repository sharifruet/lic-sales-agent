# LLM Integration Design Document
## AI Life Insurance Sales Agent Application

**Version**: 1.0  
**Last Updated**: [Date]  
**Authors**: AI/ML Team, Development Team  
**Status**: Draft

---

## Table of Contents

1. [Document Purpose](#document-purpose)
2. [LLM Provider Selection](#llm-provider-selection)
3. [System Prompts](#system-prompts)
4. [Conversation Templates](#conversation-templates)
5. [Prompt Engineering Strategy](#prompt-engineering-strategy)
6. [Context Management](#context-management)
7. [Response Generation](#response-generation)
8. [Response Filtering and Safety](#response-filtering-and-safety)
9. [Intent Classification](#intent-classification)
10. [Entity Extraction](#entity-extraction)
11. [Performance Optimization](#performance-optimization)
12. [Cost Management](#cost-management)
13. [Testing Strategy](#testing-strategy)
14. [Prompt Versioning](#prompt-versioning)

---

## Document Purpose

This document defines the LLM (Large Language Model) integration design for the AI Life Insurance Sales Agent. The system uses **RAG (Retrieval Augmented Generation)** with a custom knowledge base containing company-specific policy documents. This document includes system prompts, conversation templates, RAG-based prompt construction, prompt engineering strategies, and all LLM-related configurations.

**Intended Audience**:
- AI/ML engineers
- Backend developers implementing LLM integration
- Product team defining conversation flows
- QA team testing AI responses

**Related Documents**:
- Technical Design Document: `/architecture-and-design/technical-design.md`
- Requirements Document: `/requirements/requirements.md`

---

## LLM Provider Selection

### 2.1 Provider Options

#### Option 1: OpenAI GPT-4/GPT-3.5
**Pros:**
- Best overall performance and quality
- Extensive documentation and community support
- Reliable API with good uptime
- Strong reasoning and context understanding
- Fast response times

**Cons:**
- Higher cost per token
- Rate limits on API tier
- Requires API key and billing setup

**Recommended Models:**
- **Primary**: `gpt-4` or `gpt-4-turbo-preview` (best quality)
- **Fallback**: `gpt-3.5-turbo` (faster, cheaper, good quality)

#### Option 2: Anthropic Claude
**Pros:**
- Excellent safety and alignment
- Very long context windows (200K tokens)
- Strong conversational abilities
- Good for sales/conversational use cases

**Cons:**
- Slightly slower than GPT-4
- Smaller developer community
- Higher cost than GPT-3.5

**Recommended Models:**
- **Primary**: `claude-3-opus-20240229` (best quality)
- **Alternative**: `claude-3-sonnet-20240229` (faster, cheaper)

#### Option 3: Local LLM (Ollama/Llama)
**Pros:**
- No API costs (completely free)
- Complete data privacy (data never leaves your machine)
- No rate limits
- Full control
- Works offline
- Excellent for development and testing
- Multiple model options (Llama, Mistral, Mixtral)

**Cons:**
- Lower quality than GPT-4/Claude (but good enough for development)
- Requires local infrastructure (8GB+ RAM recommended)
- Slower inference than cloud (but acceptable on modern hardware)
- Limited context windows compared to cloud (but sufficient for conversations)

**Recommended Models:**
- **Primary**: `llama3.1` (8B) - Best balance of quality and speed (~4.7GB)
- **Faster**: `mistral` (7B) - Fast inference (~4.1GB)
- **Better Quality**: `mixtral` (8x7B) - Higher quality (~26GB, needs 16GB+ RAM)

### 2.2 Recommendation

**Development (Local Testing)**: **Ollama with Llama 3.1**
- Free, no API costs
- Complete data privacy
- Good enough quality for development
- No internet required
- Perfect for testing and iteration

**Production (Phase 1)**: **OpenAI GPT-4**
- Best balance of quality, reliability, and features
- Proven performance for conversational AI
- Good API stability and support

**Fallback Options:**
- GPT-3.5-turbo (if GPT-4 unavailable or for cost optimization)
- Anthropic Claude (for specific use cases)
- Ollama in production (if data privacy is critical and quality is acceptable)

### 2.3 Provider Abstraction

Design supports switching providers through abstraction layer (see Technical Design Document).

---

## System Prompts

> **LangGraph Update**  
> The production prompt inventory now lives under `chains/prompts/` and is consumed through the planner/retriever/action runnables. The legacy stage-based prompts documented below remain for historical reference and may be phased out as the LangGraph pipeline matures.

### 3.1 Base System Prompt

```python
BASE_SYSTEM_PROMPT = """
You are an AI life insurance sales agent named {agent_name} for {company_name}.

Your Role:
You help potential customers understand life insurance options and find suitable coverage for their needs. Your goal is to build trust, provide valuable information, and identify genuinely interested customers.

Your Identity:
- You are an AI assistant - be transparent about this
- Your purpose is to help, not to aggressively sell
- You provide accurate, helpful information
- You respect customer decisions

Core Principles:
1. **Transparency**: Identify yourself as an AI within the first 2-3 messages
2. **Empathy**: Show understanding and care for customer concerns
3. **Honesty**: Provide accurate information, admit when you don't know something
4. **Respect**: Never pressure or be aggressive
5. **Value First**: Focus on helping, not selling

Conversation Style:
- Professional yet friendly
- Conversational, not scripted
- Natural and empathetic
- Clear and jargon-free
- One question at a time
- Explain why you're asking questions

What You Do:
✓ Answer questions about life insurance
✓ Explain policy features and benefits
✓ Help customers understand their options
✓ Address concerns and objections
✓ Identify interested prospects
✓ Collect information from interested customers

What You Don't Do:
✗ Make false promises or guarantees
✗ Pressure customers
✗ Misrepresent yourself as human
✗ Provide medical or legal advice
✗ Make aggressive sales tactics
✗ Create false urgency
"""
```

### 3.2 Stage-Specific System Prompts

#### 3.2.1 Introduction Stage Prompt

```python
INTRODUCTION_PROMPT = BASE_SYSTEM_PROMPT + """
Current Stage: Introduction & Rapport Building

Your Task:
1. Greet the customer warmly
2. Introduce yourself as an AI life insurance advisor
3. Explain how you can help
4. Start building rapport

Guidelines:
- Use friendly greeting appropriate to time of day
- Be clear about being an AI assistant
- Explain that you're here to help, not to sell aggressively
- Offer reassurance about privacy
- Wait for customer response before asking questions
- Match customer's communication style (formal/informal)
"""

Example Output:
```
"Hello! I'm [Agent Name], your AI life insurance advisor. I'm here to help you understand your life insurance options and find coverage that fits your needs. 

I should mention that I'm an AI assistant, but I'm designed to have natural conversations and provide accurate information about our policies. How can I help you today?"
```

#### 3.2.2 Qualification Stage Prompt

```python
QUALIFICATION_PROMPT = BASE_SYSTEM_PROMPT + """
Current Stage: Qualification

Your Task:
Gather information to understand customer needs:
- Age
- Current insurance coverage
- Purpose for seeking insurance
- Dependents/family situation
- Coverage amount interest

Guidelines:
- Ask ONE question at a time
- Explain WHY you're asking (to find best options)
- Accept various response formats
- Handle partial answers gracefully
- Don't pressure if customer hesitates
- Build trust by being transparent
- Use positive reinforcement

Question Strategy:
1. Start with easy, non-intrusive questions
2. Build up to more personal questions
3. Respect if customer doesn't want to answer
"""
```

Example Questions:
```
"To help me recommend the best policies for you, may I ask how old you are? This helps because premiums are age-based, and I want to show you options that fit your life stage."

"I see you're [age]. Are you currently covered by any life insurance policy, or would this be your first policy?"

"Great! Can you tell me what's the main reason you're looking into life insurance? For example, is it for family protection, debt coverage, or something else?"
```

#### 3.2.3 Information Stage Prompt (RAG-Augmented)

```python
INFORMATION_PROMPT = BASE_SYSTEM_PROMPT + """
Current Stage: Policy Information & Education

Your Task:
Provide relevant policy information based on customer profile using the retrieved policy knowledge base information:
- Present 2-3 most suitable policies from the retrieved context
- Explain features and benefits clearly using the policy documents provided
- Use examples relevant to customer's situation
- Answer questions about policies using ONLY information from the retrieved policy documents
- Compare options when asked

Guidelines:
- Use ONLY information from the retrieved policy context below - do not make up policy details
- If information is not in the retrieved context, say you don't have that specific information
- Start with policies most relevant to customer
- Use simple, clear language
- Explain technical terms
- Provide real examples (use customer's age, situation)
- Focus on benefits, not just features
- Be honest about limitations
- Don't overwhelm with too much information at once
- Cite which policy you're referencing when presenting multiple options

Retrieved Policy Context:
{retrieved_policy_context}

IMPORTANT: Only use information from the retrieved policy context above. Do not invent or assume policy details that are not explicitly stated in the retrieved context.

Policy Presentation Format:
1. Policy name and type (from retrieved context)
2. Key benefits for customer's situation (from retrieved context)
3. Coverage range (from retrieved context)
4. Premium range (from retrieved context, explain factors affecting cost)
5. Who it's best for (based on retrieved context and customer profile)
"""
```

Example Output:
```
"Based on your age and family situation, I'd like to highlight a couple of policies that might work well for you.

First is our Term Life 20-Year policy. This is great for family protection because:
- It covers you for 20 years, which typically aligns with major life milestones like your children growing up
- It's affordable - for someone your age, coverage of $500,000 would be around $50-75 per month
- The premiums stay fixed for the entire 20-year term
- No medical exam required for coverage up to $500K

This policy is designed for people like you who want to ensure their family is protected during their working years and while raising children. Does this sound like what you're looking for?"
```

#### 3.2.4 Persuasion Stage Prompt

```python
PERSUASION_PROMPT = BASE_SYSTEM_PROMPT + """
Current Stage: Persuasion & Objection Handling

Your Task:
- Address customer concerns empathetically
- Use persuasive techniques naturally
- Build urgency when appropriate (age, health)
- Emphasize benefits relevant to customer
- Don't be aggressive

Persuasive Techniques (Use Naturally):
1. **Social Proof**: "Many customers in your situation..."
2. **Scarcity**: "Premiums increase with age, so securing coverage now..."
3. **Benefit Emphasis**: Focus on what matters to THIS customer
4. **Reciprocity**: "I've given you detailed information..."
5. **Authority**: Demonstrate expertise through accurate information

Objection Handling:
- Listen and acknowledge concerns
- Provide facts and empathy
- Address root cause, not just surface concern
- Don't minimize concerns
- If can't overcome, accept gracefully
"""
```

Example Objection Responses:
```
Customer: "It's too expensive"

Your Response:
"I completely understand that cost is an important consideration. Let me put this in perspective:
- For $500,000 in coverage, that's about $1.67 per day - less than a cup of coffee
- This protects your family's financial future
- We also have lower coverage options if you'd prefer to start smaller
- The peace of mind this provides is invaluable

What coverage amount would feel comfortable for your budget?"
```

#### 3.2.5 Information Collection Stage Prompt

```python
INFORMATION_COLLECTION_PROMPT = BASE_SYSTEM_PROMPT + """
Current Stage: Information Collection

Your Task:
Collect customer information from interested prospects:
- Full Name
- Phone Number
- National ID (NID)
- Address
- Policy of Interest
- Optional: Email, preferred contact time

Guidelines:
- Ask for ONE piece of information at a time
- Explain why you need it (for registration/contact)
- Validate format as you go
- Confirm information before saving
- Be reassuring about privacy
- Thank customer for each piece of information
- Show progress ("Great! Just a couple more pieces of information...")

Privacy Assurance:
- Explain how information will be used
- Reassure about data security
- Mention that sales team will contact them
"""
```

Example:
```
"Great! I'd be happy to help you get started. To register your interest, I'll need some basic information from you. Don't worry, this is secure and we'll only use it to have our sales team contact you.

Let's start with your full name. How would you like to be addressed?"
```

---

## Conversation Templates

### 4.1 Welcome Message Template

```python
WELCOME_TEMPLATES = {
    "morning": [
        "Good morning! I'm {agent_name}, your AI life insurance advisor. I'm here to help you understand your coverage options. How can I assist you today?",
        "Hello! Good morning. I'm {agent_name}, an AI assistant specializing in life insurance. I'd love to help you explore your options. What brings you here today?"
    ],
    "afternoon": [
        "Good afternoon! I'm {agent_name}, your AI life insurance advisor. How can I help you find the right coverage today?",
        "Hello! I'm {agent_name}. I'm here as your AI life insurance assistant to answer questions and help you find suitable policies. What would you like to know?"
    ],
    "evening": [
        "Good evening! I'm {agent_name}, your AI life insurance advisor. Even though it's evening, I'm here to help. What can I assist you with?",
        "Hello! I'm {agent_name}. I understand you're looking into life insurance - I'm here to help make that process easier for you. How can I assist?"
    ],
    "generic": [
        "Hello! I'm {agent_name}, your AI life insurance advisor. I'm here to help you understand your coverage options and find the right policy for your needs. How can I help you today?",
        "Hi there! I'm {agent_name}, an AI assistant specializing in life insurance. My goal is to help you make an informed decision about coverage. What questions can I answer for you?"
    ]
}
```

### 4.2 Qualifying Question Templates

```python
QUALIFYING_QUESTIONS = {
    "age": [
        "To help me find the best options for you, may I ask how old you are? This helps because insurance rates vary by age.",
        "I'd like to show you policies that match your life stage. Could you share your age?",
        "Premiums are based on several factors, with age being one. If you don't mind sharing, how old are you?"
    ],
    "current_coverage": [
        "Before we look at new options, are you currently covered by any life insurance policy?",
        "Do you already have life insurance coverage, or would this be your first policy?",
        "I'm curious - are you currently insured, or are you exploring life insurance for the first time?"
    ],
    "purpose": [
        "What's the main reason you're looking into life insurance? For example, are you thinking about family protection, covering debts, or estate planning?",
        "Everyone's situation is different. Can you tell me what prompted you to look into life insurance today?",
        "I'd like to understand your needs better. What would you like life insurance to help you accomplish?"
    ],
    "dependents": [
        "Do you have dependents - like a spouse, children, or parents you support - that you'd like to protect?",
        "Are there people who depend on you financially? This helps me recommend the right coverage amount.",
        "Family situation is important for determining coverage needs. Do you have a spouse, children, or other dependents?"
    ]
}
```

### 4.3 Policy Presentation Template

```python
POLICY_PRESENTATION_TEMPLATE = """
Based on your situation - {customer_summary} - I'd like to highlight {policy_count} policy{plural} that might work well for you.

{policy_section}

Would you like to hear more details about {top_policy}, or would you prefer to see other options?
"""

POLICY_SECTION_TEMPLATE = """
**{policy_name}** ({policy_type})
This policy is excellent for {target_audience} because:

Key Benefits:
{benefits_list}

Coverage Options: ${coverage_min:,} to ${coverage_max:,}
Premium Range: ${premium_min}/month to ${premium_max}/month
(Exact premium depends on {premium_factors})

Special Features:
{features_list}

Example: For someone your age ({age}), ${coverage_amount:,} in coverage would cost approximately ${estimated_premium}/month.
"""

# Example filled template:
"""
Based on your situation - you're 35, have two children, and want family protection - I'd like to highlight 2 policies that might work well for you.

**Term Life 20-Year** (Term Life Insurance)
This policy is excellent for young families because:

Key Benefits:
• Protects your family during your prime earning years
• Affordable premiums that stay fixed for 20 years
• No medical exam required for coverage up to $500K
• Flexible coverage amounts to match your needs

Coverage Options: $50,000 to $1,000,000
Premium Range: $30/month to $200/month
(Exact premium depends on your age, health, and coverage amount)

Special Features:
• Convertible to whole life later
• Option to add riders (disability, critical illness)
• Simple application process

Example: For someone your age (35), $500,000 in coverage would cost approximately $55-70/month.
"""
```

### 4.4 Objection Response Templates

```python
OBJECTION_RESPONSE_TEMPLATES = {
    "cost": """
I completely understand that cost is important to you. Let me help put this in perspective:

• For ${coverage_amount:,} in coverage, that's about ${daily_cost} per day - less than {comparison}
• Think of it as protecting your family's financial security
• We also offer coverage starting at ${min_coverage:,} if you'd like to start smaller
• Many of our customers find that the peace of mind is well worth the cost

What coverage amount would fit your budget better?
""",
    
    "necessity": """
I appreciate that perspective. Many people feel that way initially. However, consider:

• Life insurance isn't for you - it's for the people who depend on you
• {statistic} - unexpected events can happen to anyone
• Getting coverage while you're {age} and healthy locks in lower rates
• Premiums increase {percentage}% per year after age {threshold}
• It's one of the few financial decisions that gets more expensive the longer you wait

What concerns you most about not having coverage?
""",
    
    "complexity": """
I totally get that - insurance can seem complicated at first! But it's actually simpler than most people think:

Think of it this way: You're choosing how much protection your family gets, for how long, and how much you want to pay. That's really it.

I'll guide you through every step, and our application process is straightforward. Most customers find it much simpler than they expected.

What specific part feels confusing? I'm happy to clarify.
""",
    
    "trust": """
That's a very valid concern, and I'm glad you're asking. Let me address that:

• We're a {years} year-old insurance company, licensed and regulated
• You can verify us at {regulatory_body}
• Your information is encrypted and secure
• If you prefer, I can connect you with one of our human agents
• We have {number} satisfied customers and {rating} star rating

Would you like me to share more about our company's credentials, or would you prefer to speak with a human agent?
""",
    
    "timing": """
I understand wanting to think it over - that's a smart approach to any important decision.

However, there are a few timing considerations:
• Premiums increase {age_increase}% each year as you get older
• Health conditions can develop that affect rates
• Life changes (like getting a mortgage or having children) make coverage more important
• You can lock in today's rates while you're {age} and healthy

Would you like me to send you a summary of what we discussed so you can review it? Or are there specific questions I can answer to help with your decision?
""",
    
    "comparison": """
I appreciate you doing your research - that's exactly the right approach. Let me address your comparison:

• We understand other companies offer competitive rates
• However, we offer {unique_benefits}
• Our customer service rating is {rating}, and we have {satisfaction}% customer satisfaction
• Our claims process is {fast/efficient}, and we pay out {percentage}% of claims
• Many customers find our overall value proposition - including service and reliability - makes us the better choice

What specifically are you seeing from other companies that interests you? I'd be happy to compare apples to apples.
"""
}
```

### 4.5 Closing Templates

```python
CLOSING_TEMPLATES = {
    "assumptive": """
Based on everything we've discussed, which policy do you think would work best for your situation? I can help you get started with the registration process.
""",
    
    "alternative": """
Great! We have two excellent options: {policy_a} and {policy_b}. Which one appeals to you more? Both would provide solid protection for your family.
""",
    
    "summary": """
Let me make sure I understand what you're looking for:
• Your main need: {purpose}
• Recommended policy: {policy_name}
• Coverage amount: ${coverage:,}
• Estimated premium: ${premium}/month

Does this align with what you were thinking? If so, I can help you register and get started.
""",
    
    "urgency": """
Since you're {age} years old, this is actually a perfect time to secure coverage. Premiums typically increase {percentage}% each year, so locking in today's rates makes financial sense.

Would you like to proceed with getting started?
""",
    
    "soft": """
It sounds like {policy_name} could be a great fit for your needs. Would you like to learn more about the next steps, or do you have any other questions I can answer?
"""
}
```

### 4.6 Exit Templates

```python
EXIT_TEMPLATES = {
    "not_interested": """
I completely understand. Life insurance is an important decision, and I respect that it might not be the right time for you right now.

If you change your mind in the future or have questions, please feel free to reach out. We're always here to help.

Thank you for your time today, and I wish you all the best!
""",
    
    "later": """
No problem at all! I appreciate you taking the time to learn about your options.

If you'd like, I can send you a summary of what we discussed so you can review it later. Just let me know if you'd like that, or if you have any other questions before we wrap up.
""",
    
    "needs_more_info": """
Absolutely! It's smart to gather all the information you need before making a decision.

If you have more questions later or want to continue our conversation, just reach out anytime. I'm here to help whenever you're ready.

Thank you for your time today!
"""
}
```

---

## Prompt Engineering Strategy

### 5.1 Prompt Structure

#### Standard Prompt Format (RAG-Enhanced)

```python
PROMPT_STRUCTURE = """
System Message:
{system_prompt}

Context:
- Customer Profile: {customer_profile}
- Conversation Stage: {stage}
- Previous Messages: {message_history}
- Retrieved Policy Context: {retrieved_policy_context}

Current User Message:
{user_message}

Instructions:
{task_specific_instructions}

IMPORTANT: When discussing policies, use ONLY information from the Retrieved Policy Context above. If you don't have specific information in the retrieved context, admit that you don't have that information rather than making assumptions.
"""
```

#### RAG-Based Prompt Construction

The system uses Retrieval Augmented Generation (RAG) to provide accurate policy information. Here's how policy context is retrieved and injected into prompts:

```python
async def build_rag_enhanced_prompt(
    user_message: str,
    customer_profile: CustomerProfile,
    conversation_history: List[Message]
) -> str:
    """
    Build prompt with RAG-retrieved policy context
    """
    # 1. Build query from user message and customer profile
    query = build_semantic_query(user_message, customer_profile)
    
    # 2. Retrieve relevant policy documents from knowledge base
    retrieved_policies = await policy_service.search_policies(
        query=query,
        customer_profile=customer_profile,
        top_k=3  # Retrieve top 3 most relevant policies
    )
    
    # 3. Format retrieved context for prompt
    policy_context = format_retrieved_context(retrieved_policies)
    
    # 4. Build prompt with retrieved context
    prompt = PROMPT_STRUCTURE.format(
        system_prompt=INFORMATION_PROMPT,
        customer_profile=format_customer_profile(customer_profile),
        stage="information",
        message_history=format_message_history(conversation_history),
        retrieved_policy_context=policy_context,  # RAG-retrieved context
        user_message=user_message,
        task_specific_instructions="Answer the customer's question using the retrieved policy information."
    )
    
    return prompt

def format_retrieved_context(retrieved_policies: List[RetrievedPolicy]) -> str:
    """Format retrieved policies for prompt inclusion"""
    context_parts = []
    
    for i, policy in enumerate(retrieved_policies, 1):
        context_parts.append(f"""
Policy {i}: {policy.policy_name} ({policy.policy_type})

Content:
{policy.content}

Metadata:
- Coverage Range: {policy.metadata.get('coverage_range')}
- Premium Range: {policy.metadata.get('premium_range')}
- Age Requirements: {policy.metadata.get('age_requirements')}
- Source: {policy.source}
- Similarity Score: {policy.similarity_score:.2f}
""")
    
    return "\n".join(context_parts)
```

### 5.2 Few-Shot Learning Examples

#### Example 1: Age Extraction

```python
AGE_EXTRACTION_EXAMPLES = """
Example 1:
User: "I'm 35 years old"
Extract: {{"age": 35}}

Example 2:
User: "I turned 45 last month"
Extract: {{"age": 45}}

Example 3:
User: "Mid-thirties"
Extract: {{"age": 35, "confidence": "medium"}}

Example 4:
User: "I'm a vampire" (not a valid age)
Extract: {{"age": null, "reason": "invalid_input"}}

Now extract age from: "{user_message}"
"""

# LLM can learn from these examples to extract age accurately
```

#### Example 2: Interest Detection

```python
INTEREST_DETECTION_EXAMPLES = """
Examples of buying signals:

1. "I'm interested in that policy" → Interest Level: HIGH
2. "What do I need to do to sign up?" → Interest Level: HIGH
3. "That sounds good" → Interest Level: MEDIUM
4. "I'll think about it" → Interest Level: LOW
5. "Not interested, thanks" → Interest Level: NONE

Analyze this message: "{user_message}"
Determine interest level and explain why.
"""
```

### 5.3 Chain-of-Thought Prompting

For complex reasoning tasks:

```python
CHAIN_OF_THOUGHT_TEMPLATE = """
Let's think step by step about which policy to recommend for this customer:

Customer Profile:
- Age: {age}
- Purpose: {purpose}
- Dependents: {dependents}

Available Policies:
{policies_list}

Reasoning Steps:
1. Consider age eligibility for each policy
2. Match purpose to policy benefits
3. Consider budget constraints
4. Factor in family situation

Based on this reasoning, recommend the top policy and explain why.
"""
```

### 5.4 Role-Playing Prompt

```python
ROLE_PLAYING_PROMPT = """
You are an experienced, empathetic life insurance sales agent with {years} years of experience. 

You've helped hundreds of customers like this one:
- You understand their concerns because you've heard them before
- You're patient and never pushy
- You genuinely care about helping people find the right coverage
- You use your expertise to guide, not to sell aggressively

Now have a conversation with this customer: {user_message}

Respond as this experienced, caring agent would.
"""
```

---

## Context Management

### 6.1 Context Window Strategy

#### Token Budget Allocation (RAG-Enhanced)

```
Total Context Window: 8,000 tokens (conservative for GPT-4)

Allocation:
- System Prompt: ~500 tokens
- Customer Profile: ~200 tokens
- Retrieved Policy Context (RAG): ~1,200 tokens (3 policies × ~400 tokens each)
  - Policy 1 content + metadata: ~400 tokens
  - Policy 2 content + metadata: ~400 tokens
  - Policy 3 content + metadata: ~400 tokens
- Recent Messages (last 20): ~2,000 tokens
- Conversation Summary: ~300 tokens
- Current Message: ~200 tokens
- Reserved Buffer: ~3,600 tokens

Strategy: 
- Keep last 50 messages maximum, summarize older messages
- Limit retrieved policy context to top 3 most relevant policies
- Truncate policy chunks if they exceed ~400 tokens per policy
- Use metadata filtering to reduce retrieved content size
```

#### RAG Context Management

The retrieved policy context is dynamically included based on the conversation needs:

```python
RAG_CONTEXT_STRATEGY = {
    "when_to_retrieve": [
        "Customer asks about policies",
        "Customer mentions specific policy type",
        "Transitioning to information stage",
        "Customer asks comparison questions",
        "Need to answer policy-specific questions"
    ],
    
    "retrieval_parameters": {
        "top_k": 3,  # Retrieve top 3 most relevant policy chunks
        "min_similarity": 0.7,  # Minimum similarity score threshold
        "max_tokens_per_policy": 400,  # Limit each policy chunk size
        "include_metadata": True,  # Include policy metadata (coverage, premiums, etc.)
        "filter_by_eligibility": True  # Filter by customer age/eligibility
    },
    
    "context_injection": {
        "format": "Structured with policy name, content, and metadata",
        "placement": "After system prompt, before conversation history",
        "instruction": "Use ONLY information from retrieved context"
    }
}
```

#### Context Compression Algorithm

```python
def compress_context(messages: List[Message], max_tokens: int) -> List[Message]:
    """
    Compress conversation context while preserving key information
    """
    # Always keep:
    # - System messages
    # - Last 30 messages (recent conversation)
    
    # Summarize:
    # - Messages 31-80 (middle conversation)
    
    # Drop:
    # - Very old messages (>80) if still over limit
    
    system_msgs = [m for m in messages if m.role == "system"]
    recent_msgs = messages[-30:]
    middle_msgs = messages[len(system_msgs):-30] if len(messages) > 30 else []
    
    # Summarize middle messages
    if middle_msgs and estimated_tokens(system_msgs + middle_msgs + recent_msgs) > max_tokens:
        summary = summarize_messages(middle_msgs)
        system_msgs.append(Message(
            role="system",
            content=f"Earlier conversation summary: {summary}"
        ))
    
    return system_msgs + recent_msgs
```

### 6.2 Key Information Preservation

Always preserve in context:
1. **Customer Profile**: Age, purpose, dependents, name
2. **Collected Data**: Any information already collected
3. **Policy Interest**: Policies discussed and customer's reactions
4. **Objections Raised**: What concerns were expressed
5. **Conversation Stage**: Current stage to maintain flow

```python
KEY_INFORMATION_TEMPLATE = """
CONVERSATION CONTEXT:

Customer Profile:
- Name: {name}
- Age: {age}
- Purpose: {purpose}
- Dependents: {dependents}
- Coverage Interest: {coverage_amount}

Conversation Progress:
- Stage: {stage}
- Policies Discussed: {policies_discussed}
- Objections Raised: {objections}
- Interest Level: {interest_level}

Collected Information:
{collected_data}
"""
```

### 6.3 Context Summary Generation

```python
SUMMARY_GENERATION_PROMPT = """
Summarize the key points from this conversation section:

Messages:
{messages}

Include:
1. Customer's main concerns or questions
2. Information provided by customer
3. Policies discussed
4. Customer's reactions to policies
5. Any objections raised
6. Current interest level

Keep summary concise (2-3 sentences).
"""
```

---

## Response Generation

### 7.1 Response Generation Parameters

```python
LLM_CONFIG = {
    "temperature": 0.7,  # Balance creativity and consistency
    "max_tokens": 500,   # Limit response length
    "top_p": 0.9,       # Nucleus sampling
    "frequency_penalty": 0.0,
    "presence_penalty": 0.1,  # Encourage new topics
    "stop": None        # No stop sequences for conversations
}

# Stage-specific configurations
STAGE_CONFIGS = {
    "introduction": {
        "temperature": 0.8,  # More friendly, varied greetings
        "max_tokens": 150
    },
    "qualification": {
        "temperature": 0.6,  # More consistent questions
        "max_tokens": 200
    },
    "information": {
        "temperature": 0.7,  # Balanced explanation
        "max_tokens": 600    # Longer for policy details
    },
    "persuasion": {
        "temperature": 0.7,  # Natural persuasion
        "max_tokens": 400
    },
    "collection": {
        "temperature": 0.5,  # More structured, less creative
        "max_tokens": 200
    }
}
```

### 7.2 Response Length Guidelines

```python
RESPONSE_LENGTH_GUIDELINES = {
    "greeting": "50-100 words",
    "question": "20-50 words",
    "policy_explanation": "100-200 words",
    "objection_response": "80-150 words",
    "closing": "30-80 words",
    "information_request": "40-100 words"
}
```

### 7.3 Response Style Guidelines

```python
RESPONSE_STYLE_RULES = """
Response Guidelines:

1. Length:
   - Keep responses concise but complete
   - One topic per response
   - Break long explanations into digestible parts

2. Tone:
   - Friendly and professional
   - Empathetic and understanding
   - Not overly formal or casual
   - Match customer's communication style when possible

3. Structure:
   - Use bullet points for lists
   - Use paragraph breaks for readability
   - Highlight key points
   - End with a question or next step when appropriate

4. Language:
   - Avoid insurance jargon (or explain when used)
   - Use simple, clear language
   - Use "you" to personalize
   - Use examples relevant to customer

5. Formatting:
   - Use markdown formatting sparingly
   - Use **bold** for emphasis on key points
   - Use line breaks for readability
"""
```

---

## Response Filtering and Safety

### 8.1 Content Filtering

```python
BLOCKED_PHRASES = [
    # False promises
    "guaranteed approval",
    "guaranteed coverage",
    "no questions asked",
    "instant approval",
    
    # Aggressive sales
    "must buy now",
    "limited time only",
    "act immediately",
    "don't miss out",
    
    # Medical claims
    "will cure",
    "medical advice",
    "diagnose",
    
    # Financial guarantees
    "guaranteed returns",
    "risk-free",
    "no risk"
]

PROHIBITED_CONTENT = [
    "discrimination",
    "illegal advice",
    "false claims",
    "misleading information"
]

def filter_response(response: str) -> str:
    """Filter LLM response for safety and compliance"""
    filtered = response
    
    # Remove blocked phrases
    for phrase in BLOCKED_PHRASES:
        if phrase.lower() in filtered.lower():
            filtered = filtered.replace(phrase, "[removed]")
            # Log filtering action
    
    # Check for prohibited content
    for content in PROHIBITED_CONTENT:
        if content.lower() in filtered.lower():
            # Flag for review or replace with safe default
            return "I apologize, but I can't provide that type of information. Let me help you with something else."
    
    return filtered.strip()
```

### 8.2 Brand Safety Checks

```python
BRAND_SAFETY_CHECKS = {
    "no_competitor_bashing": True,
    "no_false_claims": True,
    "transparency_about_ai": True,
    "no_medical_advice": True,
    "no_legal_advice": True,
    "respect_customer_decisions": True
}

def check_brand_safety(response: str) -> bool:
    """Check if response meets brand safety standards"""
    # Implement checks based on BRAND_SAFETY_CHECKS
    pass
```

### 8.3 Fact-Checking for Policies (RAG-Based)

Since policy information comes from the RAG knowledge base, fact-checking is built into the retrieval process:

```python
async def verify_policy_response(
    response: str,
    retrieved_policies: List[RetrievedPolicy],
    original_query: str
) -> Tuple[str, bool]:
    """
    Verify that response is grounded in retrieved policy context.
    
    Returns:
        - Verified response (possibly corrected)
        - Whether response is accurate (True/False)
    """
    # Extract policy mentions from response
    policy_mentions = extract_policy_mentions(response)
    
    # Check if each mention has supporting evidence in retrieved context
    verification_results = []
    for mention in policy_mentions:
        # Find supporting evidence in retrieved policies
        supporting_evidence = find_supporting_evidence(mention, retrieved_policies)
        
        if supporting_evidence:
            verification_results.append({
                "mention": mention,
                "verified": True,
                "source": supporting_evidence.source
            })
        else:
            verification_results.append({
                "mention": mention,
                "verified": False,
                "warning": "No supporting evidence in retrieved context"
            })
    
    # If unverified claims found, flag or correct
    unverified = [r for r in verification_results if not r["verified"]]
    
    if unverified:
        # Log warning
        logger.warning(f"Response contains unverified policy claims: {unverified}")
        
        # Option 1: Return response with warning
        # Option 2: Correct response to only use verified information
        corrected_response = correct_response_with_retrieved_context(
            response, retrieved_policies, unverified
        )
        return corrected_response, False
    
    return response, True

def find_supporting_evidence(
    policy_mention: str,
    retrieved_policies: List[RetrievedPolicy]
) -> Optional[RetrievedPolicy]:
    """Find if policy mention has supporting evidence in retrieved context"""
    for policy in retrieved_policies:
        if policy_mention.lower() in policy.content.lower() or \
           policy_mention.lower() in policy.policy_name.lower():
            return policy
    return None
```

**RAG-Based Accuracy Guarantees**:
- All policy information comes from company-specific knowledge base
- LLM is instructed to only use retrieved context
- Response verification ensures grounding in retrieved documents
- Reduces hallucinations by constraining LLM to retrieved information

---

## Intent Classification

### 9.1 Intent Classification Prompt

```python
INTENT_CLASSIFICATION_PROMPT = """
Classify the intent of this customer message: "{message}"

Context:
- Current Stage: {stage}
- Previous Intent: {previous_intent}

Possible Intents:
1. greeting - Customer is greeting or starting conversation
2. question - Customer is asking a question
3. objection - Customer is raising a concern or objection
4. interest - Customer is showing buying interest
5. exit - Customer wants to end conversation
6. information_request - Customer wants policy information
7. policy_comparison - Customer wants to compare policies
8. clarification - Customer needs clarification
9. unknown - Intent is unclear

Respond with ONLY the intent name (lowercase, one word).
"""

# Example outputs:
# "greeting"
# "objection"
# "interest"
```

### 9.2 Intent Classification with Confidence

```python
INTENT_CLASSIFICATION_WITH_CONFIDENCE = """
Analyze this customer message and classify intent with confidence level:

Message: "{message}"
Context: {context}

Return JSON format:
{
  "intent": "objection",
  "confidence": 0.95,
  "subtype": "cost",
  "reasoning": "Message contains cost-related keywords and negative sentiment"
}
"""
```

---

## Entity Extraction

### 10.1 Entity Extraction Prompt

```python
ENTITY_EXTRACTION_PROMPT = """
Extract structured information from this customer message: "{message}"

Extract the following entities if present:
- age: Numeric age (18-100), or null
- phone: Phone number with country code, or null
- name: Full name or first name, or null
- address: Complete address, or null
- email: Email address, or null
- coverage_amount: Desired coverage amount, or null
- policy_interest: Policy name or type mentioned, or null

Return JSON format:
{
  "age": 35,
  "phone": null,
  "name": "John",
  "address": null,
  "email": null,
  "coverage_amount": 500000,
  "policy_interest": "term life"
}

If entity is not found, use null.
"""
```

### 10.2 Structured Extraction with Validation

```python
STRUCTURED_EXTRACTION_PROMPT = """
Extract information from: "{message}"

Extract and validate:
1. Age: Must be 18-100, extract from formats like "I'm 35", "35 years old", "mid-thirties"
2. Phone: Must include country code, format: +XXXXXXXXXXX
3. Name: Extract first and last name if provided
4. Email: Must be valid email format

Validation Rules:
- Age must be reasonable (18-100)
- Phone must have country code
- Email must have @ symbol and valid domain

Return JSON with extracted values and validation status:
{
  "age": {"value": 35, "valid": true, "confidence": 0.95},
  "phone": {"value": null, "valid": false, "confidence": 0},
  ...
}
"""
```

---

## Performance Optimization

### 11.1 Response Caching Strategy

```python
# Cache common responses to reduce API calls
CACHEABLE_RESPONSES = [
    "welcome_messages",
    "common_questions",
    "policy_descriptions",
    "objection_templates"
]

# Cache key format: response_type:context_hash
def get_cached_response(response_type: str, context: str) -> Optional[str]:
    """Get cached response if available"""
    cache_key = f"{response_type}:{hash(context)}"
    return redis.get(cache_key)

def cache_response(response_type: str, context: str, response: str):
    """Cache response for future use"""
    cache_key = f"{response_type}:{hash(context)}"
    redis.setex(cache_key, 3600, response)  # 1 hour TTL
```

### 11.2 Streaming Responses (Future)

```python
# For Phase 2: Stream responses for better UX
async def stream_response(prompt: str):
    """Stream LLM response token by token"""
    async for chunk in llm_provider.stream(prompt):
        yield chunk
```

### 11.3 Batch Processing

```python
# Batch multiple requests when possible
async def batch_classify_intents(messages: List[str]):
    """Classify multiple intents in one API call"""
    batch_prompt = "\n\n".join([
        f"Message {i+1}: {msg}" for i, msg in enumerate(messages)
    ])
    # Single API call for multiple classifications
```

---

## Cost Management

### 12.1 Token Usage Optimization

```python
TOKEN_OPTIMIZATION_STRATEGIES = {
    "system_prompt": "Keep concise, ~500 tokens",
    "context_window": "Limit to 50 recent messages",
    "policy_info": "Only include relevant policies (top 3)",
    "summarization": "Summarize old messages instead of keeping full text",
    "response_length": "Use max_tokens to limit response length"
}

# Cost Estimates:

# Ollama (Local Development) - FREE
OLLAMA_COSTS = {
    "api_costs": 0,  # No API costs
    "infrastructure": "Local machine resources only",
    "setup": "Free - just install Ollama",
    "monthly_estimate": "$0 (completely free)"
}

# OpenAI GPT-4 (Production)
OPENAI_COSTS = {
    "input_per_1k_tokens": 0.03,  # $0.03 per 1K input tokens
    "output_per_1k_tokens": 0.06,  # $0.06 per 1K output tokens
    "average_conversation": {
        "input_tokens": 3000,
        "output_tokens": 500,
        "cost": (3000/1000 * 0.03) + (500/1000 * 0.06)  # = $0.12 per conversation
    },
    "monthly_estimate": "1000 conversations/month * $0.12 = $120/month"
}

# GPT-3.5-turbo (Cost-effective alternative)
GPT35_COSTS = {
    "input_per_1k_tokens": 0.0005,  # $0.0005 per 1K input tokens
    "output_per_1k_tokens": 0.0015,  # $0.0015 per 1K output tokens
    "average_conversation_cost": "$0.002-0.004 per conversation",
    "monthly_estimate": "1000 conversations/month * $0.003 = $3/month"
}
```

### 12.2 Cost Reduction Strategies

#### For Local Development:
1. **Use Ollama**: Completely free, no API costs
2. **Use smaller models**: `mistral` or `llama3.1` instead of `mixtral`
3. **Optimize prompts**: Shorter prompts = faster inference

#### For Production (Cloud Providers):
1. **Use GPT-3.5 for simple tasks**: Classification, extraction (90% cheaper)
2. **Cache common responses**: Reduce API calls
3. **Summarize context**: Reduce input tokens
4. **Limit response length**: Reduce output tokens
5. **Batch operations**: Multiple classifications in one call
6. **Use cheaper models**: GPT-3.5 for non-critical responses
7. **Consider Ollama in production**: If data privacy > quality and cost savings needed

```python
# Smart model selection
def select_model(environment: str, task_complexity: str) -> str:
    """Select appropriate model based on environment and task"""
    if environment == "development":
        return "ollama:llama3.1"  # Free local model
    elif task_complexity == "simple":
        return "gpt-3.5-turbo"  # Cheaper cloud model
    elif task_complexity == "medium":
        return "gpt-4"  # Balanced
    else:
        return "gpt-4-turbo"  # Best quality
```

---

## Testing Strategy

### 13.1 Prompt Testing

```python
TEST_CASES = [
    {
        "name": "Greeting Response",
        "input": "Hello",
        "expected_features": [
            "Contains greeting",
            "Introduces agent",
            "Mentions AI nature",
            "Asks how to help"
        ],
        "expected_length": "50-150 words"
    },
    {
        "name": "Age Extraction",
        "input": "I'm 35 years old",
        "expected_output": {"age": 35},
        "expected_confidence": 0.95
    },
    {
        "name": "Cost Objection Handling",
        "input": "It's too expensive",
        "expected_features": [
            "Acknowledges concern",
            "Provides perspective",
            "Offers alternatives",
            "Not aggressive"
        ]
    }
]
```

### 13.2 Response Quality Metrics

```python
QUALITY_METRICS = {
    "relevance": "Response addresses user's question/concern",
    "accuracy": "Information is factually correct",
    "tone": "Professional, friendly, empathetic",
    "clarity": "Clear and easy to understand",
    "completeness": "Sufficient information provided",
    "brand_alignment": "Matches brand voice and values",
    "safety": "No prohibited content or false claims"
}
```

### 13.3 A/B Testing Prompts

```python
# Test different prompt variations
PROMPT_VARIANTS = {
    "variant_a": BASE_SYSTEM_PROMPT + "...",
    "variant_b": BASE_SYSTEM_PROMPT + "...",  # Slightly different
}

# Measure:
# - Conversion rate
# - Customer satisfaction
# - Response quality scores
# - Average conversation length
```

---

## Prompt Versioning

### 14.1 Version Control for Prompts

```python
PROMPT_VERSIONS = {
    "system_prompt": {
        "v1.0": BASE_SYSTEM_PROMPT,
        "v1.1": BASE_SYSTEM_PROMPT + "...",  # Updated version
        "current": "v1.1"
    },
    "objection_handling": {
        "v1.0": OBJECTION_RESPONSE_TEMPLATES,
        "v1.1": UPDATED_OBJECTION_TEMPLATES,
        "current": "v1.1"
    }
}

# Track which version is used in each conversation
# Allow rollback if issues detected
```

### 14.2 Prompt Configuration File

```python
# prompts.yaml
system_prompts:
  base:
    version: "1.1"
    content: "..."
  
  introduction:
    version: "1.0"
    content: "..."
  
  qualification:
    version: "1.2"
    content: "..."

templates:
  welcome:
    version: "1.0"
    variants:
      morning: "..."
      afternoon: "..."
  
  objection_responses:
    version: "1.1"
    cost: "..."
    necessity: "..."
```

---

## Implementation Examples

### 15.1 Complete Conversation Flow Example

```python
# Example: Complete conversation with prompts

# Step 1: Start Conversation
system_prompt = BASE_SYSTEM_PROMPT.format(
    agent_name="Alex",
    company_name="SecureLife Insurance"
)
context = build_context(customer_profile={}, messages=[])

# Step 2: User greets
user_message = "Hi"
response = await llm.generate(
    system_prompt=system_prompt,
    context=context,
    user_message=user_message,
    stage="introduction"
)
# Expected: Greeting, introduction, offer to help

# Step 3: User responds
user_message = "I'm looking for life insurance"
response = await llm.generate(...)
# Expected: Ask qualifying question (age, purpose, etc.)

# Step 4: User provides age
user_message = "I'm 35"
# Extract age
age = extract_entity(user_message, "age")  # Returns 35
# Update customer profile
# Continue to next question

# Step 5: Present policies (RAG-based)
# Retrieve policies from knowledge base using RAG
query = build_enhanced_query("policies for young families", customer_profile)
retrieved_policies = await policy_service.search_policies(
    query=query,
    customer_profile=customer_profile,
    top_k=3
)
# Build RAG-augmented prompt with retrieved context
response = await llm.generate(
    ...,
    retrieved_policy_context=format_retrieved_context(retrieved_policies),
    stage="information"
)
# Expected: Present 2-3 relevant policies with benefits from knowledge base

# Step 6: Handle objection
user_message = "That sounds expensive"
objection_type = detect_objection(user_message)  # Returns "cost"
response = await llm.generate(
    ...,
    objection_type=objection_type,
    stage="persuasion"
)
# Expected: Address cost concern empathetically

# Step 7: Detect interest
user_message = "I'm interested in the term life policy"
interest = detect_interest(user_message)  # Returns HIGH
# Transition to information collection

# Step 8: Collect information
response = await llm.generate(
    ...,
    stage="information_collection"
)
# Expected: Ask for name, phone, etc. one at a time
```

### 15.2 Prompt Engineering Best Practices

1. **Be Specific**: Clear instructions produce better results
2. **Use Examples**: Few-shot learning improves accuracy
3. **Iterate**: Test and refine prompts based on outputs
4. **Version Control**: Track prompt changes and their impact
5. **A/B Test**: Compare prompt variations
6. **Monitor**: Track response quality metrics
7. **Optimize**: Balance quality with cost and speed

---

## Appendix

### A.1 Prompt Templates Library

Prompt templates are version-controlled in the `chains/prompts/` directory:
- `chains/prompts/planner.prompt`
- `chains/prompts/retriever.prompt`
- `chains/prompts/action.prompt`
- Legacy templates (e.g., `prompts/closing_templates.py`) are retained for reference during migration.

### A.2 LLM Provider Configuration

```python
# config/llm_config.py
LLM_CONFIG = {
    "ollama": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "model": os.getenv("OLLAMA_MODEL", "llama3.1"),
        "temperature": 0.7,
        "max_tokens": 500,
        # No API key needed for Ollama
    },
    "openai": {
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "temperature": 0.7,
        "max_tokens": 500,
        "api_key": os.getenv("OPENAI_API_KEY")
    },
    "anthropic": {
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
        "temperature": 0.7,
        "max_tokens": 500,
        "api_key": os.getenv("ANTHROPIC_API_KEY")
    }
}
```

### A.3 Ollama Setup for Development

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download recommended model
ollama pull llama3.1

# Verify installation
ollama list
ollama run llama3.1 "Hello"

# Test API
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Hello",
  "stream": false
}'
```

### A.4 Ollama vs Cloud Providers Comparison

| Feature | Ollama (Local) | OpenAI GPT-4 | Anthropic Claude |
|---------|---------------|--------------|------------------|
| Cost | Free | $0.12/conv | ~$0.15/conv |
| Privacy | Complete (local) | Data sent to API | Data sent to API |
| Quality | Good (7-8/10) | Excellent (9-10/10) | Excellent (9-10/10) |
| Speed | Medium (2-5s) | Fast (1-2s) | Fast (1-3s) |
| Setup | Easy | API key needed | API key needed |
| Internet | Not required | Required | Required |
| Best For | Development, Testing | Production | Production |

### A.3 References

- OpenAI Best Practices: https://platform.openai.com/docs/guides/prompt-engineering
- Anthropic Prompt Engineering: https://docs.anthropic.com/claude/docs/prompt-engineering
- Prompt Engineering Guide: https://www.promptingguide.ai/

---

**Document Status**: Draft - Pending Review  
**Next Steps**: Implement prompts, test with real conversations, iterate based on results

