# Facebook Ads Report Analysis
This notebook connects to BigQuery to analyze Facebook Ads performance data and helps recreate the insights from the '7D Facebook Ads Report for Inkkas.md'.


```python
# 1. Import necessary libraries
from google.cloud import bigquery
from google.oauth2 import service_account # Added for service account
import pandas as pd
from datetime import date, timedelta
# import os # Not strictly needed if passing credentials directly to client

# 2. Configure your BigQuery client using Service Account
# Path to your service account key file, relative to the notebook's location
credentials_path = "../built2scale-2c7cc11e1ca6.json"

# Load credentials from the service account file
try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    project_id = credentials.project_id # Get project_id from credentials
    print(f"Successfully loaded credentials for project: {project_id}")
except Exception as e:
    print(f"Error loading service account credentials from {credentials_path}: {e}")
    print("Please ensure the path is correct and the file is valid JSON.")
    # You might want to raise the exception or exit if credentials fail to load
    credentials = None # Ensure client initialization below handles this
    project_id = "built2scale" # Fallback to known project_id if credentials fail

# Ensure dataset_id is still set by the user if not in credentials (it usually isn't)
dataset_id = "b2sreporting" # Dataset ID from schema_summary.md

# Instantiate the BigQuery client
if credentials:
    client = bigquery.Client(project=project_id, credentials=credentials)
    print(f"Connected to BigQuery project: {client.project} using service account.")
else:
    # Fallback to default or prompt for action if credentials failed
    print("Attempting to connect to BigQuery with default credentials or expecting an error.")
    client = bigquery.Client(project=project_id) # This will likely use ADC or fail

# 3. Define your target end date for the 7-day report (adjust as needed)
your_target_end_date = date.today() # Or a specific date like date(2025, 4, 12)
your_target_start_date = your_target_end_date - timedelta(days=7)

print(f"Reporting period: {your_target_start_date} to {your_target_end_date - timedelta(days=1)}")

# 4. Define the primary table for analysis
table_name = "v1_b2s_all_acquisition_production_report"
# Important: Ensure dataset_id is correctly set above by the user!
table_id = f"`{project_id}.{dataset_id}.{table_name}`"


print(f"Using table: {table_id}")

# 5. Define the SQL query for Overall 7-Day Summary Metrics
sql_overall_summary = f"""
SELECT
    COUNT(DISTINCT campaign_id) AS number_of_active_campaigns, -- Assuming 'active' is implicit or add filter for active status
    SUM(spend) AS total_spend,
    SUM(conversion_value) AS total_revenue,
    SUM(conversions) AS total_purchases,
    SUM(impressions) AS total_impressions,
    SUM(reach) AS total_reach,
    SUM(clicks) AS total_clicks,
    SUM(leads) AS total_leads,
    (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS overall_roas,
    (SUM(spend) / NULLIF(SUM(conversions), 0)) AS overall_cpp,
    (SUM(spend) / NULLIF(SUM(leads), 0)) AS overall_cpl,
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS overall_ctr,
    (SUM(impressions) / NULLIF(SUM(reach), 0)) AS overall_frequency,
    (SUM(spend) / NULLIF(SUM(impressions), 0)) * 1000 AS overall_cpm -- CPM is (Spend/Impressions)*1000
FROM
    {table_id}
WHERE
    -- Assuming 'date' is a TIMESTAMP or DATE field in your BigQuery table
    DATE(date) >= '{your_target_start_date.strftime('%Y-%m-%d')}' AND DATE(date) < '{your_target_end_date.strftime('%Y-%m-%d')}'
    -- Add filter for 'active' campaigns if such a column (e.g., 'active' with value 'TRUE' or 'ACTIVE') exists:
    -- AND active = 'TRUE' 
"""

print("\nExecuting Overall Summary Query:")
print(sql_overall_summary)

# 6. Execute the query and load results into a pandas DataFrame
try:
    if client.project: # Proceed only if client was successfully initialized
        query_job_overall = client.query(sql_overall_summary)  # Make an API request.
        df_overall_summary = query_job_overall.to_dataframe()  # Waits for the job to complete.

        # 7. Display the results
        print("\nOverall 7-Day Performance Summary:")
        # Transpose for better readability if it's a single row of summary stats
        if len(df_overall_summary) == 1:
            print(df_overall_summary.T.to_string())
        else:
            print(df_overall_summary.to_string()) # .to_string() helps to see all columns if wide
    else:
        print("BigQuery client not fully initialized due to credential or project_id issue. Query not executed.")

except Exception as e:
    print(f"An error occurred: {e}")

```

## I. Executive Facebook Campaign Summary (Continued)
### Campaign Performance Highlights\n\nThis section breaks down performance by individual campaigns over the last 7 days, ordered by Return on Ad Spend (ROAS).


```python
# 8. Define SQL for Campaign Performance Highlights (7-Day)
sql_campaign_highlights = f"""
SELECT
    campaign_name,
    campaign_id,
    SUM(spend) AS campaign_spend,
    SUM(conversion_value) AS campaign_revenue,
    SUM(conversions) AS campaign_purchases,
    SUM(impressions) AS campaign_impressions,
    SUM(clicks) AS campaign_clicks,
    (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS campaign_roas,
    (SUM(spend) / NULLIF(SUM(conversions), 0)) AS campaign_cpp,
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS campaign_ctr
FROM
    {table_id} # This uses the table_id defined in the first code cell
WHERE
    DATE(date) >= '{your_target_start_date.strftime('%Y-%m-%d')}' AND DATE(date) < '{your_target_end_date.strftime('%Y-%m-%d')}'
    # Add filter for 'active' campaigns if such a column exists:
    # AND active = 'TRUE'
GROUP BY
    campaign_name, campaign_id
ORDER BY
    campaign_roas DESC
LIMIT 10 # Display top 10 performing campaigns by ROAS
"""

print("\nExecuting Campaign Performance Highlights Query:")
print(sql_campaign_highlights)

# 9. Execute the query and load into a pandas DataFrame
try:
    query_job_campaigns = client.query(sql_campaign_highlights)
    df_campaign_highlights = query_job_campaigns.to_dataframe()

    # 10. Display the results
    print("\nTop Campaign Performance Highlights (Last 7 Days):")
    print(df_campaign_highlights.to_string())

except Exception as e:
    print(f"An error occurred while fetching campaign highlights: {e}")

```

## II. Audience Engagement & Lead Generation Summary

This section focuses on how users are interacting with the ads (engagement) and the effectiveness of the campaigns in generating leads.

**Note:** The primary data table (`v1_b2s_all_acquisition_production_report`) does not contain direct metrics for video views or specific landing page views. The analysis below is based on available fields like clicks, impressions, and leads. `unique_outbound_clicks` could be considered as a proxy for traffic driven to landing pages if needed for further custom analysis, though it's not explicitly part of the summary statistics from the markdown report.


```python
# 11. Display Audience Engagement & Lead Generation Metrics from Overall Summary
print("\n--- Audience Engagement & Lead Generation Summary ---")

if 'df_overall_summary' in locals() and not df_overall_summary.empty:
    total_clicks = df_overall_summary['total_clicks'].iloc[0]
    overall_ctr = df_overall_summary['overall_ctr'].iloc[0]
    total_leads = df_overall_summary['total_leads'].iloc[0]
    overall_cpl = df_overall_summary['overall_cpl'].iloc[0]
    
    print(f"\nTotal Clicks (Last 7 Days): {total_clicks:,.0f}")
    print(f"Overall Average CTR (Last 7 Days): {overall_ctr:.2%}")
    print(f"Total Leads Captured (Last 7 Days): {total_leads:,.0f}")
    print(f"Overall Average Cost Per Lead (CPL) (Last 7 Days): ${overall_cpl:,.2f}")
else:
    print("\nOverall summary data (df_overall_summary) not available. Please run the first code cell.")

# 12. Define SQL for Campaign with Highest CTR (7-Day)
sql_highest_ctr_campaign = f"""
SELECT
    campaign_name,
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS campaign_ctr
FROM
    {table_id} # This uses the table_id defined in the first code cell
WHERE
    DATE(date) >= '{your_target_start_date.strftime('%Y-%m-%d')}' AND DATE(date) < '{your_target_end_date.strftime('%Y-%m-%d')}'
GROUP BY
    campaign_name
HAVING
    SUM(impressions) > 0
ORDER BY
    campaign_ctr DESC
LIMIT 1
"""

print("\nExecuting Query for Campaign with Highest CTR:")
# print(sql_highest_ctr_campaign) # Optional: print the query itself

try:
    query_job_highest_ctr = client.query(sql_highest_ctr_campaign)
    df_highest_ctr = query_job_highest_ctr.to_dataframe()

    print("\nCampaign with Highest CTR (Last 7 Days):")
    if not df_highest_ctr.empty:
        print(f"- Campaign: {df_highest_ctr['campaign_name'].iloc[0]}")
        print(f"- CTR: {df_highest_ctr['campaign_ctr'].iloc[0]:.2%}")
    else:
        print("No campaign data found for highest CTR.")

except Exception as e:
    print(f"An error occurred while fetching the highest CTR campaign: {e}")

# 13. Define SQL for Campaign with Most Efficient (Lowest) CPL (7-Day)
sql_lowest_cpl_campaign = f"""
SELECT
    campaign_name,
    (SUM(spend) / NULLIF(SUM(leads), 0)) AS campaign_cpl
FROM
    {table_id} # This uses the table_id defined in the first code cell
WHERE
    DATE(date) >= '{your_target_start_date.strftime('%Y-%m-%d')}' AND DATE(date) < '{your_target_end_date.strftime('%Y-%m-%d')}'
GROUP BY
    campaign_name
HAVING
    SUM(leads) > 0
ORDER BY
    campaign_cpl ASC
LIMIT 1
"""

print("\nExecuting Query for Campaign with Lowest CPL:")
# print(sql_lowest_cpl_campaign) # Optional: print the query itself

try:
    query_job_lowest_cpl = client.query(sql_lowest_cpl_campaign)
    df_lowest_cpl = query_job_lowest_cpl.to_dataframe()

    print("\nCampaign with Most Efficient (Lowest) CPL (Last 7 Days):")
    if not df_lowest_cpl.empty:
        print(f"- Campaign: {df_lowest_cpl['campaign_name'].iloc[0]}")
        print(f"- CPL: ${df_lowest_cpl['campaign_cpl'].iloc[0]:,.2f}")
    else:
        print("No campaign data found for lowest CPL (ensure campaigns have generated leads).")

except Exception as e:
    print(f"An error occurred while fetching the lowest CPL campaign: {e}")

print("\nReminder: Specific metrics like detailed video views and landing page views are not directly available from the current table.")

```

## III. Product Category Performance (Inferred)

This section provides an overview of performance based on inferred product categories or campaign types, derived from keywords in campaign names. This aligns with the qualitative insights from the example report.

**Note:** These categorizations are based on common naming conventions. Actual product category performance might require more granular data or specific product category tags if available in other tables.


```python
# 14. Analyze Performance by Inferred Product Categories
print("\n--- Product Category Performance (Inferred, Last 7 Days) ---")

def get_category_performance(category_name, like_conditions):
    conditions_sql = " OR ".join([f"LOWER(campaign_name) LIKE '{condition.lower()}'" for condition in like_conditions])
    query = f"""
    SELECT
        '{category_name}' AS inferred_category,
        SUM(spend) AS total_spend,
        SUM(conversion_value) AS total_revenue,
        SUM(conversions) AS total_purchases,
        (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS roas
    FROM
        {table_id} # Uses table_id from the first code cell
    WHERE
        DATE(date) >= '{your_target_start_date.strftime('%Y-%m-%d')}' AND DATE(date) < '{your_target_end_date.strftime('%Y-%m-%d')}'
        AND ({conditions_sql})
    """
    try:
        query_job = client.query(query)
        df_category = query_job.to_dataframe()
        return df_category
    except Exception as e:
        print(f"An error occurred while querying for {category_name}: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

# Define categories and their corresponding campaign name keywords
categories_to_analyze = {
    "Footwear (Boots, Slip Ons)": ["%boot%", "%slip on%", "%slip-on%"],
    "Clearance Campaigns": ["%clearance%"],
    "DPA Campaigns": ["%dpa%"],
    "UGC Testing Campaigns": ["%ugc test%", "%ugc%"] # Broader UGC match
}

all_category_dfs = []

for cat_name, keywords in categories_to_analyze.items():
    print(f"\nFetching data for: {cat_name}")
    df_cat = get_category_performance(cat_name, keywords)
    if not df_cat.empty and pd.notna(df_cat['total_spend'].iloc[0]) and df_cat['total_spend'].iloc[0] > 0:
        print(df_cat.to_string(index=False))
        all_category_dfs.append(df_cat)
    elif not df_cat.empty and (pd.isna(df_cat['total_spend'].iloc[0]) or df_cat['total_spend'].iloc[0] == 0):
        print(f"No significant spend or data found for {cat_name}.")
    else:
        print(f"No data returned for {cat_name} or an error occurred.")

# Combine into a single DataFrame for a summary table if dfs exist
if all_category_dfs:
    df_inferred_categories_summary = pd.concat(all_category_dfs, ignore_index=True)
    print("\nSummary Table for Inferred Categories (where data was found):")
    print(df_inferred_categories_summary.to_string(index=False))
else:
    print("\nNo data found for any of the inferred categories.")

print("\nQualitative Insights from example report (for context):")
print("- Footwear categories (Slip Ons, Camping Boots, Trekk Boots) consistently show higher ROAS compared to accessory collections.")
print("- The Clearance campaign indicates successful performance of discounted products.")
print("- The DPA (Dynamic Product Ads) campaign shows moderate performance with 1.31 ROAS, effectively retargeting previous site visitors.")
print("- The most recently launched campaign April 2025 UGC Testing is showing early promise with a positive ROAS of 1.25 despite limited data.")


```

## IV. Facebook Campaign Performance Overview (Last 3 Days)

This section delves into a more granular look at campaign performance over the recent 3-day period.


```python
# 15. Define date range for 3-Day analysis
three_day_target_end_date = date.today()
three_day_target_start_date = three_day_target_end_date - timedelta(days=3)

print(f"Reporting period for 3-Day analysis: {three_day_target_start_date} to {three_day_target_end_date - timedelta(days=1)}")

# 16. Define SQL for Campaign-Level Metrics (Last 3 Days)
sql_campaign_metrics_3day = f"""
SELECT
    campaign_name,
    campaign_id,
    SUM(spend) AS spend_3day,
    SUM(conversion_value) AS revenue_3day,
    SUM(conversions) AS purchases_3day,
    SUM(impressions) AS impressions_3day,
    SUM(clicks) AS clicks_3day,
    (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS roas_3day,
    (SUM(spend) / NULLIF(SUM(conversions), 0)) AS cpp_3day,
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS ctr_3day
FROM
    {table_id} # Uses table_id from the first code cell
WHERE
    DATE(date) >= '{three_day_target_start_date.strftime('%Y-%m-%d')}' AND DATE(date) < '{three_day_target_end_date.strftime('%Y-%m-%d')}'
    # Add filter for 'active' campaigns if such a column exists:
    # AND active = 'TRUE'
GROUP BY
    campaign_name, campaign_id
ORDER BY
    roas_3day DESC
"""

print("\nExecuting 3-Day Campaign-Level Metrics Query:")
# print(sql_campaign_metrics_3day) # Optional: print the query

try:
    query_job_campaigns_3day = client.query(sql_campaign_metrics_3day)
    df_campaign_metrics_3day = query_job_campaigns_3day.to_dataframe()

    print("\nCampaign-Level Performance (Last 3 Days):")
    if not df_campaign_metrics_3day.empty:
        print(df_campaign_metrics_3day.to_string())
        
        # Calculate Overall Portfolio Metrics for Last 3 Days from this DataFrame
        overall_spend_3day = df_campaign_metrics_3day['spend_3day'].sum()
        overall_revenue_3day = df_campaign_metrics_3day['revenue_3day'].sum()
        overall_purchases_3day = df_campaign_metrics_3day['purchases_3day'].sum()
        
        overall_roas_3day = overall_revenue_3day / overall_spend_3day if overall_spend_3day else 0
        overall_cpp_3day = overall_spend_3day / overall_purchases_3day if overall_purchases_3day else 0
        
        print("\n--- Overall Portfolio Performance (Last 3 Days) ---")
        print(f"Total Spend: ${overall_spend_3day:,.2f}")
        print(f"Total Revenue: ${overall_revenue_3day:,.2f}")
        print(f"Total Purchases: {overall_purchases_3day:,.0f}")
        print(f"Overall ROAS: {overall_roas_3day:.2f}")
        print(f"Average CPP: ${overall_cpp_3day:,.2f}")
        
    else:
        print("No campaign data found for the last 3 days.")

except Exception as e:
    print(f"An error occurred while fetching 3-day campaign metrics: {e}")

print("\nNote: The 'Health Score' and detailed 'Reasoning' for each campaign as seen in the sample report are qualitative assessments.")
print("The table above provides quantitative metrics. For a full replication, qualitative analysis would be needed.")

```

### Further Qualitative Analysis (from Sample Report Context)

The following subsections are typically derived from a qualitative analysis of the data presented above, combined with business context and campaign strategy knowledge. In the original sample report (`7D Facebook Ads Report for Inkkas.md`), these included:

*   **Highest and Lowest Performing Campaigns (based on Health Scores/Qualitative Assessment)**
*   **Aggregate Performance Health Analysis (Portfolio Health by Spend Allocation)**
*   **Structural Analysis Observations (Campaign Objectives, Types, Creative Strategies)**
*   **Performance Observations (Detailed CPM/CPL ranges, Funnel Drop-offs - some of which may require more granular data than available in `v1_b2s_all_acquisition_production_report`)**
*   **Biggest Risks Right Now**

To fully replicate the sample report, these sections would involve manual interpretation and summarization based on the data generated by this notebook and specific business goals or targets (e.g., target ROAS of 2.0+).

For now, this notebook focuses on generating the primary quantitative metrics. You can use the output above to inform these qualitative assessments or copy relevant summaries from the source `7D Facebook Ads Report for Inkkas.md` if desired.

## V. Facebook Ad Set Analysis (Last 7 Days)

This section breaks down performance at the ad set level for the last 7 days, providing insights into which ad sets are driving results and their efficiency.

**Note:** The 'Health Score' and detailed qualitative funnel performance for each ad set, as seen in the sample report, would require manual analysis and interpretation. This section focuses on the quantitative metrics available from the data.


```python
# 17. Define SQL for Ad Set-Level Metrics (Last 7 Days)
# Using the 7-day date range defined in the first code cell (your_target_start_date, your_target_end_date)

sql_ad_set_metrics_7day = f"""
SELECT
    adset_name,
    adset_id,
    SUM(spend) AS spend_7day,
    SUM(conversion_value) AS revenue_7day,
    SUM(conversions) AS purchases_7day,
    SUM(impressions) AS impressions_7day,
    SUM(clicks) AS clicks_7day,
    SUM(leads) AS leads_7day,
    (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS roas_7day,
    (SUM(spend) / NULLIF(SUM(conversions), 0)) AS cpp_7day, -- Cost Per Purchase
    (SUM(spend) / NULLIF(SUM(impressions), 0)) * 1000 AS cpm_7day, -- Cost Per Mille (Thousand Impressions)
    (SUM(spend) / NULLIF(SUM(clicks), 0)) AS cpc_7day, -- Cost Per Click
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS ctr_7day -- Click-Through Rate
FROM
    {table_id} # Uses table_id from the first code cell
WHERE
    DATE(date) >= '{your_target_start_date.strftime('%Y-%m-%d')}' AND DATE(date) < '{your_target_end_date.strftime('%Y-%m-%d')}'
    # Add filter for 'active' ad sets if such a column exists at ad set level or can be inferred
    # AND adset_delivery_status = 'ACTIVE' # Example if a delivery status column exists
GROUP BY
    adset_name, adset_id
ORDER BY
    roas_7day DESC
"""

print("\nExecuting 7-Day Ad Set-Level Metrics Query:")
# print(sql_ad_set_metrics_7day) # Optional: print the query

try:
    query_job_ad_sets_7day = client.query(sql_ad_set_metrics_7day)
    df_ad_set_metrics_7day = query_job_ad_sets_7day.to_dataframe()

    print("\nAd Set-Level Performance (Last 7 Days):")
    if not df_ad_set_metrics_7day.empty:
        print(df_ad_set_metrics_7day.to_string())
        
        # Calculate Overall Ad Set Efficiency Metrics (Last 7 Days)
        total_adset_spend_7day = df_ad_set_metrics_7day['spend_7day'].sum()
        total_adset_purchases_7day = df_ad_set_metrics_7day['purchases_7day'].sum()
        total_adset_impressions_7day = df_ad_set_metrics_7day['impressions_7day'].sum()
        total_adset_clicks_7day = df_ad_set_metrics_7day['clicks_7day'].sum()
        
        avg_cpp_7day = total_adset_spend_7day / total_adset_purchases_7day if total_adset_purchases_7day else 0
        avg_cpm_7day = (total_adset_spend_7day / total_adset_impressions_7day) * 1000 if total_adset_impressions_7day else 0
        avg_cpc_7day = total_adset_spend_7day / total_adset_clicks_7day if total_adset_clicks_7day else 0
        avg_ctr_7day = total_adset_clicks_7day / total_adset_impressions_7day if total_adset_impressions_7day else 0
        
        print("\n--- Overall Ad Set Efficiency Metrics (Last 7 Days) ---")
        print(f"Average CPP (Cost Per Purchase): ${avg_cpp_7day:,.2f}")
        print(f"Average CPM (Cost Per Mille): ${avg_cpm_7day:,.2f}")
        print(f"Average CPC (Cost Per Click): ${avg_cpc_7day:,.2f}")
        print(f"Average CTR (Click-Through Rate): {avg_ctr_7day:.2%}")
        
    else:
        print("No ad set data found for the last 7 days.")

except Exception as e:
    print(f"An error occurred while fetching 7-day ad set metrics: {e}")

```

### Ad Set Spend, Reach & Frequency (Last 7 Days)

The table above shows the total spend per ad set over the last 7 days. The sample report also discusses daily budget distribution, which isn't directly available in the `v1_b2s_all_acquisition_production_report` table. 

Below, we'll calculate the reach and average frequency for each ad set over the same 7-day period.


```python
# 18. Define SQL for Ad Set Reach & Frequency (Last 7 Days)
sql_ad_set_reach_frequency_7day = f"""
SELECT
    adset_name,
    adset_id,
    SUM(reach) AS total_reach_7day,
    SUM(impressions) AS total_impressions_7day,
    (SUM(impressions) / NULLIF(SUM(reach), 0)) AS frequency_7day
FROM
    {table_id} # Uses table_id from the first code cell
WHERE
    DATE(date) >= '{your_target_start_date.strftime('%Y-%m-%d')}' AND DATE(date) < '{your_target_end_date.strftime('%Y-%m-%d')}'
GROUP BY
    adset_name, adset_id
ORDER BY
    total_reach_7day DESC
"""

print("\nExecuting 7-Day Ad Set Reach & Frequency Query:")
# print(sql_ad_set_reach_frequency_7day) # Optional: print the query

try:
    query_job_ad_sets_rf_7day = client.query(sql_ad_set_reach_frequency_7day)
    df_ad_set_rf_7day = query_job_ad_sets_rf_7day.to_dataframe()

    print("\nAd Set Reach & Frequency (Last 7 Days):")
    if not df_ad_set_rf_7day.empty:
        print(df_ad_set_rf_7day.to_string())
        
        # Calculate Overall Average Frequency
        overall_impressions_7day = df_ad_set_rf_7day['total_impressions_7day'].sum()
        overall_reach_7day = df_ad_set_rf_7day['total_reach_7day'].sum()
        avg_frequency_7day = overall_impressions_7day / overall_reach_7day if overall_reach_7day else 0
        
        print("\n--- Overall Average Ad Set Frequency (Last 7 Days) ---")
        print(f"Average Frequency: {avg_frequency_7day:.2f}")
    else:
        print("No ad set reach/frequency data found for the last 7 days.")

except Exception as e:
    print(f"An error occurred while fetching 7-day ad set reach & frequency: {e}")

print("\nNote: The sample report also discusses engagement patterns (video content, user journey metrics) and audience interest analysis, which often require more granular event data or qualitative interpretation beyond what this query provides.")

```

### Ad Set Engagement, Audience Interest, and Health Scores (Qualitative Analysis)

The sample report (`7D Facebook Ads Report for Inkkas.md`) further details ad set performance through:

*   **Engagement Patterns:** This involves analyzing metrics like video views (e.g., video plays, 25% video views) and user journey metrics (e.g., view content to add-to-cart rates, add-to-cart to initiate checkout rates, initiate checkout to purchase rates). These often require more granular event tracking data than what is available in `v1_b2s_all_acquisition_production_report`.
*   **Audience Interest Analysis:** This is a qualitative assessment based on which product-specific ad sets resonate best with audiences, often inferred from comparing engagement and conversion metrics across different ad set themes.
*   **Health Score Breakdown:** Similar to campaign health scores, this section in the sample report provides a qualitative health score (e.g., 88/100) and reasoning for individual ad sets based on a holistic view of their performance, positive indicators, and areas for improvement.

Generating these sections programmatically with high fidelity would require either more detailed data sources (e.g., tables with specific funnel event counts per ad set) or a sophisticated model for qualitative assessment based on the available quantitative metrics and predefined business rules/targets.

For now, this notebook focuses on presenting the core quantitative ad set metrics. The data generated above can be used as a basis for these manual qualitative assessments or for copying relevant summaries from the source `7D Facebook Ads Report for Inkkas.md` if desired.

# VI. Facebook Ads Performance Executive Summary (Last 7 Days)

This section provides a high-level executive summary of Facebook Ads performance over the last 7 days, drawing from the detailed analyses in previous sections and incorporating insights similar to the sample report.

## A. OVERVIEW: Last 7 Days Performance


```python
# 19. Display 7-Day Performance Overview from df_overall_summary
print("\n--- OVERVIEW: Last 7 Days Performance ---")

if 'df_overall_summary' in locals() and not df_overall_summary.empty:
    overall_roas_7d = df_overall_summary['overall_roas'].iloc[0]
    total_spend_7d = df_overall_summary['total_spend'].iloc[0]
    total_revenue_7d = df_overall_summary['total_revenue'].iloc[0]
    total_purchases_7d = df_overall_summary['total_purchases'].iloc[0]
    total_leads_7d = df_overall_summary['total_leads'].iloc[0]
    overall_cpl_7d = df_overall_summary['overall_cpl'].iloc[0]
    
    print(f"Overall ROAS (Return on Ad Spend): {overall_roas_7d:.2f}")
    print(f"Total Ad Spend: ${total_spend_7d:,.2f}")
    print(f"Total Revenue (from conversions): ${total_revenue_7d:,.2f}")
    print(f"Total Purchases: {total_purchases_7d:,.0f}")
    print(f"Total Leads: {total_leads_7d:,.0f}")
    print(f"Average Cost Per Lead (CPL): ${overall_cpl_7d:,.2f}")
    
    # Note: The sample report mentions a "Top ROAS: 16.33 (Coronet Western Boot)". 
    # This is a specific ad-level or granular product-level metric which we haven't specifically queried for the top single ROAS ad.
    # The df_campaign_highlights shows top campaigns by ROAS.
    if 'df_campaign_highlights' in locals() and not df_campaign_highlights.empty:
        top_campaign_roas = df_campaign_highlights['campaign_roas'].iloc[0] # Assuming it's sorted DESC
        top_campaign_name = df_campaign_highlights['campaign_name'].iloc[0]
        print(f"Top Campaign ROAS: {top_campaign_roas:.2f} (from campaign: {top_campaign_name})")
    else:
        print("Top campaign ROAS data not available (df_campaign_highlights missing or empty).")
else:
    print("Overall summary data (df_overall_summary) not available. Please run the first code cell.")

```

## B. TOP PERFORMING AD CREATIVE FORMATS (Qualitative Insights)

The sample report includes an analysis of top-performing ad creative formats, broken down into:

*   **Product Format Analysis:** (e.g., "Boots & Outdoor Styles consistently outperform other categories with 32% higher ROAS", "Western Boots show the highest engagement")
*   **Creative Format Analysis:** (e.g., "UGC-style videos showing product in action drive 43% higher CTR than static images", "Lifestyle imagery with nature backdrops outperforms studio shots by 28%")

**Data Requirements for Programmatic Replication:**

Automating this type of analysis would typically require:
1.  **Structured Tags/Labels:** Additional metadata fields in your data source that explicitly tag each ad or campaign with its `product_format` (e.g., "Boots", "Sandals", "Accessory") and `creative_format` (e.g., "UGC Video", "Static Image - Studio", "Static Image - Lifestyle", "Carousel").
2.  **Granular Ad-Level Data:** Access to performance metrics at the individual ad creative level if not already using it.
3.  **Comparative Analysis Logic:** Code to group by these tags, calculate average performance for each, and then compare them to derive insights like "X outperforms Y by Z%".

Without such structured tags and potentially more granular ad-level data easily queryable for these specific attributes, this analysis remains largely qualitative, drawing conclusions by observing trends in campaign/ad names and their associated performance.

The quantitative data generated in the previous sections (e.g., campaign performance, inferred product category performance) can serve as a starting point for manually deriving these kinds_of insights.

## C. TOP PERFORMING CAMPAIGNS (Last 7 Days)


```python
# 20. Display Top Performing Campaigns from df_campaign_highlights
print("\n--- TOP PERFORMING CAMPAIGNS (Last 7 Days) ---")

if 'df_campaign_highlights' in locals() and not df_campaign_highlights.empty:
    # Displaying top 3 campaigns as an example, similar to the sample report structure
    # The sample report also includes Campaign IDs, which are in df_campaign_highlights
    top_n_campaigns = min(3, len(df_campaign_highlights)) # Show up to top 3 or fewer if less data
    
    for i in range(top_n_campaigns):
        campaign = df_campaign_highlights.iloc[i]
        print(f"\n### {i+1}. {campaign['campaign_name']} (ID: {campaign['campaign_id']})")
        print(f"*   ROAS: {campaign['campaign_roas']:.2f}")
        print(f"*   Spend: ${campaign['campaign_spend']:,.2f}")
        print(f"*   Purchases: {campaign['campaign_purchases']:,.0f}")
        print(f"*   CPP: ${campaign['campaign_cpp']:,.2f}")
        print(f"*   CTR: {campaign['campaign_ctr']:.2%}")
        print("*   Key Performers (Ad/Product Level): [Requires ad-level data query or manual input based on deeper analysis]")
        print("*   Insight: [Qualitative insight to be added manually based on campaign specifics]")
        
    if top_n_campaigns == 0:
        print("No campaign highlight data available to display top performers.")
        
else:
    print("Campaign highlights data (df_campaign_highlights) not available. Please run the relevant earlier code cell.")

print("\nNote: The 'Key Performers' (specific ads/products within these campaigns) and qualitative 'Insight' for each campaign, as seen in the sample report, require more granular (ad-level) data analysis and/or manual interpretation. The details above are campaign-level aggregates.")

```

## D. Further Executive Summary Insights (Qualitative)

The remainder of the Executive Summary in the sample report (`7D Facebook Ads Report for Inkkas.md`) delves into highly specific qualitative insights and data points that typically require deep dives into ad-level creative performance, specific messaging tests, audience segmentation beyond basic demographics, and potentially data from analytics platforms outside of the ads manager (e.g., for conversion path analysis).

These sections include:

*   **Audience & Messaging Insights:** (e.g., "Sustainability: Tree planting messaging increases CTR by 26%", "Handcrafted/Premium: Quality messaging drives 18% higher conversion rates", specific effective ad copy phrases).
*   **Frequency & Delivery Insights:** (e.g., "Optimal frequency sits between 1.3-1.7", "Performance drops significantly above 2.0 frequency", "Mobile placements outperforming desktop by 37%"). While overall frequency can be calculated (as done in the Ad Set section), optimal ranges and platform-specific delivery insights often require more detailed breakdown or A/B test data.
*   **Creative Performance Drivers:** (e.g., detailed descriptions of top video and static image performers, highlighting specific features and messaging within those ads).
*   **Optimization Opportunities:** (e.g., "Creatives: Focus on authentic UGC showcasing actual usage", "Budget: Shift budgets toward Western Boots and Sandals"). These are strategic recommendations based on the full analysis.
*   **Ad Performance Analysis / Conversion Path Insights:** (e.g., detailed ad-level ROAS for specific product creatives, analysis of time to purchase, common purchase sequences). This often involves linking ad interaction data with website analytics.

**Replicating these programmatically would require:**

*   Access to ad-creative level performance data with associated tags for creative type, messaging themes, product shown, etc.
*   Data on audience segments beyond what's in the primary tables.
*   Integration with website analytics for conversion path analysis.
*   A framework for A/B test analysis if specific comparative claims (e.g., "X increases CTR by Y%") are to be validated.

This notebook provides the foundational quantitative metrics. These detailed qualitative insights would typically be layered on top through manual analysis by marketing specialists, creative teams, and data analysts looking at the broader context and specific tests run.

# VII. Actionable Scaling Plan (Strategic Output)

The final section of the `7D Facebook Ads Report for Inkkas.md` sample report is a **"7-Day Actionable Scaling Plan for Inkkas."**

This plan typically includes day-by-day recommendations for:
*   Budget reallocation (pausing underperformers, scaling winners).
*   Creative deep dives and refreshes.
*   Audience and funnel optimization checks.
*   Performance reviews and next steps.

Developing such a plan is a strategic exercise that synthesizes all the quantitative data and qualitative insights gathered in the preceding sections of the report. It requires an understanding of business goals, risk tolerance, testing capacity, and market dynamics.

This notebook aims to provide the foundational data analysis. The actionable plan would be a subsequent step, typically crafted by marketing strategists or account managers using the insights generated herein.
