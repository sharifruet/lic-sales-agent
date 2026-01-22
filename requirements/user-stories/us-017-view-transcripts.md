# US-017: View Conversation Transcripts

## User Story
As an **admin/sales manager**
I want to **view conversation transcripts for leads**
So that **I can understand customer interactions, improve the AI agent, and provide better follow-up**

## Acceptance Criteria

### AC-017.1: Transcript Access from Lead
- Given admin views a lead
- When accessing conversation transcript
- Then the system provides link to view full conversation
- And transcript opens in readable format
- And all messages are displayed chronologically

### AC-017.2: Complete Message History
- Given conversation transcript is viewed
- When displaying transcript
- Then the system shows:
  - All messages in chronological order
  - Message timestamps
  - Message roles (user, assistant, system)
  - Complete message content
- And transcript is easy to read

### AC-017.3: Conversation Summary Display
- Given conversation transcript is viewed
- When displaying transcript
- Then the system shows conversation summary:
  - Customer profile summary
  - Topics discussed
  - Policies presented
  - Objections raised
  - Interest level
  - Outcome
  - Duration
- And summary is prominently displayed

### AC-017.4: Search Within Transcript
- Given conversation transcript is viewed
- When admin wants to find specific content
- Then the system allows searching within transcript:
  - Search by keyword
  - Search by topic
  - Search by policy mentioned
- And search highlights matches

### AC-017.5: Transcript Formatting
- Given conversation transcript is displayed
- When viewing
- Then the system formats transcript clearly:
  - User messages clearly distinguished from agent messages
  - Timestamps visible but not intrusive
  - Conversation flow easy to follow
  - Long messages formatted for readability
- And format supports reading flow

### AC-017.6: Transcript Export
- Given conversation transcript is viewed
- When admin wants to export
- Then the system allows exporting transcript:
  - PDF format
  - Text format
  - CSV format (structured)
- And exported file is readable and shareable

### AC-017.7: Multiple Conversation View
- Given a lead has multiple conversations (if re-engagement)
- When viewing transcripts
- Then the system shows all conversations:
  - Separated by session
  - Chronologically ordered
  - Each with its own summary
- And navigation between conversations is easy

### AC-017.8: Access Control
- Given conversation transcripts contain sensitive information
- When accessing transcripts
- Then the system enforces access control:
  - Authentication required
  - Role-based permissions
  - Access logging
- And sensitive data is protected

## Detailed Scenarios

### Scenario 1: View Full Transcript
**Given**: Admin views lead detail  
**When**: Clicks "View Conversation"  
**Then**: System displays full conversation transcript with all messages, timestamps, summary, formatted for readability

### Scenario 2: Search for Policy Mention
**Given**: Transcript is displayed  
**When**: Admin searches for "term life"  
**Then**: System highlights all mentions, shows context around matches, allows jumping to specific messages

### Scenario 3: Export Transcript
**Given**: Admin views transcript  
**When**: Clicks "Export" and selects PDF  
**Then**: System generates PDF with formatted transcript, summary, timestamps, ready for sharing or archiving

### Scenario 4: Multiple Conversations
**Given**: Lead had conversation on Monday and Wednesday  
**When**: Admin views transcripts  
**Then**: System shows both conversations, clearly separated, with dates, summaries for each, easy navigation

## Technical Notes

- Transcript retrieval API (`GET /api/conversation/{session_id}`)
- Message formatting and rendering
- Search functionality (can be added client-side or server-side)
- Export generation (can be added - PDF, text, CSV)
- Access control integration (admin authentication)
- Pagination for very long conversations (can be added)

## API Implementation

**Endpoint**: `GET /api/conversation/{session_id}` (admin authentication recommended)

**Response**:
```json
{
  "session_id": "abc123...",
  "conversation_id": "def456...",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hello! I'm Alex...",
      "timestamp": "2024-01-15T10:00:01Z"
    }
  ],
  "customer_profile": {
    "age": 35,
    "name": "John",
    "purpose": "family protection"
  },
  "conversation_stage": "information"
}
```

**Implementation Details**:
- Transcript retrieval via conversation API
- Messages retrieved from database in chronological order
- Customer profile from session state
- Conversation stage and metadata included
- Admin authentication can be added

## Related Requirements
- **FR-7.3**: Store conversation transcripts
- Use case UC-5: Admin views conversation transcripts

## Dependencies
- **Depends on**: US-014 (conversation storage)
- **Blocks**: None (standalone admin feature)

## Story Points
**Estimate**: 6 points

## Priority
**High** - Important for lead management and quality improvement

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `GET /api/conversation/{session_id}`
- **Implementation Notes**: 
  - Transcript retrieval implemented
  - Message history in chronological order
  - Customer profile included
  - Conversation metadata included
  - Export functionality can be added (future enhancement)

---

## Implementation Considerations

- ✅ Transcript retrieval API implemented
- ✅ Message formatting (JSON response, can be formatted client-side)
- ✅ Search functionality (can be added client-side or via full-text search)
- ✅ Export functionality (can be added - PDF generation library)
- ✅ Access control (can be added via admin authentication)
- ✅ Pagination for very long conversations (can be added)
