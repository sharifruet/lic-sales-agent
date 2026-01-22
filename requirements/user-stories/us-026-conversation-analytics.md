# US-026: Conversation Analytics

## User Story
As an **admin/manager**
I want to **view analytics about conversations**
So that **I can understand conversation performance and optimize the agent**

## Acceptance Criteria

### AC-026.1: Conversation Metrics
- Given admin accesses analytics
- When viewing conversation metrics
- Then the system displays:
  - Total conversations in period
  - Total messages exchanged
  - Average conversation duration
  - Average messages per conversation
  - Conversations by stage distribution
  - Conversion rate (leads/conversations)
- And metrics are accurate and up-to-date

### AC-026.2: Time Period Selection
- Given analytics dashboard
- When admin selects time period
- Then the system filters metrics by selected period (last 7 days, 30 days, etc.)
- And metrics update accordingly
- And period selection is flexible (1-365 days)

### AC-026.3: Stage Distribution
- Given conversation analytics
- When viewing stage metrics
- Then the system shows:
  - Number of conversations in each stage
  - Stage progression patterns
  - Average time in each stage
- And distribution is visualized clearly

### AC-026.4: Quality Scoring
- Given a specific conversation
- When viewing quality metrics
- Then the system provides quality score based on:
  - Conversation completeness
  - Customer engagement
  - Information collected
  - Outcome (lead generated or not)
- And score is meaningful and actionable

## Detailed Scenarios

### Scenario 1: View Overall Metrics
**Given**: Admin accesses analytics  
**When**: Viewing last 7 days  
**Then**: System shows total conversations, messages, duration, conversion rate, stage distribution

### Scenario 2: Quality Score Review
**Given**: Admin views specific conversation  
**When**: Checking quality  
**Then**: System provides quality score, rating (excellent/good/fair/poor), and breakdown

### Scenario 3: Timeline Analysis
**Given**: Admin views timeline  
**When**: Analyzing trends  
**Then**: System shows conversation volume over time, identifies patterns, highlights trends

## Technical Notes

- Analytics service with database queries
- Aggregation and calculation logic
- Time period filtering
- Quality scoring algorithm
- Performance optimization for large datasets

## API Implementation

**Endpoint**: `GET /api/analytics/conversations`

**Query Parameters**:
- `days`: Number of days to analyze (default: 7, range: 1-365)

**Response**:
```json
{
  "period_days": 7,
  "total_conversations": 150,
  "total_messages": 1250,
  "avg_conversation_duration_seconds": 420,
  "avg_messages_per_conversation": 8.3,
  "conversations_by_stage": {
    "introduction": 150,
    "qualification": 120,
    "information": 80,
    "persuasion": 50,
    "information_collection": 30,
    "closing": 15,
    "ended": 150
  },
  "conversion_rate_percent": 20.0
}
```

**Additional Endpoints**:
- `GET /api/analytics/conversation/{id}/quality` - Quality score for specific conversation
- `GET /api/analytics/timeline` - Timeline data

**Implementation Details**:
- `AnalyticsService` with database queries
- Aggregation logic for metrics
- Quality scoring algorithm
- Time period filtering
- Admin authentication required

## Related Requirements
- **FR-9.1**: View conversation metrics
- **FR-9.2**: Analyze conversation quality
- **NFR-18**: Logging and monitoring capabilities

## Dependencies
- **Depends on**: US-014 (store conversations)
- **Blocks**: None

## Story Points
**Estimate**: 8 points

## Priority
**Medium** - Phase 2 feature

## Implementation Status
- **Status**: ✅ Done
- **API Endpoints**: 
  - `GET /api/analytics/conversations`
  - `GET /api/analytics/conversation/{id}/quality`
  - `GET /api/analytics/timeline`
- **Implementation Notes**: 
  - Analytics service fully implemented
  - Conversation metrics calculation
  - Quality scoring algorithm
  - Time period filtering
  - Admin authentication required

