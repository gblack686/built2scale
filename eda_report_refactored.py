# %% [markdown]
# # Facebook Ads Report Analysis (Refactored)
# This notebook connects to BigQuery to analyze Facebook Ads performance data and helps recreate the insights from the '7D Facebook Ads Report for Inkkas.md'.
# This version is refactored to use a separate module for SQL query generation.

# %%
# 1. Import necessary libraries
from google.cloud import bigquery
from google.oauth2 import service_account # Added for service account
import pandas as pd
from datetime import date, timedelta
# import os # Not strictly needed if passing credentials directly to client
import notebooks.bq_queries as bq_queries # Import the new query module

# 2. Configure your BigQuery client using Service Account
# Path to your service account key file
credentials_path = "C:/Users/gblac/OneDrive/Desktop/WeScaleCreators/BuiltToScale/built2scale-2c7cc11e1ca6.json"

# Load credentials from the service account file
try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    project_id = credentials.project_id # Get project_id from credentials
    print(f"Successfully loaded credentials for project: {project_id}")
except Exception as e:
    print(f"Error loading service account credentials from {credentials_path}: {e}")
    print("Please ensure the path is correct and the file is valid JSON.")
    credentials = None
    project_id = "built2scale" # Fallback

dataset_id = "b2sreporting" # Dataset ID

if credentials:
    client = bigquery.Client(project=project_id, credentials=credentials)
    print(f"Connected to BigQuery project: {client.project} using service account.")
else:
    print("Attempting to connect to BigQuery with default credentials or expecting an error.")
    client = bigquery.Client(project=project_id)

# 3. Define your target end date for the 7-day report
your_target_end_date = date.today()
your_target_start_date = your_target_end_date - timedelta(days=7)

# Date formatting for queries
start_date_str_7day = your_target_start_date.strftime('%Y-%m-%d')
end_date_str_7day = your_target_end_date.strftime('%Y-%m-%d')

print(f"Reporting period (7-day): {start_date_str_7day} to {your_target_end_date - timedelta(days=1)}")

# 4. Define the primary table for analysis
table_name = "v1_b2s_all_acquisition_production_report"
table_id = f"`{project_id}.{dataset_id}.{table_name}`"
print(f"Using table: {table_id}")

# 5. Get SQL query for Overall 7-Day Summary Metrics from bq_queries module
sql_overall_summary = bq_queries.get_overall_summary_sql(table_id, start_date_str_7day, end_date_str_7day)

print("\nExecuting Overall Summary Query:")
# print(sql_overall_summary) # Optional: print the query

# 6. Execute the query and load results into a pandas DataFrame
try:
    if client.project:
        query_job_overall = client.query(sql_overall_summary)
        df_overall_summary = query_job_overall.to_dataframe()

        # 7. Display the results
        print("\nOverall 7-Day Performance Summary:")
        if len(df_overall_summary) == 1:
            print(df_overall_summary.T.to_string())
        else:
            print(df_overall_summary.to_string())
    else:
        print("BigQuery client not fully initialized. Query not executed.")
except Exception as e:
    print(f"An error occurred: {e}")

# %% [markdown]
# ## I. Executive Facebook Campaign Summary (Continued)
# ### Campaign Performance Highlights

# %%
# 8. Get SQL for Campaign Performance Highlights (7-Day) from bq_queries module
sql_campaign_highlights = bq_queries.get_campaign_highlights_sql(table_id, start_date_str_7day, end_date_str_7day)

print("\nExecuting Campaign Performance Highlights Query:")
# print(sql_campaign_highlights) # Optional: print the query

# 9. Execute the query and load into a pandas DataFrame
try:
    if client.project:
        query_job_campaigns = client.query(sql_campaign_highlights)
        df_campaign_highlights = query_job_campaigns.to_dataframe()

        # 10. Display the results
        print("\nTop Campaign Performance Highlights (Last 7 Days):")
        print(df_campaign_highlights.to_string())
    else:
        print("BigQuery client not fully initialized. Query not executed.")
except Exception as e:
    print(f"An error occurred while fetching campaign highlights: {e}")

# %% [markdown]
# ## II. Audience Engagement & Lead Generation Summary

# %%
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
    print("\nOverall summary data (df_overall_summary) not available.")

# 12. Get SQL for Campaign with Highest CTR (7-Day) from bq_queries module
sql_highest_ctr_campaign = bq_queries.get_highest_ctr_campaign_sql(table_id, start_date_str_7day, end_date_str_7day)

print("\nExecuting Query for Campaign with Highest CTR:")
try:
    if client.project:
        query_job_highest_ctr = client.query(sql_highest_ctr_campaign)
        df_highest_ctr = query_job_highest_ctr.to_dataframe()
        print("\nCampaign with Highest CTR (Last 7 Days):")
        if not df_highest_ctr.empty:
            print(f"- Campaign: {df_highest_ctr['campaign_name'].iloc[0]}")
            print(f"- CTR: {df_highest_ctr['campaign_ctr'].iloc[0]:.2%}")
        else:
            print("No campaign data found for highest CTR.")
    else:
        print("BigQuery client not fully initialized. Query not executed.")
except Exception as e:
    print(f"An error occurred while fetching the highest CTR campaign: {e}")

# 13. Get SQL for Campaign with Most Efficient (Lowest) CPL (7-Day) from bq_queries module
sql_lowest_cpl_campaign = bq_queries.get_lowest_cpl_campaign_sql(table_id, start_date_str_7day, end_date_str_7day)

print("\nExecuting Query for Campaign with Lowest CPL:")
try:
    if client.project:
        query_job_lowest_cpl = client.query(sql_lowest_cpl_campaign)
        df_lowest_cpl = query_job_lowest_cpl.to_dataframe()
        print("\nCampaign with Most Efficient (Lowest) CPL (Last 7 Days):")
        if not df_lowest_cpl.empty:
            print(f"- Campaign: {df_lowest_cpl['campaign_name'].iloc[0]}")
            print(f"- CPL: ${df_lowest_cpl['campaign_cpl'].iloc[0]:,.2f}")
        else:
            print("No campaign data found for lowest CPL.")
    else:
        print("BigQuery client not fully initialized. Query not executed.")
except Exception as e:
    print(f"An error occurred while fetching the lowest CPL campaign: {e}")

print("\nReminder: Specific metrics like detailed video views and landing page views are not directly available from the current table.")

# %% [markdown]
# ## III. Product Category Performance (Inferred)

# %%
# 14. Analyze Performance by Inferred Product Categories
print("\n--- Product Category Performance (Inferred, Last 7 Days) ---")

def get_category_performance_data(category_name, like_conditions):
    # Get SQL from bq_queries module
    query = bq_queries.get_category_performance_sql(table_id, category_name, like_conditions, start_date_str_7day, end_date_str_7day)
    try:
        if client.project:
            query_job = client.query(query)
            df_category = query_job.to_dataframe()
            return df_category
        else:
            print(f"BigQuery client not fully initialized. Query for {category_name} not executed.")
            return pd.DataFrame()
    except Exception as e:
        print(f"An error occurred while querying for {category_name}: {e}")
        return pd.DataFrame()

categories_to_analyze = {
    "Footwear (Boots, Slip Ons)": ["%boot%", "%slip on%", "%slip-on%"],
    "Clearance Campaigns": ["%clearance%"],
    "DPA Campaigns": ["%dpa%"],
    "UGC Testing Campaigns": ["%ugc test%", "%ugc%"]
}

all_category_dfs = []
for cat_name, keywords in categories_to_analyze.items():
    print(f"\nFetching data for: {cat_name}")
    df_cat = get_category_performance_data(cat_name, keywords)
    if not df_cat.empty and pd.notna(df_cat['total_spend'].iloc[0]) and df_cat['total_spend'].iloc[0] > 0:
        print(df_cat.to_string(index=False))
        all_category_dfs.append(df_cat)
    elif not df_cat.empty and (pd.isna(df_cat['total_spend'].iloc[0]) or df_cat['total_spend'].iloc[0] == 0):
        print(f"No significant spend or data found for {cat_name}.")
    else:
        print(f"No data returned for {cat_name} or an error occurred.")

if all_category_dfs:
    df_inferred_categories_summary = pd.concat(all_category_dfs, ignore_index=True)
    print("\nSummary Table for Inferred Categories (where data was found):")
    print(df_inferred_categories_summary.to_string(index=False))
else:
    print("\nNo data found for any of the inferred categories.")

# %% [markdown]
# ## IV. Facebook Campaign Performance Overview (Last 3 Days)

# %%
# 15. Define date range for 3-Day analysis
three_day_target_end_date = date.today()
three_day_target_start_date = three_day_target_end_date - timedelta(days=3)

start_date_str_3day = three_day_target_start_date.strftime('%Y-%m-%d')
end_date_str_3day = three_day_target_end_date.strftime('%Y-%m-%d')

print(f"Reporting period for 3-Day analysis: {start_date_str_3day} to {three_day_target_end_date - timedelta(days=1)}")

# 16. Get SQL for Campaign-Level Metrics (Last 3 Days) from bq_queries module
sql_campaign_metrics_3day = bq_queries.get_campaign_metrics_3day_sql(table_id, start_date_str_3day, end_date_str_3day)

print("\nExecuting 3-Day Campaign-Level Metrics Query:")
try:
    if client.project:
        query_job_campaigns_3day = client.query(sql_campaign_metrics_3day)
        df_campaign_metrics_3day = query_job_campaigns_3day.to_dataframe()
        print("\nCampaign-Level Performance (Last 3 Days):")
        if not df_campaign_metrics_3day.empty:
            print(df_campaign_metrics_3day.to_string())
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
    else:
        print("BigQuery client not fully initialized. Query not executed.")
except Exception as e:
    print(f"An error occurred while fetching 3-day campaign metrics: {e}")

# %% [markdown]
# ## V. Facebook Ad Set Analysis (Last 7 Days)

# %%
# 17. Get SQL for Ad Set-Level Metrics (Last 7 Days) from bq_queries module
sql_ad_set_metrics_7day = bq_queries.get_ad_set_metrics_7day_sql(table_id, start_date_str_7day, end_date_str_7day)

print("\nExecuting 7-Day Ad Set-Level Metrics Query:")
try:
    if client.project:
        query_job_ad_sets_7day = client.query(sql_ad_set_metrics_7day)
        df_ad_set_metrics_7day = query_job_ad_sets_7day.to_dataframe()
        print("\nAd Set-Level Performance (Last 7 Days):")
        if not df_ad_set_metrics_7day.empty:
            print(df_ad_set_metrics_7day.to_string())
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
    else:
        print("BigQuery client not fully initialized. Query not executed.")
except Exception as e:
    print(f"An error occurred while fetching 7-day ad set metrics: {e}")

# %% [markdown]
# ### Ad Set Spend, Reach & Frequency (Last 7 Days)

# %%
# 18. Get SQL for Ad Set Reach & Frequency (Last 7 Days) from bq_queries module
sql_ad_set_reach_frequency_7day = bq_queries.get_ad_set_reach_frequency_7day_sql(table_id, start_date_str_7day, end_date_str_7day)

print("\nExecuting 7-Day Ad Set Reach & Frequency Query:")
try:
    if client.project:
        query_job_ad_sets_rf_7day = client.query(sql_ad_set_reach_frequency_7day)
        df_ad_set_rf_7day = query_job_ad_sets_rf_7day.to_dataframe()
        print("\nAd Set Reach & Frequency (Last 7 Days):")
        if not df_ad_set_rf_7day.empty:
            print(df_ad_set_rf_7day.to_string())
            overall_impressions_7day_rf = df_ad_set_rf_7day['total_impressions_7day'].sum() # Renamed to avoid conflict
            overall_reach_7day_rf = df_ad_set_rf_7day['total_reach_7day'].sum() # Renamed to avoid conflict
            avg_frequency_7day = overall_impressions_7day_rf / overall_reach_7day_rf if overall_reach_7day_rf else 0
            print("\n--- Overall Average Ad Set Frequency (Last 7 Days) ---")
            print(f"Average Frequency: {avg_frequency_7day:.2f}")
        else:
            print("No ad set reach/frequency data found for the last 7 days.")
    else:
        print("BigQuery client not fully initialized. Query not executed.")
except Exception as e:
    print(f"An error occurred while fetching 7-day ad set reach & frequency: {e}")

# %% [markdown]
# # VI. Facebook Ads Performance Executive Summary (Last 7 Days)

# %% [markdown]
# ## A. OVERVIEW: Last 7 Days Performance

# %%
# 19. Display 7-Day Performance Overview
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
    
    if 'df_campaign_highlights' in locals() and not df_campaign_highlights.empty:
        top_campaign_roas = df_campaign_highlights['campaign_roas'].iloc[0]
        top_campaign_name = df_campaign_highlights['campaign_name'].iloc[0]
        print(f"Top Campaign ROAS: {top_campaign_roas:.2f} (from campaign: {top_campaign_name})")
    else:
        print("Top campaign ROAS data not available.")
else:
    print("Overall summary data not available.")

# %% [markdown]
# ## C. TOP PERFORMING CAMPAIGNS (Last 7 Days)

# %%
# 20. Display Top Performing Campaigns
print("\n--- TOP PERFORMING CAMPAIGNS (Last 7 Days) ---")
if 'df_campaign_highlights' in locals() and not df_campaign_highlights.empty:
    top_n_campaigns = min(3, len(df_campaign_highlights))
    for i in range(top_n_campaigns):
        campaign = df_campaign_highlights.iloc[i]
        print(f"\n### {i+1}. {campaign['campaign_name']} (ID: {campaign['campaign_id']})")
        print(f"*   ROAS: {campaign['campaign_roas']:.2f}")
        print(f"*   Spend: ${campaign['campaign_spend']:,.2f}")
        print(f"*   Purchases: {campaign['campaign_purchases']:,.0f}")
        print(f"*   CPP: ${campaign['campaign_cpp']:,.2f}")
        print(f"*   CTR: {campaign['campaign_ctr']:.2%}")
    if top_n_campaigns == 0:
        print("No campaign highlight data available.")
else:
    print("Campaign highlights data not available.")

# %% [markdown]
# # End of Refactored Report Script
# The qualitative sections and actionable plans from the original notebook are omitted for brevity 
# but would follow the same pattern of analysis based on the data generated above. 