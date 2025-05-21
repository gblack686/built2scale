from google.cloud import bigquery
from google.oauth2 import service_account

# Replace 'path/to/your/service-account-file.json' with the actual path to your JSON key file.
# Ensure this file is kept secure and not checked into version control.
credentials = service_account.Credentials.from_service_account_file(
    'built2scale-2c7cc11e1ca6.json')

# Replace 'your-bigquery-project-id-here' with your Google Cloud project ID.
project_id = 'built2scale'

# Initialize the BigQuery client
client = bigquery.Client(credentials=credentials, project=project_id)

# Define your SQL query
# Example: Query public dataset for USA names in Texas
QUERY = """
    SELECT
  client_name,
  COUNT(*) AS total_campaigns,
  SUM(spend) AS total_spend,
  AVG(spend) AS average_spend,
  MAX(spend) AS max_spend,
  MIN(spend) AS min_spend
FROM
  `built2scale`.`b2sreporting`.`v1_b2s_all_acquisition_production_report`
GROUP BY
  client_name;
"""

# Execute the query
query_job = client.query(QUERY)  # API request
print("Starting query job...")

# Wait for the job to complete and get the results
rows = query_job.result()  # Waits for query to finish
print("Query finished.")

# Print the results
print("Query results:")
for row in rows:
    print(f'{row.client_name} - {row.total_campaigns} - {row.total_spend} - {row.average_spend} - {row.max_spend} - {row.min_spend}')

print("Script finished.")
