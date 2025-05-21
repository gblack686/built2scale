# Conversions.ai Ad Analysis System Overview

## Legend
- 🟡 Addl Details
- 🟠 System Trigger
- ⚪ Agent Action

## Phase 1 - Compile Data

### Data Collection Triggers
1. **Daily or Weekly Trigger Cue** (System Trigger)
   - Sends to Data Compilation Agent

2. **Airtable Form w/Client Info Submitted** (System Trigger)
   - Feeds data to compilation process

### Data Processing Flow
1. Send to Data Compilation Agent
2. Pull BigQuery Dataset/Project by ID
3. Access Data via Storage Read API
4. Decision point: Older than X days?
   - Note: Ignore data to save context length for Model
5. Extract Account Performance Metrics
6. Aggregate from Data & Primary KPIs from Array
7. Create Week Performance Summary
8. Pull Previous Reports from Airtable Database (4-5 Weeks)
9. Send to Reporting Agent

### Key Data Metrics Collected
- **Performance Hierarchies:**
  - Campaign Level
  - Ad Set Level
  - Ad Level

- **Key Performance Indicators:**
  - ROAS
  - CVR
  - Budget

- **Note:** This will be focused primarily on high-level performance metrics. We will want to compare with reports from previous weeks on a campaign, adset and ad level.

## Phase 2 - Analysis

### Analysis Workflow
1. Ad Analysis Agent Trigger
2. Pull Creative Information (Titles, CTAs, Callouts, etc.)
3. Identify trends associated with over/under-performers
4. Compare Current Metrics with Last 4-5 Weeks of Performance
5. Compare Current Metrics with Target Metrics for Brand
6. Compare Underperformers with Previous Winners for each Brand
7. Decision point: Decided Home Brand?
8. Use formula (provided by BTS) and previous reports to generate actionable insights
9. Create New Document from External Report Template
10. Create New Document from Internal Report Template
11. Create Rough Scope of Data Being Pulled (including performance account metrics)

### Report Creation Process
1. Create Executive Client Facing Summary
2. Create Internal Report by Campaign Type
3. Download Document as PDF and Extract Document Link
4. Create Clickup Asset
5. Create Airtable or other DB Record in Reports Table
6. Upload Report to Record & Link to Client Profile
7. Slack Notification sent to Designated Channel

### Report Distribution Links
- Clickup Asset Link
- Airtable Record Link
- Google Doc Link
- Downloadable PDF

### Report Components Breakdown

#### Executive Client Summary Metrics
- Ad Spend
- ROAS
- CPR
- CTR
- CVR %
- Impressions
- Frequency
- CPC
- Engagement Metrics
- Actionable Insights

#### Campaign Analysis Components
1. **Scaling Metrics:**
   - Performance Metrics (e.g. Frequency)
   - Budget Allocation Optimization
   - Compare with Previous Weeks & Targets
   - Create Executive Summary
   - Breakdown on Each Level (Ad, Adset, Campaign)
   - Identify Key Opportunities
   - Immediate, Short-Term and Long-Term Actions

2. **Creative Testing Components:**
   - Click & Action Metrics
   - Video/Image Metrics
   - Audience Response
   - Landing Page Metrics
   - Compare with Winning Creatives & Previous
   - Diagnose Issues using Metrics
   - Breakdown Negative % Dips Appropriately

### Notes
- Airtable is not a necessity for this flow, optional but preferred for ease of access via agents
- Much of the ad-lib reporting help and decision making will be provided by Bulit to Scale, but comprehensive list of what should be included will be included at what depth included in a report

## Scope of Data Being Pulled
- Performance Account Metrics
- Campaign KPIs
- Ad Set & Ad Level Metrics 