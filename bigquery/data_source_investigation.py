from google.cloud import bigquery
from google.oauth2 import service_account
from tabulate import tabulate
import re

# Load credentials from the service account file
credentials = service_account.Credentials.from_service_account_file(
    'built2scale-2c7cc11e1ca6.json')

# Project information
project_id = 'built2scale'

# Initialize the BigQuery client
client = bigquery.Client(credentials=credentials, project=project_id)

# Data sources to investigate
data_sources = {
    'Meta Ads': ['meta', 'facebook', 'fb', 'instagram', 'ig'],
    'Google Ads': ['google ads', 'adwords', 'google_ads', 'googleads'],
    'TikTok Ads': ['tiktok', 'tik_tok', 'tik tok'],
    'Shopify': ['shopify', 'shop'],
    'Google Analytics': ['google analytics', 'ga', 'analytics', 'ga4'],
    'Triple Whale': ['triple whale', 'triplewhale', 'triple_whale'],
    'Hyros': ['hyros'],
    'Attribution Data': ['attribution', 'attr']
}

def list_datasets():
    """List all datasets in the project."""
    datasets = list(client.list_datasets())
    
    if not datasets:
        print("No datasets found in project:", project_id)
        return []
    
    print(f"Datasets in project {project_id}:")
    dataset_ids = []
    for dataset in datasets:
        print(f"- {dataset.dataset_id}")
        dataset_ids.append(dataset.dataset_id)
    
    return dataset_ids

def list_tables_in_dataset(dataset_id):
    """List all tables in a dataset."""
    tables = list(client.list_tables(dataset_id))
    
    if not tables:
        print(f"No tables found in dataset: {dataset_id}")
        return []
    
    print(f"\nTables in dataset {dataset_id}:")
    table_ids = []
    for table in tables:
        print(f"- {table.table_id}")
        table_ids.append(table.table_id)
    
    return table_ids

def search_for_data_sources(dataset_id, table_ids):
    """Search for tables that might contain data from the specified sources."""
    results = {source: [] for source in data_sources}
    
    for table_id in table_ids:
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        
        # Check if the table name matches any of the data source keywords
        for source, keywords in data_sources.items():
            for keyword in keywords:
                if re.search(keyword, table_id.lower()):
                    if table_id not in results[source]:
                        results[source].append(table_id)
    
    return results

def get_table_schema_sample(dataset_id, table_id):
    """Get schema and a sample of data from the table."""
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    table = client.get_table(table_ref)
    
    # Get schema
    schema_info = []
    for field in table.schema:
        schema_info.append({
            'Column Name': field.name,
            'Data Type': field.field_type,
            'Mode': field.mode
        })
    
    # Get sample data
    query = f"SELECT * FROM `{table_ref}` LIMIT 5"
    sample_data = client.query(query).result()
    
    return schema_info, sample_data

def check_column_evidence(dataset_id, table_id):
    """Check if table columns suggest it contains data from specific sources."""
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    table = client.get_table(table_ref)
    
    evidence = {source: False for source in data_sources}
    
    # Define column patterns that suggest specific data sources
    column_patterns = {
        'Meta Ads': ['campaign_id', 'adset', 'facebook', 'fb_', 'instagram', 'meta'],
        'Google Ads': ['google_ads', 'adwords', 'campaign_id', 'ad_group'],
        'TikTok Ads': ['tiktok', 'tik_tok'],
        'Shopify': ['order_id', 'product_id', 'shopify'],
        'Google Analytics': ['session', 'pageview', 'ga_', 'google_analytics'],
        'Triple Whale': ['triple_whale', 'triplewhale'],
        'Hyros': ['hyros'],
        'Attribution Data': ['attribution', 'source_medium', 'conversion_path']
    }
    
    # Check column names against patterns
    for field in table.schema:
        field_name = field.name.lower()
        for source, patterns in column_patterns.items():
            for pattern in patterns:
                if pattern.lower() in field_name:
                    evidence[source] = True
    
    return evidence

def main():
    """Main function to investigate data sources."""
    print("INVESTIGATING DATA SOURCES IN BIGQUERY")
    print("=" * 50)
    
    # Step 1: List all datasets
    dataset_ids = list_datasets()
    
    # Step 2: Investigate each dataset
    all_results = {}
    
    for dataset_id in dataset_ids:
        # Get all tables in the dataset
        table_ids = list_tables_in_dataset(dataset_id)
        
        # Search for data sources based on table names
        name_results = search_for_data_sources(dataset_id, table_ids)
        
        # Initialize the results structure for this dataset
        all_results[dataset_id] = {source: [] for source in data_sources}
        
        # For each potential match, check column evidence
        for source, tables in name_results.items():
            for table_id in tables:
                evidence = check_column_evidence(dataset_id, table_id)
                
                # If we have evidence or the table name clearly indicates the source
                if evidence[source]:
                    all_results[dataset_id][source].append({
                        'table_id': table_id,
                        'confidence': 'High (column evidence)'
                    })
                else:
                    all_results[dataset_id][source].append({
                        'table_id': table_id,
                        'confidence': 'Medium (name match)'
                    })
        
        # Check all other tables for column evidence
        for table_id in table_ids:
            already_matched = any(table_id in [t['table_id'] for t in tables] for tables in all_results[dataset_id].values())
            
            if not already_matched:
                evidence = check_column_evidence(dataset_id, table_id)
                for source, has_evidence in evidence.items():
                    if has_evidence:
                        all_results[dataset_id][source].append({
                            'table_id': table_id,
                            'confidence': 'Medium (column evidence)'
                        })
    
    # Step 3: Print summary of findings
    print("\nDATA SOURCE INVESTIGATION SUMMARY")
    print("=" * 50)
    
    for source in data_sources:
        print(f"\n{source}:")
        found = False
        
        for dataset_id, results in all_results.items():
            if results[source]:
                found = True
                print(f"  In dataset '{dataset_id}':")
                for match in results[source]:
                    print(f"    - {match['table_id']} (Confidence: {match['confidence']})")
        
        if not found:
            print("  No evidence found in any dataset")
    
    # Step 4: Display detailed schema for high-confidence matches
    print("\nDETAILED SCHEMA FOR HIGH-CONFIDENCE MATCHES")
    print("=" * 50)
    
    for dataset_id, results in all_results.items():
        for source, matches in results.items():
            for match in matches:
                if 'High' in match['confidence']:
                    print(f"\nTable: {dataset_id}.{match['table_id']}")
                    print(f"Data Source: {source}")
                    print("-" * 40)
                    
                    schema_info, _ = get_table_schema_sample(dataset_id, match['table_id'])
                    print(tabulate(schema_info, headers="keys", tablefmt="grid"))

if __name__ == "__main__":
    main() 