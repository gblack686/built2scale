from google.cloud import bigquery
from google.oauth2 import service_account
from tabulate import tabulate
import csv
import os
from datetime import datetime, timedelta
import pandas as pd # For displaying results as a DataFrame

# Load credentials from the service account file
credentials = service_account.Credentials.from_service_account_file(
    'built2scale-2c7cc11e1ca6.json')

# Project and dataset information
project_id = 'built2scale'
dataset_id = 'b2sreporting'

# Initialize the BigQuery client
client = bigquery.Client(credentials=credentials, project=project_id)

# List of tables to analyze
tables = [
    'b2s_meta_acquisition_demo_breakdown_by_date_report',
    'b2s_meta_acquisition_tech_breakdown_by_date_report',
    'client_offer_compare_table',
    'client_offer_monitor_table',
    'media_buyers_table',
    'v1_b2s_all_acquisition_production_report'
]

# --- Connection Setup (as in your script) ---
try:
    credentials = service_account.Credentials.from_service_account_file(
        'built2scale-2c7cc11e1ca6.json') # Ensure this path is correct
    project_id = 'built2scale'
    # dataset_id = 'b2sreporting' # Already in the fully qualified table name
    client = bigquery.Client(credentials=credentials, project=project_id)
    print("BigQuery client initialized successfully.")
except Exception as e:
    print(f"Error initializing BigQuery client: {e}")
    # exit() # It's better to let the script continue or handle more gracefully in a notebook/interactive env
# --- End Connection Setup ---

# Placeholder for your new exploratory query
exploratory_query = """
SELECT column_name, data_type
FROM `built2scale.b2sreporting`.INFORMATION_SCHEMA.COLUMNS
WHERE table_name = 'v1_b2s_all_acquisition_production_report'
ORDER BY column_name;
"""

print("\nExecuting the exploratory SQL query to list columns from v1_b2s_all_acquisition_production_report...")

try:
    query_job = client.query(exploratory_query)
    results_df = query_job.to_dataframe()

    if not results_df.empty:
        print("\nQuery Results:")
        print(results_df.to_string())
    else:
        print("The query returned no results.")

except Exception as e:
    print(f"An error occurred while executing the query: {e}")

if __name__ == "__main__":
    # You can add any specific logic to run here if needed,
    # or just let the query execution above be the main action.
    print("\nScript execution finished.")

# The previous main function and its calls are removed.
# The first_sql_query and its execution logic are removed.
# All function definitions (get_table_schema, get_min_max_dates, etc.) are removed.

# --- SQL Queries for Detailed Client Statistics ---
# Note: Replace 'YOUR_CLIENT_NAME' with the actual client name before running these queries.

query_client_daily_performance = """
SELECT
    report_date,
    client_name,
    client_offer,
    ad_network,
    total_spend,
    total_impressions,
    total_clicks,
    total_reach,
    total_purchases,
    total_leads,
    total_registrations,
    total_conversion_value,
    roas,
    cpc,
    cpm,
    ctr,
    cpa_purchase,
    cpa_lead,
    cpa_registration,
    frequency,
    active_campaigns_count,
    active_adsets_count,
    active_ads_count,
    last_updated
FROM
    b2sreporting.wsc_client_daily_performance_summary  -- Updated view name
WHERE
    client_name = 'Organnix';
"""

query_client_campaign_periodic_summary = """
SELECT
    client_name,
    client_offer,
    campaign_id,
    period_type,
    period_start_date,
    period_end_date,
    campaign_name,
    ad_network,
    campaign_status,
    total_spend,
    total_impressions,
    total_clicks,
    total_reach,
    total_purchases,
    total_leads,
    total_registrations,
    total_conversion_value,
    roas,
    cpc,
    cpm,
    ctr,
    cpa_purchase,
    cpa_lead,
    cpa_registration,
    frequency,
    last_updated
FROM
    b2sreporting.wsc_client_campaign_periodic_summary  -- Updated view name
WHERE
    client_name = 'Organnix';
"""

query_client_adset_periodic_summary = """
SELECT
    client_name,
    client_offer,
    campaign_id,
    adset_id,
    period_type,
    period_start_date,
    period_end_date,
    campaign_name,
    adset_name,
    ad_network,
    adset_status,
    total_spend,
    total_impressions,
    total_clicks,
    total_reach,
    total_purchases,
    total_leads,
    total_registrations,
    total_conversion_value,
    roas,
    cpc,
    cpm,
    ctr,
    cpa_purchase,
    cpa_lead,
    cpa_registration,
    frequency,
    last_updated
FROM
    b2sreporting.client_adset_periodic_summary  -- Replace with your actual table name if different
WHERE
    client_name = 'Organnix';
"""

query_client_ad_periodic_summary = """
SELECT
    client_name,
    client_offer,
    campaign_id,
    adset_id,
    ad_id,
    period_type,
    period_start_date,
    period_end_date,
    campaign_name,
    adset_name,
    ad_name,
    ad_network,
    ad_status,
    total_spend,
    total_impressions,
    total_clicks,
    total_reach,
    total_purchases,
    total_leads,
    total_registrations,
    total_conversion_value,
    roas,
    cpc,
    cpm,
    ctr,
    cpa_purchase,
    cpa_lead,
    cpa_registration,
    frequency,
    last_updated
FROM
    b2sreporting.client_ad_periodic_summary  -- Replace with your actual table name if different
WHERE
    client_name = 'Organnix';
"""

query_client_overall_snapshot = """
SELECT
    client_name,
    client_offer,
    period_type,
    period_start_date,
    period_end_date,
    ad_network,
    total_spend,
    total_impressions,
    total_clicks,
    total_reach,
    total_purchases,
    total_leads,
    total_registrations,
    total_conversion_value,
    roas,
    cpc,
    cpm,
    ctr,
    cpa_purchase,
    cpa_lead,
    cpa_registration,
    frequency,
    number_of_active_campaigns,
    number_of_active_adsets,
    number_of_active_ads,
    top_roas_campaign_name,
    top_roas_campaign_value,
    lowest_cpl_campaign_name,
    lowest_cpl_campaign_value,
    highest_ctr_campaign_name,
    highest_ctr_campaign_value,
    last_updated
FROM
    b2sreporting.client_overall_snapshot  -- Replace with your actual table name if different
WHERE
    client_name = 'Organnix';
"""

# Example of how you might print or use one of the queries:
# print("\n--- SQL Query for Daily Performance ---")
# print(query_client_daily_performance)

# If you want to execute these, you would do something like:
client_to_query = "Organnix" # Define the client name

print(f"--- Executing queries for client: {client_to_query} ---")

# Query 1: Client Daily Performance
formatted_query_daily = query_client_daily_performance.replace('YOUR_CLIENT_NAME', client_to_query)
try:
    print(f"\nExecuting Daily Performance query for {client_to_query}...")
    query_job_daily = client.query(formatted_query_daily)
    results_df_daily = query_job_daily.to_dataframe()
    if not results_df_daily.empty:
        print(f"\nResults for {client_to_query} (Daily Performance):")
        print(results_df_daily.to_string())
    else:
        print(f"The Daily Performance query for {client_to_query} returned no results.")
except Exception as e:
    print(f"An error occurred during Daily Performance query: {e}")

# Query 2: Client Campaign Periodic Summary
formatted_query_campaign_periodic = query_client_campaign_periodic_summary.replace('YOUR_CLIENT_NAME', client_to_query)
try:
    print(f"\nExecuting Campaign Periodic Summary query for {client_to_query}...")
    query_job_campaign_periodic = client.query(formatted_query_campaign_periodic)
    results_df_campaign_periodic = query_job_campaign_periodic.to_dataframe()
    if not results_df_campaign_periodic.empty:
        print(f"\nResults for {client_to_query} (Campaign Periodic Summary):")
        print(results_df_campaign_periodic.to_string())
    else:
        print(f"The Campaign Periodic Summary query for {client_to_query} returned no results.")
except Exception as e:
    print(f"An error occurred during Campaign Periodic Summary query: {e}")

# Query 3: Client Adset Periodic Summary
formatted_query_adset_periodic = query_client_adset_periodic_summary.replace('YOUR_CLIENT_NAME', client_to_query)
try:
    print(f"\nExecuting Adset Periodic Summary query for {client_to_query}...")
    query_job_adset_periodic = client.query(formatted_query_adset_periodic)
    results_df_adset_periodic = query_job_adset_periodic.to_dataframe()
    if not results_df_adset_periodic.empty:
        print(f"\nResults for {client_to_query} (Adset Periodic Summary):")
        print(results_df_adset_periodic.to_string())
    else:
        print(f"The Adset Periodic Summary query for {client_to_query} returned no results.")
except Exception as e:
    print(f"An error occurred during Adset Periodic Summary query: {e}")

# Query 4: Client Ad Periodic Summary
formatted_query_ad_periodic = query_client_ad_periodic_summary.replace('YOUR_CLIENT_NAME', client_to_query)
try:
    print(f"\nExecuting Ad Periodic Summary query for {client_to_query}...")
    query_job_ad_periodic = client.query(formatted_query_ad_periodic)
    results_df_ad_periodic = query_job_ad_periodic.to_dataframe()
    if not results_df_ad_periodic.empty:
        print(f"\nResults for {client_to_query} (Ad Periodic Summary):")
        print(results_df_ad_periodic.to_string())
    else:
        print(f"The Ad Periodic Summary query for {client_to_query} returned no results.")
except Exception as e:
    print(f"An error occurred during Ad Periodic Summary query: {e}")

# Query 5: Client Overall Snapshot
formatted_query_overall_snapshot = query_client_overall_snapshot.replace('YOUR_CLIENT_NAME', client_to_query)
try:
    print(f"\nExecuting Overall Snapshot query for {client_to_query}...")
    query_job_overall_snapshot = client.query(formatted_query_overall_snapshot)
    results_df_overall_snapshot = query_job_overall_snapshot.to_dataframe()
    if not results_df_overall_snapshot.empty:
        print(f"\nResults for {client_to_query} (Overall Snapshot):")
        print(results_df_overall_snapshot.to_string())
    else:
        print(f"The Overall Snapshot query for {client_to_query} returned no results.")
except Exception as e:
    print(f"An error occurred during Overall Snapshot query: {e}")

print("\nClient statistics SQL queries have been added to the script.") 