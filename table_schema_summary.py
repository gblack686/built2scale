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

def get_table_schema(table_name):
    """Retrieve schema information for a given table."""
    table_ref = f"{project_id}.{dataset_id}.{table_name}"
    table = client.get_table(table_ref)
    
    schema_info = []
    for field in table.schema:
        schema_info.append({
            'Table': table_name,
            'Column Name': field.name,
            'Data Type': field.field_type,
            'Mode': field.mode,
            'Description': field.description or 'No description available'
        })
    
    return schema_info, table

def get_min_max_dates(table_name, date_field):
    """Retrieve the minimum and maximum dates from a given table and date field."""
    if not date_field:
        return None, None
    
    query = f"""
    SELECT MIN({date_field}) as min_date, MAX({date_field}) as max_date
    FROM `{project_id}.{dataset_id}.{table_name}`
    """
    try:
        query_job = client.query(query)
        results = list(query_job)
        if results and results[0]:
            return results[0]['min_date'], results[0]['max_date']
    except Exception as e:
        print(f"Error querying min/max dates from {table_name}: {str(e)}")
    return None, None

def get_date_field(schema_info):
    """Determine the date field in the table schema."""
    date_fields = []
    
    for field in schema_info:
        field_name = field['Column Name'].lower()
        field_type = field['Data Type'].lower()
        
        # Look for common date field names and appropriate data types
        if (field_name == 'date' or 'date' in field_name) and (field_type == 'date' or field_type == 'timestamp'):
            date_fields.append(field['Column Name'])
        elif (field_name == 'time' or field_name == 'timestamp' or 'created' in field_name) and (field_type == 'date' or field_type == 'timestamp'):
            date_fields.append(field['Column Name'])
    
    # Return the first date field found, or None if none found
    return date_fields[0] if date_fields else None

def get_recent_records(table_name, schema_info, days=7, limit=10):
    """Retrieve records from the past N days from a given table."""
    date_field = get_date_field(schema_info)
    
    # Calculate the date threshold (N days ago from today)
    date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    if date_field:
        query = f"""
        SELECT * 
        FROM `{project_id}.{dataset_id}.{table_name}` 
        WHERE {date_field} >= '{date_threshold}'
        LIMIT {limit}
        """
        
        # Count query for getting total number of recent records
        count_query = f"""
        SELECT COUNT(*) as count
        FROM `{project_id}.{dataset_id}.{table_name}` 
        WHERE {date_field} >= '{date_threshold}'
        """
    else:
        # If no date field is found, just get the most recent records by whatever order
        query = f"""
        SELECT * 
        FROM `{project_id}.{dataset_id}.{table_name}` 
        LIMIT {limit}
        """
        
        # Total records query without date filter
        count_query = f"""
        SELECT COUNT(*) as count
        FROM `{project_id}.{dataset_id}.{table_name}` 
        """
    
    try:
        # Execute the query
        query_job = client.query(query)
        records = query_job.to_dataframe()
        
        # Execute the count query
        count_job = client.query(count_query)
        count_result = list(count_job)[0]
        record_count = count_result['count']
        
        return records, record_count, date_field
    except Exception as e:
        print(f"Error querying recent records from {table_name}: {str(e)}")
        return None, 0, date_field

def print_table_info(table_name, export_data=None, show_recent_records=False):
    """Print formatted schema information for a table and optionally show recent records."""
    print(f"\n{'=' * 80}")
    print(f"TABLE: {table_name}")
    print(f"{'=' * 80}")
    
    try:
        schema_info, table = get_table_schema(table_name)
        print(tabulate(schema_info, headers="keys", tablefmt="grid"))
        
        # Additional table metadata
        print(f"\nTotal rows: {table.num_rows}")
        print(f"Last modified: {table.modified}")
        print(f"Created: {table.created}")
        
        # Get and print Min/Max dates
        date_field_for_min_max = get_date_field(schema_info)
        if date_field_for_min_max:
            min_date, max_date = get_min_max_dates(table_name, date_field_for_min_max)
            if min_date is not None and max_date is not None:
                print(f"Date Range ({date_field_for_min_max}): {min_date} to {max_date}")
            else:
                print(f"Could not retrieve date range for field: {date_field_for_min_max}")
        else:
            print("No suitable date field found to determine date range.")
        
        # Add data to export list if needed
        if export_data is not None:
            export_data.extend(schema_info)
        
        # Display recent records if requested
        if show_recent_records:
            records, record_count, date_field = get_recent_records(table_name, schema_info)
            
            if records is not None and not records.empty:
                print(f"\nRECENT RECORDS (Last 7 days{' filtered by ' + date_field if date_field else ''}):")
                print(f"Found {record_count} records in the last 7 days")
                print("\nSample of recent records:")
                
                # Format the DataFrame for display
                # Limit the number of columns if there are too many
                if len(records.columns) > 8:
                    display_cols = list(records.columns)[:8]
                    print(tabulate(records[display_cols].head(5), headers="keys", tablefmt="grid"))
                    print("(Note: Only showing first 8 columns due to space constraints)")
                else:
                    print(tabulate(records.head(5), headers="keys", tablefmt="grid"))
            else:
                print("\nNo recent records found or error retrieving records")
            
    except Exception as e:
        print(f"Error retrieving schema for {table_name}: {str(e)}")

def export_to_csv(data, filename=None):
    """Export schema data to CSV file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"schema_summary_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                print(f"\nSchema summary exported to {os.path.abspath(filename)}")
            else:
                print("\nNo data to export")
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")

def export_recent_records_to_csv(table_name, days=7):
    """Export recent records from a specific table to CSV."""
    try:
        schema_info, _ = get_table_schema(table_name)
        records, record_count, date_field = get_recent_records(table_name, schema_info, days=days, limit=1000)
        
        if records is not None and not records.empty:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{table_name}_recent_records_{timestamp}.csv"
            
            records.to_csv(filename, index=False)
            print(f"Exported {len(records)} recent records to {os.path.abspath(filename)}")
        else:
            print(f"No recent records found for {table_name} or error retrieving records")
    except Exception as e:
        print(f"Error exporting records for {table_name}: {str(e)}")

def main(export_csv=True, show_recent_records=True, export_records=False):
    """Main function to retrieve and display schema and recent records for all tables."""
    print(f"SCHEMA SUMMARY AND RECENT RECORDS FOR TABLES IN {project_id}.{dataset_id}")
    
    export_data = [] if export_csv else None
    
    for table in tables:
        print_table_info(table, export_data, show_recent_records)
        
        if export_records:
            export_recent_records_to_csv(table)
    
    if export_csv and export_data:
        export_to_csv(export_data)
    
    print("\nSchema summary and recent records check completed.")

if __name__ == "__main__":
    main(export_csv=True, show_recent_records=True, export_records=False) # Set export_records=True to export all recent records 

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
    exit()
# --- End Connection Setup ---

first_sql_query = """
SELECT
    SUM(spend) AS total_spend,
    SUM(impressions) AS total_impressions,
    SUM(clicks) AS total_clicks,
    SUM(conversions) AS total_conversions,
    SUM(IFNULL(conversion_value, 0)) AS total_conversion_value,
    SUM(IFNULL(leads, 0)) AS total_leads
FROM
    `built2scale.b2sreporting.v1_b2s_all_acquisition_production_report`
WHERE
    DATE(date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
    AND DATE(date) < CURRENT_DATE()
"""

print("\nExecuting the first SQL query for Overall Performance Snapshot (Last 7 Days)...")

try:
    query_job = client.query(first_sql_query)
    results_df = query_job.to_dataframe()

    if not results_df.empty:
        print("\nQuery Results:")
        print(results_df.to_string())

        # You can then calculate derived metrics in Python:
        total_spend = results_df['total_spend'].iloc[0]
        total_impressions = results_df['total_impressions'].iloc[0]
        total_clicks = results_df['total_clicks'].iloc[0]
        total_conversions = results_df['total_conversions'].iloc[0]
        total_conversion_value = results_df['total_conversion_value'].iloc[0]
        total_leads = results_df['total_leads'].iloc[0]

        ctr = (total_clicks / total_impressions) * 100 if total_impressions else 0
        cpc = total_spend / total_clicks if total_clicks else 0
        cpa = total_spend / total_conversions if total_conversions else 0
        roas = total_conversion_value / total_spend if total_spend else 0
        cpl = total_spend / total_leads if total_leads else 0
        
        print("\nCalculated Metrics (Last 7 Days):")
        print(f"Average CTR: {ctr:.2f}%")
        print(f"Average CPC: ${cpc:.2f}")
        print(f"Average CPA: ${cpa:.2f}")
        print(f"Overall ROAS: {roas:.2f}")
        print(f"Average CPL: ${cpl:.2f}")

    else:
        print("The query returned no results.")

except Exception as e:
    print(f"An error occurred while executing the query: {e}") 