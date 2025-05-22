# %% [markdown]
# # Facebook Ads Report Analysis (Refactored)
# This notebook connects to BigQuery to analyze Facebook Ads performance data and helps recreate the insights from the '7D Facebook Ads Report for Inkkas.md'.
# This version is refactored to use a separate module for SQL query generation and outputs to HTML.

# %%
# 1. Import necessary libraries
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import date, timedelta
import bq_queries as bq_queries

# Function to append to HTML content
html_content = ""
client_to_filter = "Organixx" # Define the client to filter by
monitor_table_name = "client_offer_monitor_table" # Define the monitor table name

def initialize_html_header(client_name, offer_details, ad_network="Facebook/Meta"):
    global html_content
    html_content = "<html><head><title>Facebook Ads Report</title>"
    html_content += "<style> body { font-family: sans-serif; margin: 20px; } "
    html_content += "table { border-collapse: collapse; margin-bottom: 20px; } "
    html_content += "th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; } "
    html_content += "th { background-color: #f2f2f2; } "
    html_content += "h1, h2, h3, h4 { color: #333; } .summary-box { border: 1px solid #eee; padding: 15px; margin-bottom: 20px; background-color: #f9f9f9; } "
    html_content += ".summary-box p { margin: 5px 0; } .summary-box ul { list-style-type: none; padding-left: 0; } .summary-box li { margin-bottom: 10px; padding: 10px; border: 1px solid #e0e0e0; background-color: #fff; } </style></head><body>"
    html_content += f"<h1>Facebook Ads Performance Report for {client_name}</h1>"
    html_content += "<div class='summary-box'>"
    html_content += "<h2>Report Quick Summary by Client Offer</h2>"
    html_content += f"<p><strong>Ad Network:</strong> {ad_network}</p>"
    if offer_details:
        html_content += "<ul>"
        for offer_summary in offer_details:
            html_content += "<li>"
            html_content += f"<strong>Offer:</strong> {offer_summary['offer_name']}<br>"
            html_content += f"<strong>Ongoing Campaigns (Last 7 Days):</strong> {offer_summary['campaign_count']}<br>"
            html_content += f"<strong>Active Ad Sets (Last 7 Days):</strong> {offer_summary['ad_set_count']}"
            html_content += "</li>"
        html_content += "</ul>"
    else:
        html_content += "<p>No specific offer details found for this client in the reporting period.</p>"
    html_content += "</div>"

def print_and_accumulate_html(text, is_header=False, level=2, is_table=False, df=None):
    global html_content
    print(text)
    if is_table and df is not None:
        html_content += df.to_html(index=False, escape=False)
    elif is_header:
        html_content += f"<h{level}>{text}</h{level}>\n"
    else:
        # Replace newlines with <br> for non-table, non-header text to preserve formatting
        html_content += f"<p>{text.replace('\n', '<br>')}</p>\n"

# 2. Configure your BigQuery client using Service Account
credentials_path = "C:/Users/gblac/OneDrive/Desktop/WeScaleCreators/BuiltToScale/built2scale-2c7cc11e1ca6.json"
project_id = "built2scale" # Fallback
dataset_id = "b2sreporting"

try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    project_id = credentials.project_id
    print_and_accumulate_html(f"Successfully loaded credentials for project: {project_id}")
    client = bigquery.Client(project=project_id, credentials=credentials)
    print_and_accumulate_html(f"Connected to BigQuery project: {client.project} using service account.")
except Exception as e:
    print_and_accumulate_html(f"Error loading service account credentials from {credentials_path}: {e}")
    print_and_accumulate_html("Please ensure the path is correct and the file is valid JSON.")
    print_and_accumulate_html("Attempting to connect to BigQuery with default credentials or expecting an error.")
    client = bigquery.Client(project=project_id) # This will likely use ADC or fail
    # Exit if client is not initialized, as further operations will fail
    if not client.project:
        print_and_accumulate_html("BigQuery client failed to initialize. Exiting script.")
        html_content += "</body></html>"
        with open("facebook_ads_report.html", "w", encoding='utf-8') as f:
            f.write(html_content)
        exit()

# 3. Define your target end date for the 7-day report
your_target_end_date = date.today()
your_target_start_date = your_target_end_date - timedelta(days=7)
start_date_str_7day = your_target_start_date.strftime('%Y-%m-%d')
end_date_str_7day = your_target_end_date.strftime('%Y-%m-%d')
print_and_accumulate_html(f"Reporting period (7-day): {start_date_str_7day} to {your_target_end_date - timedelta(days=1)}", is_header=True, level=2)

# 4. Define the primary table for analysis
table_name = "v1_b2s_all_acquisition_production_report"
table_id = f"`{project_id}.{dataset_id}.{table_name}`"
monitor_table_id = f"`{project_id}.{dataset_id}.{monitor_table_name}`"
print_and_accumulate_html(f"Using primary data table: {table_id}")
print_and_accumulate_html(f"Using client offer monitor table: {monitor_table_id}")

# Fetch client offers for the specified client
offer_details_for_header = []
sql_client_offers = bq_queries.get_client_offers_sql(monitor_table_id, client_to_filter)
try:
    query_job_client_offers = client.query(sql_client_offers)
    df_client_offers = query_job_client_offers.to_dataframe()
    if not df_client_offers.empty:
        print_and_accumulate_html(f"Found {len(df_client_offers)} offers for client: {client_to_filter}")
        for index, row in df_client_offers.iterrows():
            current_offer = row['client_offer']
            campaign_count_for_offer = 0
            ad_set_count_for_offer = 0
            
            # Get campaign count for this offer
            sql_camp_count_offer = bq_queries.get_campaign_count_for_offer_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter, current_offer)
            try:
                df_camp_count = client.query(sql_camp_count_offer).to_dataframe()
                if not df_camp_count.empty and 'campaign_count' in df_camp_count.columns:
                    campaign_count_for_offer = df_camp_count['campaign_count'].iloc[0]
            except Exception as e_camp:
                print_and_accumulate_html(f"Error fetching campaign count for offer {current_offer}: {e_camp}")

            # Get ad set count for this offer
            sql_adset_count_offer = bq_queries.get_ad_set_count_for_offer_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter, current_offer)
            try:
                df_adset_count = client.query(sql_adset_count_offer).to_dataframe()
                if not df_adset_count.empty and 'ad_set_count' in df_adset_count.columns:
                    ad_set_count_for_offer = df_adset_count['ad_set_count'].iloc[0]
            except Exception as e_adset:
                print_and_accumulate_html(f"Error fetching ad set count for offer {current_offer}: {e_adset}")

            offer_details_for_header.append({
                "offer_name": current_offer,
                "campaign_count": campaign_count_for_offer,
                "ad_set_count": ad_set_count_for_offer
            })
    else:
        print_and_accumulate_html(f"No offers found for client {client_to_filter} in the monitor table.")
except Exception as e:
    print_and_accumulate_html(f"An error occurred fetching client offers: {e}")

# Initialize HTML Header with dynamic counts per offer
initialize_html_header(client_to_filter, offer_details_for_header)

# 5. Overall 7-Day Summary Metrics (This remains for the client as a whole)
print_and_accumulate_html(f"Overall 7-Day Performance Summary for {client_to_filter} (All Offers Combined)", is_header=True, level=3)
sql_overall_summary = bq_queries.get_overall_summary_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
# active_campaign_count = 0 # This was for the old header, not strictly needed now unless used elsewhere
# active_ad_set_count = 0   # This was for the old header

try:
    query_job_overall = client.query(sql_overall_summary)
    df_overall_summary = query_job_overall.to_dataframe()
    if not df_overall_summary.empty:
        # active_campaign_count = df_overall_summary['number_of_active_campaigns'].iloc[0] if 'number_of_active_campaigns' in df_overall_summary.columns else 0
        df_display_overall_summary = df_overall_summary.T if len(df_overall_summary) == 1 else df_overall_summary
        if len(df_overall_summary) == 1: # If transposed
            df_display_overall_summary.columns = ['Value'] # Rename the single column header
        print_and_accumulate_html("Overall Summary Data (Full Table for Client - All Offers):", is_table=True, df=df_display_overall_summary)
    else:
        print_and_accumulate_html("No overall summary data returned for counts.")
except Exception as e:
    print_and_accumulate_html(f"An error occurred fetching overall summary for counts: {e}")
    df_overall_summary = pd.DataFrame() # Ensure df_overall_summary exists for later parts

# Get Active Ad Set Count - Old overall count, not strictly needed for header now
# sql_ad_set_count = bq_queries.get_active_ad_set_count_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
# try:
#     query_job_ad_set_count = client.query(sql_ad_set_count)
#     df_ad_set_count = query_job_ad_set_count.to_dataframe()
#     if not df_ad_set_count.empty and 'active_ad_set_count' in df_ad_set_count.columns:
#         active_ad_set_count = df_ad_set_count['active_ad_set_count'].iloc[0]
#     else:
#         print_and_accumulate_html("No ad set count data returned.")
# except Exception as e:
#     print_and_accumulate_html(f"An error occurred fetching ad set count: {e}")

# Initialize HTML Header with dynamic counts
# initialize_html_header(client_to_filter, active_campaign_count, active_ad_set_count) # Old call, replaced by offer-specific header

# Now print the original overall summary table if data exists
# if not df_overall_summary.empty:
#     print_and_accumulate_html("Overall Summary Data (Full Table):", is_table=True, df=df_overall_summary.T if len(df_overall_summary) == 1 else df_overall_summary)
# else:
#     print_and_accumulate_html("No overall summary data table to display.")

# %% [markdown]
# ## I. Executive Facebook Campaign Summary (Continued)
# ### Campaign Performance Highlights
print_and_accumulate_html(f"Campaign Performance Highlights (Last 7 Days) for {client_to_filter}", is_header=True, level=3)
sql_campaign_highlights = bq_queries.get_campaign_highlights_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
try:
    query_job_campaigns = client.query(sql_campaign_highlights)
    df_campaign_highlights = query_job_campaigns.to_dataframe()
    if not df_campaign_highlights.empty:
        print_and_accumulate_html("Top Campaign Performance:", is_table=True, df=df_campaign_highlights)
    else:
        print_and_accumulate_html("No campaign highlight data returned.")
except Exception as e:
    print_and_accumulate_html(f"An error occurred fetching campaign highlights: {e}")
    df_campaign_highlights = pd.DataFrame() # Ensure df_campaign_highlights exists

# %% [markdown]
# ## II. Audience Engagement & Lead Generation Summary
print_and_accumulate_html(f"Audience Engagement & Lead Generation Summary (Last 7 Days) for {client_to_filter}", is_header=True, level=3)
if not df_overall_summary.empty:
    total_clicks = df_overall_summary['total_clicks'].iloc[0]
    overall_ctr = df_overall_summary['overall_ctr'].iloc[0]
    total_leads = df_overall_summary['total_leads'].iloc[0]
    overall_cpl = df_overall_summary['overall_cpl'].iloc[0]
    print_and_accumulate_html(f"Total Clicks: {total_clicks:,.0f}\nOverall Average CTR: {overall_ctr:.2%}\nTotal Leads Captured: {total_leads:,.0f}\nOverall Average Cost Per Lead (CPL): ${overall_cpl:,.2f}")
else:
    print_and_accumulate_html("Overall summary data not available for audience engagement.")

# Highest CTR Campaign
sql_highest_ctr_campaign = bq_queries.get_highest_ctr_campaign_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
try:
    query_job_highest_ctr = client.query(sql_highest_ctr_campaign)
    df_highest_ctr = query_job_highest_ctr.to_dataframe()
    print_and_accumulate_html("Campaign with Highest CTR:", is_header=True, level=4)
    if not df_highest_ctr.empty:
        print_and_accumulate_html(f"- Campaign: {df_highest_ctr['campaign_name'].iloc[0]}\n- CTR: {df_highest_ctr['campaign_ctr'].iloc[0]:.2%}")
    else:
        print_and_accumulate_html("No campaign data found for highest CTR.")
except Exception as e:
    print_and_accumulate_html(f"An error occurred fetching highest CTR campaign: {e}")

# Lowest CPL Campaign
sql_lowest_cpl_campaign = bq_queries.get_lowest_cpl_campaign_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
try:
    query_job_lowest_cpl = client.query(sql_lowest_cpl_campaign)
    df_lowest_cpl = query_job_lowest_cpl.to_dataframe()
    print_and_accumulate_html("Campaign with Most Efficient (Lowest) CPL:", is_header=True, level=4)
    if not df_lowest_cpl.empty:
        print_and_accumulate_html(f"- Campaign: {df_lowest_cpl['campaign_name'].iloc[0]}\n- CPL: ${df_lowest_cpl['campaign_cpl'].iloc[0]:,.2f}")
    else:
        print_and_accumulate_html("No campaign data found for lowest CPL.")
except Exception as e:
    print_and_accumulate_html(f"An error occurred fetching lowest CPL campaign: {e}")

# %% [markdown]
# ## III. Product Category Performance (Inferred)
print_and_accumulate_html(f"Product Category Performance (Inferred, Last 7 Days) for {client_to_filter}", is_header=True, level=3)
def get_category_performance_data(category_name, like_conditions):
    query = bq_queries.get_category_performance_sql(table_id, category_name, like_conditions, start_date_str_7day, end_date_str_7day, client_to_filter)
    try:
        query_job = client.query(query)
        df_category = query_job.to_dataframe()
        return df_category
    except Exception as e:
        print_and_accumulate_html(f"An error occurred while querying for {category_name}: {e}")
        return pd.DataFrame()

categories_to_analyze = {
    "Footwear (Boots, Slip Ons)": ["%boot%", "%slip on%", "%slip-on%"],
    "Clearance Campaigns": ["%clearance%"],
    "DPA Campaigns": ["%dpa%"],
    "UGC Testing Campaigns": ["%ugc test%", "%ugc%"]
}
all_category_dfs = []
for cat_name, keywords in categories_to_analyze.items():
    print_and_accumulate_html(f"Fetching data for: {cat_name}", is_header=True, level=4)
    df_cat = get_category_performance_data(cat_name, keywords)
    if not df_cat.empty and pd.notna(df_cat['total_spend'].iloc[0]) and df_cat['total_spend'].iloc[0] > 0:
        print_and_accumulate_html(f"{cat_name} Performance:", is_table=True, df=df_cat)
        all_category_dfs.append(df_cat)
    elif not df_cat.empty and (pd.isna(df_cat['total_spend'].iloc[0]) or df_cat['total_spend'].iloc[0] == 0):
        print_and_accumulate_html(f"No significant spend or data found for {cat_name}.")
    else:
        print_and_accumulate_html(f"No data returned for {cat_name} or an error occurred.")

if all_category_dfs:
    df_inferred_categories_summary = pd.concat(all_category_dfs, ignore_index=True)
    print_and_accumulate_html("Summary Table for Inferred Categories:", is_header=True, level=4)
    print_and_accumulate_html("Summary of Inferred Categories:", is_table=True, df=df_inferred_categories_summary)
else:
    print_and_accumulate_html("No data found for any of the inferred categories.")

# %% [markdown]
# ## IV. Facebook Campaign Performance Overview (Last 3 Days)
three_day_target_end_date = date.today()
three_day_target_start_date = three_day_target_end_date - timedelta(days=3)
start_date_str_3day = three_day_target_start_date.strftime('%Y-%m-%d')
end_date_str_3day = three_day_target_end_date.strftime('%Y-%m-%d')
print_and_accumulate_html(f"Facebook Campaign Performance Overview (Last 3 Days: {start_date_str_3day} to {three_day_target_end_date - timedelta(days=1)}) for {client_to_filter}", is_header=True, level=3)

sql_campaign_metrics_3day = bq_queries.get_campaign_metrics_3day_sql(table_id, start_date_str_3day, end_date_str_3day, client_to_filter)
try:
    query_job_campaigns_3day = client.query(sql_campaign_metrics_3day)
    df_campaign_metrics_3day = query_job_campaigns_3day.to_dataframe()
    if not df_campaign_metrics_3day.empty:
        print_and_accumulate_html("Campaign-Level Performance (Last 3 Days):", is_table=True, df=df_campaign_metrics_3day)
        overall_spend_3day = df_campaign_metrics_3day['spend_3day'].sum()
        overall_revenue_3day = df_campaign_metrics_3day['revenue_3day'].sum()
        overall_purchases_3day = df_campaign_metrics_3day['purchases_3day'].sum()
        overall_roas_3day = overall_revenue_3day / overall_spend_3day if overall_spend_3day else 0
        overall_cpp_3day = overall_spend_3day / overall_purchases_3day if overall_purchases_3day else 0
        print_and_accumulate_html("Overall Portfolio Performance (Last 3 Days):", is_header=True, level=4)
        summary_3day_text = (
            f"Total Spend: ${overall_spend_3day:,.2f}\n"
            f"Total Revenue: ${overall_revenue_3day:,.2f}\n"
            f"Total Purchases: {overall_purchases_3day:,.0f}\n"
            f"Overall ROAS: {overall_roas_3day:.2f}\n"
            f"Average CPP: ${overall_cpp_3day:,.2f}"
        )
        print_and_accumulate_html(summary_3day_text)
    else:
        print_and_accumulate_html("No campaign data found for the last 3 days.")
except Exception as e:
    print_and_accumulate_html(f"An error occurred fetching 3-day campaign metrics: {e}")

# %% [markdown]
# ## V. Facebook Ad Set Analysis (Last 7 Days)
print_and_accumulate_html(f"Facebook Ad Set Analysis (Last 7 Days) for {client_to_filter}", is_header=True, level=3)
sql_ad_set_metrics_7day = bq_queries.get_ad_set_metrics_7day_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
try:
    query_job_ad_sets_7day = client.query(sql_ad_set_metrics_7day)
    df_ad_set_metrics_7day = query_job_ad_sets_7day.to_dataframe()
    if not df_ad_set_metrics_7day.empty:
        print_and_accumulate_html("Ad Set-Level Performance (Last 7 Days):", is_table=True, df=df_ad_set_metrics_7day)
        total_adset_spend_7day = df_ad_set_metrics_7day['spend_7day'].sum()
        total_adset_purchases_7day = df_ad_set_metrics_7day['purchases_7day'].sum()
        total_adset_impressions_7day = df_ad_set_metrics_7day['impressions_7day'].sum()
        total_adset_clicks_7day = df_ad_set_metrics_7day['clicks_7day'].sum()
        avg_cpp_7day = total_adset_spend_7day / total_adset_purchases_7day if total_adset_purchases_7day else 0
        avg_cpm_7day = (total_adset_spend_7day / total_adset_impressions_7day) * 1000 if total_adset_impressions_7day else 0
        avg_cpc_7day = total_adset_spend_7day / total_adset_clicks_7day if total_adset_clicks_7day else 0
        avg_ctr_7day = total_adset_clicks_7day / total_adset_impressions_7day if total_adset_impressions_7day else 0
        print_and_accumulate_html("Overall Ad Set Efficiency Metrics (Last 7 Days):", is_header=True, level=4)
        ad_set_efficiency_text = (
            f"Average CPP (Cost Per Purchase): ${avg_cpp_7day:,.2f}\n"
            f"Average CPM (Cost Per Mille): ${avg_cpm_7day:,.2f}\n"
            f"Average CPC (Cost Per Click): ${avg_cpc_7day:,.2f}\n"
            f"Average CTR (Click-Through Rate): {avg_ctr_7day:.2%}"
        )
        print_and_accumulate_html(ad_set_efficiency_text)
    else:
        print_and_accumulate_html("No ad set data found for the last 7 days.")
except Exception as e:
    print_and_accumulate_html(f"An error occurred fetching 7-day ad set metrics: {e}")

# Ad Set Reach & Frequency
print_and_accumulate_html(f"Ad Set Spend, Reach & Frequency (Last 7 Days) for {client_to_filter}", is_header=True, level=4)
sql_ad_set_reach_frequency_7day = bq_queries.get_ad_set_reach_frequency_7day_sql(table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
try:
    query_job_ad_sets_rf_7day = client.query(sql_ad_set_reach_frequency_7day)
    df_ad_set_rf_7day = query_job_ad_sets_rf_7day.to_dataframe()
    if not df_ad_set_rf_7day.empty:
        print_and_accumulate_html("Ad Set Reach & Frequency:", is_table=True, df=df_ad_set_rf_7day)
        overall_impressions_7day_rf = df_ad_set_rf_7day['total_impressions_7day'].sum()
        overall_reach_7day_rf = df_ad_set_rf_7day['total_reach_7day'].sum()
        avg_frequency_7day = overall_impressions_7day_rf / overall_reach_7day_rf if overall_reach_7day_rf else 0
        print_and_accumulate_html("Overall Average Ad Set Frequency (Last 7 Days):", is_header=True, level=5)
        print_and_accumulate_html(f"Average Frequency: {avg_frequency_7day:.2f}")
    else:
        print_and_accumulate_html("No ad set reach/frequency data found.")
except Exception as e:
    print_and_accumulate_html(f"An error occurred fetching 7-day ad set reach & frequency: {e}")

# %% [markdown]
# # VI. Facebook Ads Performance Executive Summary (Last 7 Days)
print_and_accumulate_html(f"Facebook Ads Performance Executive Summary (Last 7 Days) for {client_to_filter}", is_header=True, level=2)

# ## A. OVERVIEW: Last 7 Days Performance
print_and_accumulate_html(f"OVERVIEW: Last 7 Days Performance for {client_to_filter}", is_header=True, level=3)
if not df_overall_summary.empty:
    overall_roas_7d = df_overall_summary['overall_roas'].iloc[0]
    total_spend_7d = df_overall_summary['total_spend'].iloc[0]
    total_revenue_7d = df_overall_summary['total_revenue'].iloc[0]
    total_purchases_7d = df_overall_summary['total_purchases'].iloc[0]
    total_leads_7d = df_overall_summary['total_leads'].iloc[0]
    overall_cpl_7d = df_overall_summary['overall_cpl'].iloc[0]
    
    overview_text = (
        f"Overall ROAS (Return on Ad Spend): {overall_roas_7d:.2f}\n"
        f"Total Ad Spend: ${total_spend_7d:,.2f}\n"
        f"Total Revenue (from conversions): ${total_revenue_7d:,.2f}\n"
        f"Total Purchases: {total_purchases_7d:,.0f}\n"
        f"Total Leads: {total_leads_7d:,.0f}\n"
        f"Average Cost Per Lead (CPL): ${overall_cpl_7d:,.2f}"
    )
    print_and_accumulate_html(overview_text)
    
    if 'df_campaign_highlights' in locals() and not df_campaign_highlights.empty:
        top_campaign_roas = df_campaign_highlights['campaign_roas'].iloc[0]
        top_campaign_name = df_campaign_highlights['campaign_name'].iloc[0]
        print_and_accumulate_html(f"Top Campaign ROAS: {top_campaign_roas:.2f} (from campaign: {top_campaign_name})")
    else:
        print_and_accumulate_html("Top campaign ROAS data not available.")
else:
    print_and_accumulate_html("Overall summary data not available for executive summary.")

# ## C. TOP PERFORMING CAMPAIGNS (Last 7 Days)
print_and_accumulate_html(f"TOP PERFORMING CAMPAIGNS (Last 7 Days) for {client_to_filter}", is_header=True, level=3)
if 'df_campaign_highlights' in locals() and not df_campaign_highlights.empty:
    top_n_campaigns = min(3, len(df_campaign_highlights))
    if top_n_campaigns > 0:
        # Create a temporary DataFrame for HTML output of top N campaigns
        df_top_campaigns_html = df_campaign_highlights.head(top_n_campaigns).copy()
        # Format for better readability in HTML
        for col in ['campaign_spend', 'campaign_cpp']:
            if col in df_top_campaigns_html.columns: 
                df_top_campaigns_html[col] = df_top_campaigns_html[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else x)
        for col in ['campaign_roas']:
            if col in df_top_campaigns_html.columns:
                df_top_campaigns_html[col] = df_top_campaigns_html[col].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else x)
        for col in ['campaign_purchases']:
            if col in df_top_campaigns_html.columns:
                 df_top_campaigns_html[col] = df_top_campaigns_html[col].apply(lambda x: f"{x:,.0f}" if pd.notnull(x) else x)
        for col in ['campaign_ctr']:
            if col in df_top_campaigns_html.columns:
                df_top_campaigns_html[col] = df_top_campaigns_html[col].apply(lambda x: f"{x:.2%}" if pd.notnull(x) else x)
        print_and_accumulate_html("Top Campaigns Details:", is_table=True, df=df_top_campaigns_html)
    else:
        print_and_accumulate_html("No campaign highlight data available to display top performers.")
else:
    print_and_accumulate_html("Campaign highlights data not available for executive summary.")

# End of script - Save HTML content to a file
html_content += "</body></html>"
output_file_name = "facebook_ads_report.html"
with open(output_file_name, "w", encoding='utf-8') as f:
    f.write(html_content)
print(f"\nReport saved to {output_file_name}") 