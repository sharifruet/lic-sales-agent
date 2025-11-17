# US-027: Lead Generation Analytics

## User Story
As an **admin/manager**
I want to **view analytics about lead generation**
So that **I can track lead generation performance and optimize conversion**

## Acceptance Criteria

### AC-027.1: Lead Metrics
- Given admin accesses lead analytics
- When viewing lead metrics
- Then the system displays:
  - Total leads generated in period
  - Leads by source (conversation, direct entry)
  - Leads by policy interest
  - Lead generation rate (leads/conversations)
  - Lead status distribution
  - Average time to lead conversion
- And metrics are accurate and up-to-date

### AC-027.2: Time Period Selection
- Given analytics dashboard
- When admin selects time period
- Then the system filters lead metrics by selected period
- And metrics update accordingly
- And period selection is flexible (1-365 days)

### AC-027.3: Policy Interest Analysis
- Given lead analytics
- When viewing policy interest
- Then the system shows:
  - Number of leads per policy
  - Most popular policies
  - Policy interest trends
- And analysis helps identify popular products

### AC-027.4: Conversion Funnel
- Given lead generation data
- When analyzing conversion
- Then the system shows:
  - Conversation to interest conversion
  - Interest to information collection conversion
  - Information collection to lead conversion
  - Overall conversion rate
- And funnel helps identify bottlenecks

## Detailed Scenarios

### Scenario 1: View Lead Metrics
**Given**: Admin accesses analytics  
**When**: Viewing last 30 days  
**Then**: System shows total leads, generation rate, policy distribution, status breakdown

### Scenario 2: Policy Interest Analysis
**Given**: Admin views policy analytics  
**When**: Analyzing interest  
**Then**: System shows most popular policies, trends, recommendations

### Scenario 3: Conversion Funnel
**Given**: Admin views conversion data  
**When**: Analyzing funnel  
**Then**: System shows conversion rates at each stage, identifies bottlenecks, suggests improvements

## Technical Notes

- Analytics service with database queries
- Lead aggregation and calculation
- Policy interest analysis
- Conversion funnel calculation
- Performance optimization

## API Implementation

**Endpoint**: `GET /api/analytics/leads`

**Query Parameters**:
- `days`: Number of days to analyze (default: 7, range: 1-365)

**Response**:
```json
{
  "period_days": 7,
  "total_leads": 30,
  "leads_by_policy": {
    "Term Life 20-Year": 15,
    "Whole Life": 10,
    "Term Life 10-Year": 5
  },
  "lead_generation_rate_percent": 20.0,
  "leads_by_status": {
    "new": 25,
    "contacted": 3,
    "converted": 2
  },
  "avg_time_to_lead_seconds": 1800
}
```

**Implementation Details**:
- `AnalyticsService` with lead queries
- Aggregation logic for metrics
- Policy interest analysis
- Conversion rate calculation
- Admin authentication required

## Related Requirements
- **FR-9.3**: View lead generation metrics
- **FR-9.4**: Analyze conversion funnel
- **NFR-18**: Logging and monitoring capabilities

## Dependencies
- **Depends on**: US-013 (store leads)
- **Blocks**: None

## Story Points
**Estimate**: 5 points

## Priority
**Medium** - Phase 2 feature

## Implementation Status
- **Status**: ✅ Done
- **API Endpoint**: `GET /api/analytics/leads`
- **Implementation Notes**: 
  - Lead analytics service implemented
  - Lead metrics calculation
  - Policy interest analysis
  - Conversion rate calculation
  - Admin authentication required

