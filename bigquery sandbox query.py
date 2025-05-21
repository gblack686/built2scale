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