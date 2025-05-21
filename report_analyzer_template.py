import os
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai

# --- CONFIGURATION ---
# BigQuery Configuration
SERVICE_ACCOUNT_FILE_PATH = "path/to/your/service_account.json"  # Replace with your service account key file path
# project_id will be inferred from service account by default, or you can set it explicitly.
# BIGQUERY_PROJECT_ID = "your-gcp-project-id"
# BIGQUERY_DATASET_ID = "your-dataset-id" # Only if your query doesn't fully qualify tables

# Gemini API Configuration
# IMPORTANT: Store your API key securely. Using an environment variable is recommended.
# Create a .env file in the same directory with: GEMINI_API_KEY="YOUR_API_KEY"
# or set it as an environment variable in your system.
# from dotenv import load_dotenv # Uncomment if using python-dotenv
# load_dotenv() # Uncomment if using python-dotenv
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Fallback: Replace with your key if not using env var

# --- BIGQUERY FUNCTIONS ---

def initialize_bigquery_client(credentials_path):
    """Initializes and returns a BigQuery client using service account credentials."""
    try:
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        project_id = credentials.project_id
        client = bigquery.Client(project=project_id, credentials=credentials)
        print(f"Successfully connected to BigQuery project: {project_id}")
        return client
    except Exception as e:
        print(f"Error initializing BigQuery client from {credentials_path}: {e}")
        return None

def execute_sql_query(client, sql_query):
    """Executes the given SQL query using the BigQuery client and returns a pandas DataFrame."""
    if not client:
        print("BigQuery client not initialized. Cannot execute query.")
        return None
    try:
        print(f"\nExecuting SQL Query:\n{sql_query}")
        query_job = client.query(sql_query)  # Make an API request.
        df_results = query_job.to_dataframe()  # Waits for the job to complete.
        print("\nQuery executed successfully. Results:")
        print(df_results.head())
        return df_results
    except Exception as e:
        print(f"An error occurred while executing the BigQuery query: {e}")
        return None

# --- GEMINI API FUNCTIONS ---

def initialize_gemini_model(api_key):
    """Initializes and returns a Gemini generative model."""
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        print("Gemini API key not configured. Please set GEMINI_API_KEY environment variable or update the script.")
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro') # Or choose a specific model like 'gemini-1.5-flash' etc.
        print("Gemini API model initialized successfully.")
        return model
    except Exception as e:
        print(f"Error initializing Gemini model: {e}")
        return None

def get_qualitative_analysis_from_gemini(model, data_df, custom_prompt_instructions=""):
    """
    Sends data to Gemini for qualitative analysis.
    data_df: pandas DataFrame containing the data from the SQL query.
    custom_prompt_instructions: Optional string with specific instructions for Gemini.
    """
    if not model:
        print("Gemini model not initialized. Cannot get analysis.")
        return None
    if data_df is None or data_df.empty:
        print("No data to analyze.")
        return None

    # Convert DataFrame to a string format suitable for the prompt (e.g., CSV or JSON string)
    # Using to_markdown() for a readable format, but JSON or a more compact string might be better for large data.
    data_string = data_df.to_markdown(index=False)

    # You can also use JSON:
    # data_string = data_df.to_json(orient='records', indent=2)

    prompt = f"""
Please provide a qualitative analysis of the following dataset.
The data represents [DESCRIBE THE CONTEXT OF YOUR DATA HERE - e.g., 'Facebook ad campaign performance over the last 7 days'].

Dataset:
```
{data_string}
```

Based on this data, please provide insights on:
- Key trends or patterns observed.
- Notable positive performance aspects.
- Areas of concern or potential underperformance.
- Any surprising findings.
- Potential contributing factors to the observed performance (if inferable).
{custom_prompt_instructions}

Provide the analysis in a clear, concise, and actionable manner.
Focus on qualitative interpretation rather than just restating the numbers.
"""

    print("\nSending request to Gemini API...")
    try:
        response = model.generate_content(prompt)
        analysis = response.text
        print("\n--- Gemini Qualitative Analysis ---")
        print(analysis)
        return analysis
    except Exception as e:
        print(f"An error occurred while communicating with the Gemini API: {e}")
        return None

# --- MAIN EXECUTION ---

def main():
    # 1. Initialize BigQuery Client
    bq_client = initialize_bigquery_client(SERVICE_ACCOUNT_FILE_PATH)
    if not bq_client:
        return

    # 2. Define Your SQL Query
    # Example: Overall 7-Day Summary Metrics (modify as needed)
    # Ensure your table names are fully qualified if BIGQUERY_DATASET_ID is not used
    # e.g., `your-gcp-project-id.your-dataset-id.your-table-name`

    # ---- REPLACE THE SQL QUERY BELOW WITH YOUR DESIRED QUERY ----
    your_target_end_date_str = pd.Timestamp('today').strftime('%Y-%m-%d')
    your_target_start_date_str = (pd.Timestamp('today') - pd.Timedelta(days=7)).strftime('%Y-%m-%d')

    # If you have a default project and dataset ID set in the client or environment,
    # you might not need to fully qualify table names. Otherwise, do so.
    # This example assumes the table_id includes project and dataset.
    # If your query is for a specific table like 'v1_b2s_all_acquisition_production_report'
    # in a dataset like 'b2sreporting', construct table_id accordingly.
    # For example:
    # project = bq_client.project
    # dataset = "b2sreporting" # Replace with your actual dataset
    # table_name_for_query = "v1_b2s_all_acquisition_production_report" # Replace
    # fully_qualified_table_id = f"`{project}.{dataset}.{table_name_for_query}`"

    # Placeholder for a generic table if you haven't set up specific ones yet
    fully_qualified_table_id = "`your_project.your_dataset.your_table`" # !!! REPLACE THIS !!!

    sql_query = f"""
    SELECT
        campaign_name,
        SUM(spend) AS total_spend,
        SUM(conversions) AS total_conversions,
        (SUM(conversions) / NULLIF(SUM(spend), 0)) AS conversion_rate_per_dollar_spent, -- Example metric
        (SUM(spend) / NULLIF(SUM(conversions), 0)) AS cost_per_conversion
    FROM
        {fully_qualified_table_id}
    WHERE
        -- DATE(date_column) >= '{your_target_start_date_str}' AND DATE(date_column) < '{your_target_end_date_str}' -- Modify date_column
        1=1 -- Remove this if WHERE clause is used
    GROUP BY
        campaign_name
    ORDER BY
        total_spend DESC
    LIMIT 10;
    """
    # ---- END OF SQL QUERY REPLACEMENT SECTION ----

    # 3. Execute SQL Query
    results_df = execute_sql_query(bq_client, sql_query)
    if results_df is None or results_df.empty:
        print("No data returned from BigQuery. Exiting.")
        return

    # 4. Initialize Gemini Model
    gemini_model = initialize_gemini_model(GEMINI_API_KEY)
    if not gemini_model:
        return

    # 5. Get Qualitative Analysis from Gemini
    # Optionally, add custom instructions for the Gemini prompt
    custom_instructions = "Highlight any campaigns that seem to be outliers in terms of cost per conversion."

    # Remember to update the description in the prompt inside get_qualitative_analysis_from_gemini
    # to match the context of YOUR SQL query.
    get_qualitative_analysis_from_gemini(gemini_model, results_df, custom_prompt_instructions=custom_instructions)

if __name__ == "__main__":
    # To use python-dotenv for loading GEMINI_API_KEY from a .env file:
    # 1. pip install python-dotenv
    # 2. Create a .env file in the same directory as this script:
    #    GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
    # 3. Uncomment the dotenv lines in the CONFIGURATION section and below (if needed).
    # from dotenv import load_dotenv
    # load_dotenv()
    main() 