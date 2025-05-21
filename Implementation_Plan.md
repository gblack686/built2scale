# Built To Scale: AI-Powered Reporting System Project Plan

## Project Overview

This plan outlines the implementation of a Python-based reporting system for Built To Scale, focusing on automating ad performance reports similar to the Inkkas Facebook Ads sample. The system will follow the workflow defined in the Miro board, providing both detailed and executive reports.

## Phase 1: Setup & Data Pipeline (Week 1-2)

### 1.1 Environment & Dependencies Setup

```python
# requirements.txt
google-cloud-bigquery==3.11.4
pandas==2.0.3
matplotlib==3.7.2
seaborn==0.12.2
jinja2==3.1.2
python-dotenv==1.0.0
schedule==1.2.0
markdown==3.4.4
weasyprint==59.0  # For PDF generation
```

### 1.2 BigQuery Connection Module

```python
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os

def initialize_bigquery_client():
    """Initialize BigQuery client with credentials."""
    credentials = service_account.Credentials.from_service_account_file(
        'built2scale-credentials.json')
    return bigquery.Client(credentials=credentials, project='built2scale')

def fetch_campaign_data(client, date_range, platform='facebook'):
    """Pull campaign performance data from BigQuery."""
    query = f"""
    SELECT * FROM `built2scale.b2sreporting.v1_b2s_all_acquisition_production_report`
    WHERE date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {date_range} DAY) AND CURRENT_DATE()
    AND advertising_channel = '{platform}'
    """
    return client.query(query).to_dataframe()
```

### 1.3 Data Processing Module

```python
def calculate_health_scores(campaign_df):
    """Calculate health scores for campaigns based on ROAS, CTR, and CPM."""
    # Example health score calculation
    campaign_df['health_score'] = 0
    
    # Add points for good ROAS (example logic)
    campaign_df.loc[campaign_df['roas'] >= 2.0, 'health_score'] += 3
    campaign_df.loc[(campaign_df['roas'] < 2.0) & (campaign_df['roas'] >= 1.5), 'health_score'] += 2
    campaign_df.loc[campaign_df['roas'] < 1.5, 'health_score'] += 0
    
    # Add points for good CTR (example logic)
    campaign_df.loc[campaign_df['ctr'] >= 0.02, 'health_score'] += 3
    campaign_df.loc[(campaign_df['ctr'] < 0.02) & (campaign_df['ctr'] >= 0.01), 'health_score'] += 2
    campaign_df.loc[campaign_df['ctr'] < 0.01, 'health_score'] += 0
    
    # Normalize to 10-point scale
    campaign_df['health_score'] = (campaign_df['health_score'] / 6) * 10
    
    return campaign_df
```

## Phase 2: Analysis Engine (Week 3)

### 2.1 Campaign Analysis Module

```python
def analyze_campaign_performance(df, previous_period_df=None):
    """Analyze campaign performance and identify trends and insights."""
    results = {
        "top_campaigns": df.sort_values('roas', ascending=False).head(3),
        "underperforming_campaigns": df[df['roas'] < 1.0],
        "high_spend_low_return": df[(df['spend'] > df['spend'].quantile(0.75)) & 
                                    (df['roas'] < df['roas'].quantile(0.25))],
        "overall_performance": {
            "total_spend": df['spend'].sum(),
            "total_revenue": df['spend'].sum() * df['roas'].mean(),
            "average_roas": df['roas'].mean(),
            "total_purchases": df['conversions'].sum(),
        }
    }
    
    # Compare to previous period if available
    if previous_period_df is not None:
        results["period_comparison"] = {
            "spend_change": ((df['spend'].sum() / previous_period_df['spend'].sum()) - 1) * 100,
            "roas_change": ((df['roas'].mean() / previous_period_df['roas'].mean()) - 1) * 100,
            "conversion_change": ((df['conversions'].sum() / previous_period_df['conversions'].sum()) - 1) * 100
        }
    
    return results
```

### 2.2 Creative Analysis Module

```python
def analyze_creative_performance(df):
    """Analyze creative performance to identify winning elements."""
    # Group by creative elements and calculate metrics
    creative_analysis = {
        "by_creative_type": df.groupby('creative_type').agg({
            'spend': 'sum',
            'impressions': 'sum',
            'clicks': 'sum',
            'conversions': 'sum'
        }),
        "top_performing_creatives": df.sort_values('roas', ascending=False).head(5),
        "creative_elements": {},  # Would contain analysis of headlines, images, etc.
    }
    
    # Calculate CTR, CPC, CVR for each creative type
    creative_analysis["by_creative_type"]['ctr'] = creative_analysis["by_creative_type"]['clicks'] / creative_analysis["by_creative_type"]['impressions']
    creative_analysis["by_creative_type"]['cpc'] = creative_analysis["by_creative_type"]['spend'] / creative_analysis["by_creative_type"]['clicks']
    creative_analysis["by_creative_type"]['cvr'] = creative_analysis["by_creative_type"]['conversions'] / creative_analysis["by_creative_type"]['clicks']
    
    return creative_analysis
```

## Phase 3: Report Generation (Week 4)

### 3.1 Executive Summary Report Generator

```python
def generate_executive_summary(analysis_results, client_name, platform, date_range):
    """Generate executive summary report in markdown format."""
    template = f"""# {date_range}D {platform.title()} Ads Report for {client_name} - {datetime.now().strftime('%m/%d/%Y')}

## Executive Summary

### Overall Performance
- ROAS: **{analysis_results['overall_performance']['average_roas']:.2f}**
- Total Ad Spend: **${analysis_results['overall_performance']['total_spend']:,.2f}**
- Total Revenue: **${analysis_results['overall_performance']['total_revenue']:,.2f}**
- Total Purchases: **{analysis_results['overall_performance']['total_purchases']}**

### Top Performing Campaigns
{generate_campaign_summary_markdown(analysis_results['top_campaigns'])}

### Recommendations
1. **Budget Allocation:** Increase budget for top-performing campaigns by 15-20%.
2. **Creative Optimization:** Replace underperforming creatives in Campaign X.
3. **Audience Targeting:** Test new lookalike audiences based on recent purchasers.
"""
    return template
```

### 3.2 Detailed Report Generator

```python
def generate_detailed_report(analysis_results, creative_analysis, client_name, platform, date_range):
    """Generate detailed internal report with comprehensive metrics and analysis."""
    # This would be a more extensive template with all the sections from the sample report
    # For brevity, I'm not including the full template here
    template = f"""# {date_range}D {platform.title()} Ads Report for {client_name} - {datetime.now().strftime('%m/%d/%Y')}

## Campaign-Level Metrics Analysis
{generate_campaign_analysis_markdown(analysis_results)}

## Ad Set Analysis
{generate_adset_analysis_markdown(analysis_results)}

## Creative Performance Analysis
{generate_creative_analysis_markdown(creative_analysis)}

## Optimization & Opportunities Summary
{generate_optimization_recommendations(analysis_results, creative_analysis)}

## 7-Day Actionable Plan
{generate_action_plan(analysis_results)}
"""
    return template
```

### 3.3 PDF Generation and Distribution

```python
def convert_to_pdf(markdown_content, output_filename):
    """Convert markdown report to PDF."""
    import markdown
    from weasyprint import HTML
    
    # Convert markdown to HTML
    html = markdown.markdown(markdown_content)
    
    # Add some basic styling
    styled_html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                h1 {{ color: #333366; }}
                h2 {{ color: #333366; border-bottom: 1px solid #cccccc; padding-bottom: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            {html}
        </body>
    </html>
    """
    
    # Generate PDF
    HTML(string=styled_html).write_pdf(output_filename)
    
    return output_filename
```

## Phase 4: Automation & Integration (Week 5)

### 4.1 Scheduling Module

```python
import schedule
import time
from datetime import datetime

def schedule_weekly_reports():
    """Schedule weekly report generation for Monday mornings."""
    # Schedule for Mondays at 7 AM
    schedule.every().monday.at("07:00").do(generate_weekly_reports)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def generate_weekly_reports():
    """Generate weekly reports for all clients."""
    clients = get_active_clients()
    for client in clients:
        try:
            # Generate 7-day report
            client_data = fetch_client_data(client['id'], 7)
            report = process_and_generate_report(client_data, client['name'], 7)
            distribute_report(report, client)
            print(f"Generated report for {client['name']}")
        except Exception as e:
            print(f"Error generating report for {client['name']}: {str(e)}")
```

### 4.2 Integration Module

```python
def distribute_report(report_info, client):
    """Distribute reports through various channels."""
    # Create record in database
    record_id = create_report_record(report_info)
    
    # Upload to Google Drive if configured
    if client.get('google_drive_folder_id'):
        drive_link = upload_to_drive(report_info['pdf_path'], client['google_drive_folder_id'])
        update_report_record(record_id, {'drive_link': drive_link})
    
    # Create ClickUp task if configured
    if client.get('clickup_list_id'):
        task_id = create_clickup_task(client, report_info)
        update_report_record(record_id, {'clickup_task_id': task_id})
    
    # Send Slack notification if configured
    if client.get('slack_webhook'):
        send_slack_notification(client, report_info)
```

## Phase 5: Testing & Refinement (Week 6)

### 5.1 Validation Module

```python
def validate_report_accuracy(report_data, source_data, tolerance=0.01):
    """Validate that report calculations match source data within tolerance."""
    validation_results = {
        'passed': True,
        'issues': []
    }
    
    # Check total spend
    calc_spend = report_data['overall_performance']['total_spend']
    actual_spend = source_data['spend'].sum()
    if abs((calc_spend - actual_spend) / actual_spend) > tolerance:
        validation_results['passed'] = False
        validation_results['issues'].append(f"Total spend mismatch: {calc_spend} vs {actual_spend}")
    
    # Additional validation checks would go here
    
    return validation_results
```

## Complete Project Timeline

| Week | Key Tasks | Deliverables |
|------|-----------|-------------|
| 1 | Environment setup, BigQuery connection | Working data pipeline |
| 2 | Data processing, metric calculation | Data transformation module |
| 3 | Analysis engine, health scoring | Analysis engine |
| 4 | Report templates, PDF generation | Report generation module |
| 5 | Automation, scheduling, integration | Automated weekly reports |
| 6 | Testing, validation, refinement | Final system validation |
| 7 | Documentation, training | System documentation, handover |

## Technical Architecture

```
┌─────────────────┐       ┌───────────────────┐       ┌────────────────────┐
│                 │       │                   │       │                    │
│  Data Sources   │──────▶│  Python ETL &     │──────▶│  Report Generation │
│  (BigQuery)     │       │  Analysis Engine  │       │  & Distribution    │
│                 │       │                   │       │                    │
└─────────────────┘       └───────────────────┘       └────────────────────┘
        │                          │                           │
        │                          │                           │
        ▼                          ▼                           ▼
┌─────────────────┐       ┌───────────────────┐       ┌────────────────────┐
│  Campaign Data  │       │  Performance      │       │  Executive Report  │
│  Ad Set Data    │       │  Analysis         │       │  Detailed Report   │
│  Creative Data  │       │  Health Scoring   │       │  PDF Generation    │
└─────────────────┘       └───────────────────┘       └────────────────────┘
```

This project plan provides a framework for implementing the Built To Scale reporting system using Python, following the workflow from the Miro board and generating reports similar to the Facebook Ads sample. 