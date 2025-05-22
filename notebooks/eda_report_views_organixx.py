import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import date, timedelta
import bq_queries as bq_queries

# Configuration
client_to_filter = "Organixx"  # Client specific configuration
markdown_content = ""
monitor_table_name = "client_offer_monitor_table"
output_md_file = f"facebook_ads_report_{client_to_filter.lower().replace(' ', '_')}_views.md"

# --- New Formatting Function ---
def format_df_for_markdown(df_original):
    if df_original is None or df_original.empty:
        return df_original
    df = df_original.copy()

    currency_cols = [
        'total_spend', 'campaign_spend', 'spend_3day', 'spend_7day',
        'total_revenue', 'campaign_revenue', 'revenue_3day', 'revenue_7day',
        'overall_cpp', 'campaign_cpp', 'cpp_3day', 'cpp_7day', 'avg_cpp_7day',
        'overall_cpl', 'campaign_cpl', 'cpl_3day', 'avg_cpl_7day',
        'overall_cpm', 'cpm_7day', 'avg_cpm_7day',
        'overall_cpc', 'cpc_7day', 'avg_cpc_7day'
    ]
    integer_cols = [
        'total_impressions', 'campaign_impressions', 'impressions_3day', 'impressions_7day', 'total_impressions_7day',
        'total_clicks', 'campaign_clicks', 'clicks_3day', 'clicks_7day',
        'total_purchases', 'campaign_purchases', 'purchases_3day', 'purchases_7day',
        'total_leads', 'campaign_leads', 'leads_7day',
        'total_reach', 'total_reach_7day',
        'total_active_campaigns', 'campaign_count', 'ad_set_count'
    ]
    percent_cols = [
        'overall_ctr', 'campaign_ctr', 'ctr_3day', 'ctr_7day', 'avg_ctr_7day'
    ]
    ratio_cols = [ # For ROAS and Frequency, typically 2 decimal places
        'overall_roas', 'campaign_roas', 'roas_3day', 'roas_7day',
        'avg_frequency_7day'
    ]

    for col in df.columns:
        if col in currency_cols:
            df[col] = df[col].apply(lambda x: f'${x:,.2f}' if pd.notnull(x) else 'N/A')
        elif col in integer_cols:
            df[col] = df[col].apply(lambda x: f'{x:,.0f}' if pd.notnull(x) else 'N/A')
        elif col in percent_cols:
            df[col] = df[col].apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/A')
        elif col in ratio_cols:
            df[col] = df[col].apply(lambda x: f'{x:.2f}' if pd.notnull(x) else 'N/A')
    return df
# --- End New Formatting Function ---

def initialize_markdown_header(client_name, offer_details, ad_network="Facebook/Meta"):
    global markdown_content
    markdown_content = f"# Facebook Ads Performance Report for {client_name} (Using Views)\n\n"
    markdown_content += f"## Report Quick Summary by Client Offer\n\n"
    markdown_content += f"**Ad Network:** {ad_network}\n\n"
    if offer_details:
        for offer_summary in offer_details:
            markdown_content += f"- **Offer:** {offer_summary['offer_name']}\n"
            markdown_content += f"  - **Ongoing Campaigns (Last 7 Days):** {offer_summary['campaign_count']}\n"
            markdown_content += f"  - **Active Ad Sets (Last 7 Days):** {offer_summary['ad_set_count']}\n\n"
    else:
        markdown_content += "No specific offer details found for this client in the reporting period.\n\n"
    markdown_content += "---\n\n"

def print_and_accumulate_markdown(text, is_header=False, level=2, is_table=False, df=None):
    global markdown_content
    print(text) # Keep console output for debugging/logging
    if is_table and df is not None:
        if not df.empty:
            # Apply formatting before converting to markdown
            formatted_df = format_df_for_markdown(df)
            markdown_content += formatted_df.to_markdown(index=False) + "\n\n"
        else:
            markdown_content += "No data to display in table.\n\n"
    elif is_header:
        markdown_content += f"{'#' * level} {text}\n\n"
    else:
        markdown_content += f"{text}\n\n"

# Configure BigQuery client
credentials_path = "C:/Users/gblac/OneDrive/Desktop/WeScaleCreators/BuiltToScale/built2scale-2c7cc11e1ca6.json"
project_id_fallback = "built2scale"
dataset_id = "b2sreporting"

try:
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    project_id = credentials.project_id
    print_and_accumulate_markdown(f"Successfully loaded credentials for project: {project_id}")
    client = bigquery.Client(project=project_id, credentials=credentials)
    print_and_accumulate_markdown(f"Connected to BigQuery project: {client.project} using service account.")
except Exception as e:
    print_and_accumulate_markdown(f"Error loading service account credentials from {credentials_path}: {e}")
    project_id = project_id_fallback
    client = bigquery.Client(project=project_id)
    if not client.project:
        print_and_accumulate_markdown("BigQuery client failed to initialize. Exiting script.")
        with open(output_md_file, "w", encoding='utf-8') as f:
            f.write(markdown_content)
        exit()

# Define date ranges
your_target_end_date = date.today()
your_target_start_date_7day = your_target_end_date - timedelta(days=7)
start_date_str_7day = your_target_start_date_7day.strftime('%Y-%m-%d')
end_date_str_7day = your_target_end_date.strftime('%Y-%m-%d')

your_target_start_date_3day = your_target_end_date - timedelta(days=3)
start_date_str_3day = your_target_start_date_3day.strftime('%Y-%m-%d')
end_date_str_3day = your_target_end_date.strftime('%Y-%m-%d')

print_and_accumulate_markdown(f"Reporting period (7-day): {start_date_str_7day} to {your_target_end_date - timedelta(days=1)}", is_header=True, level=2)

# Define table and view IDs
base_table_id = f"`{project_id}.{dataset_id}.v1_b2s_all_acquisition_production_report`"
monitor_table_id = f"`{project_id}.{dataset_id}.{monitor_table_name}`"
view_daily_summary_id = f"`{project_id}.{dataset_id}.wsc_client_daily_performance_summary`"
view_campaign_summary_id = f"`{project_id}.{dataset_id}.wsc_client_campaign_periodic_summary`"
view_adset_summary_id = f"`{project_id}.{dataset_id}.wsc_client_adset_periodic_summary`"

print_and_accumulate_markdown(f"Using base data table: {base_table_id}")
print_and_accumulate_markdown(f"Using client offer monitor table: {monitor_table_id}")
print_and_accumulate_markdown(f"Using campaign summary view: {view_campaign_summary_id}")
print_and_accumulate_markdown(f"Using adset summary view: {view_adset_summary_id}")

# Fetch client offers for the specified client (from monitor table)
offer_details_for_header = []
sql_client_offers = bq_queries.get_client_offers_sql(monitor_table_id, client_to_filter)
try:
    df_client_offers = client.query(sql_client_offers).to_dataframe()
    if not df_client_offers.empty:
        print_and_accumulate_markdown(f"Found {len(df_client_offers)} offers for client: {client_to_filter}")
        for index, row in df_client_offers.iterrows():
            current_offer = row['client_offer']
            sql_camp_count_offer = f"""
            SELECT COUNT(DISTINCT campaign_id) AS campaign_count
            FROM {view_campaign_summary_id}
            WHERE DATE(period_start_date) >= '{start_date_str_7day}' AND DATE(period_start_date) < '{end_date_str_7day}'
              AND client_name = '{client_to_filter}' AND client_offer = '{current_offer}' """
            df_camp_count = client.query(sql_camp_count_offer).to_dataframe()
            campaign_count_for_offer = df_camp_count['campaign_count'].iloc[0] if not df_camp_count.empty else 0

            sql_adset_count_offer = f"""
            SELECT COUNT(DISTINCT adset_id) AS ad_set_count
            FROM {view_adset_summary_id}
            WHERE DATE(period_start_date) >= '{start_date_str_7day}' AND DATE(period_start_date) < '{end_date_str_7day}'
              AND client_name = '{client_to_filter}' AND client_offer = '{current_offer}'
              AND adset_id IS NOT NULL AND adset_id != '' """
            df_adset_count = client.query(sql_adset_count_offer).to_dataframe()
            ad_set_count_for_offer = df_adset_count['ad_set_count'].iloc[0] if not df_adset_count.empty else 0
            
            offer_details_for_header.append({
                "offer_name": current_offer, "campaign_count": campaign_count_for_offer, "ad_set_count": ad_set_count_for_offer
            })
    else:
        print_and_accumulate_markdown(f"No offers found for client {client_to_filter} in the monitor table.")
except Exception as e:
    print_and_accumulate_markdown(f"An error occurred fetching client offers: {e}")

initialize_markdown_header(client_to_filter, offer_details_for_header)

# Overall 7-Day Summary Metrics (Using base_table_id for accuracy of distinct counts like reach)
print_and_accumulate_markdown(f"Overall 7-Day Performance Summary for {client_to_filter} (All Offers Combined)", is_header=True, level=3)
sql_overall_summary = bq_queries.get_overall_summary_sql(base_table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
try:
    df_overall_summary = client.query(sql_overall_summary).to_dataframe()
    if not df_overall_summary.empty:
        print_and_accumulate_markdown("Overall Summary Data (Client - All Offers, from Base Table for Accuracy):", is_table=True, df=df_overall_summary)
    else:
        print_and_accumulate_markdown("No overall summary data returned.")
except Exception as e:
    print_and_accumulate_markdown(f"An error occurred fetching overall summary: {e}")
    df_overall_summary = pd.DataFrame()

# Campaign Performance Highlights (7-Day, from view_campaign_summary_id)
print_and_accumulate_markdown(f"Campaign Performance Highlights (Last 7 Days) for {client_to_filter}", is_header=True, level=3)
sql_campaign_highlights = f"""
SELECT
    campaign_name, campaign_id,
    SUM(total_spend) AS campaign_spend,
    SUM(total_conversion_value) AS campaign_revenue,
    SUM(total_purchases) AS campaign_purchases,
    SUM(total_impressions) AS campaign_impressions,
    SUM(total_clicks) AS campaign_clicks,
    (SUM(total_conversion_value) / NULLIF(SUM(total_spend), 0)) AS campaign_roas,
    (SUM(total_spend) / NULLIF(SUM(total_purchases), 0)) AS campaign_cpp,
    (SUM(total_clicks) / NULLIF(SUM(total_impressions), 0)) AS campaign_ctr
FROM {view_campaign_summary_id}
WHERE DATE(period_start_date) >= '{start_date_str_7day}' AND DATE(period_start_date) < '{end_date_str_7day}'
AND client_name = '{client_to_filter}'
GROUP BY campaign_name, campaign_id
ORDER BY campaign_roas DESC LIMIT 10 """
try:
    df_campaign_highlights = client.query(sql_campaign_highlights).to_dataframe()
    if not df_campaign_highlights.empty:
        print_and_accumulate_markdown("Top Campaign Performance (from View):", is_table=True, df=df_campaign_highlights)
    else:
        print_and_accumulate_markdown("No campaign highlight data returned from view.")
except Exception as e:
    print_and_accumulate_markdown(f"An error occurred fetching campaign highlights from view: {e}")
    df_campaign_highlights = pd.DataFrame()

# Audience Engagement & Lead Generation Summary (derived from df_overall_summary)
print_and_accumulate_markdown(f"Audience Engagement & Lead Generation Summary (Last 7 Days) for {client_to_filter}", is_header=True, level=3)
if not df_overall_summary.empty:
    total_clicks = df_overall_summary['total_clicks'].iloc[0] if 'total_clicks' in df_overall_summary.columns and not df_overall_summary['total_clicks'].empty else 0
    overall_ctr = df_overall_summary['overall_ctr'].iloc[0] if 'overall_ctr' in df_overall_summary.columns and not df_overall_summary['overall_ctr'].empty else 0
    total_leads = df_overall_summary['total_leads'].iloc[0] if 'total_leads' in df_overall_summary.columns and not df_overall_summary['total_leads'].empty else 0
    overall_cpl = df_overall_summary['overall_cpl'].iloc[0] if 'overall_cpl' in df_overall_summary.columns and not df_overall_summary['overall_cpl'].empty else 0
    engagement_text = (f"Total Clicks: {total_clicks:,.0f}\n"
                       f"Overall Average CTR: {overall_ctr:.2%}\n"
                       f"Total Leads Captured: {total_leads:,.0f}\n"
                       f"Overall Average Cost Per Lead (CPL): ${overall_cpl:,.2f}")
    print_and_accumulate_markdown(engagement_text)
else:
    print_and_accumulate_markdown("Overall summary data not available for audience engagement.")

# Highest CTR Campaign (from view_campaign_summary_id)
sql_highest_ctr_campaign = f"""
SELECT campaign_name, (SUM(total_clicks) / NULLIF(SUM(total_impressions), 0)) AS campaign_ctr
FROM {view_campaign_summary_id}
WHERE DATE(period_start_date) >= '{start_date_str_7day}' AND DATE(period_start_date) < '{end_date_str_7day}'
AND client_name = '{client_to_filter}'
GROUP BY campaign_name HAVING SUM(total_impressions) > 0 ORDER BY campaign_ctr DESC LIMIT 1 """
try:
    df_highest_ctr = client.query(sql_highest_ctr_campaign).to_dataframe()
    print_and_accumulate_markdown("Campaign with Highest CTR (from View):", is_header=True, level=4)
    if not df_highest_ctr.empty:
        ctr_text = (f"- Campaign: {df_highest_ctr['campaign_name'].iloc[0]}\n"
                    f"- CTR: {df_highest_ctr['campaign_ctr'].iloc[0]:.2%}")
        print_and_accumulate_markdown(ctr_text)
    else:
        print_and_accumulate_markdown("No campaign data found for highest CTR from view.")
except Exception as e:
    print_and_accumulate_markdown(f"An error occurred fetching highest CTR campaign from view: {e}")

# Lowest CPL Campaign (from view_campaign_summary_id)
sql_lowest_cpl_campaign = f"""
SELECT campaign_name, (SUM(total_spend) / NULLIF(SUM(total_leads), 0)) AS campaign_cpl
FROM {view_campaign_summary_id} 
WHERE DATE(period_start_date) >= '{start_date_str_7day}' AND DATE(period_start_date) < '{end_date_str_7day}'
AND client_name = '{client_to_filter}'
GROUP BY campaign_name HAVING SUM(total_leads) > 0 ORDER BY campaign_cpl ASC LIMIT 1 """
try:
    df_lowest_cpl = client.query(sql_lowest_cpl_campaign).to_dataframe()
    print_and_accumulate_markdown("Campaign with Most Efficient (Lowest) CPL (from View):", is_header=True, level=4)
    if not df_lowest_cpl.empty:
        cpl_text = (f"- Campaign: {df_lowest_cpl['campaign_name'].iloc[0]}\n"
                    f"- CPL: ${df_lowest_cpl['campaign_cpl'].iloc[0]:,.2f}")
        print_and_accumulate_markdown(cpl_text)
    else:
        print_and_accumulate_markdown("No campaign data found for lowest CPL from view.")
except Exception as e:
    print_and_accumulate_markdown(f"An error occurred fetching lowest CPL campaign from view: {e}")

# Product Category Performance (from base_table_id)
print_and_accumulate_markdown(f"Product Category Performance (Inferred, Last 7 Days, from Base Table) for {client_to_filter}", is_header=True, level=3)
categories_to_analyze = {
    "Footwear (Boots, Slip Ons)": ["%boot%", "%slip on%", "%slip-on%"],
    "Clearance Campaigns": ["%clearance%"], "DPA Campaigns": ["%dpa%"], "UGC Testing Campaigns": ["%ugc test%", "%ugc%"]
}
all_category_dfs = []
for cat_name, keywords in categories_to_analyze.items():
    print_and_accumulate_markdown(f"Fetching data for: {cat_name}", is_header=True, level=4)
    query = bq_queries.get_category_performance_sql(base_table_id, cat_name, keywords, start_date_str_7day, end_date_str_7day, client_to_filter)
    try:
        df_cat = client.query(query).to_dataframe()
        if not df_cat.empty and pd.notna(df_cat['total_spend'].iloc[0]) and df_cat['total_spend'].iloc[0] > 0:
            print_and_accumulate_markdown(f"{cat_name} Performance:", is_table=True, df=df_cat)
            all_category_dfs.append(df_cat)
        elif not df_cat.empty: print_and_accumulate_markdown(f"No significant spend or data found for {cat_name}.")
        else: print_and_accumulate_markdown(f"No data returned for {cat_name}.")
    except Exception as e: print_and_accumulate_markdown(f"An error querying for {cat_name}: {e}")
if all_category_dfs:
    df_inferred_categories_summary = pd.concat(all_category_dfs, ignore_index=True)
    print_and_accumulate_markdown("Summary of Inferred Categories:", is_table=True, df=df_inferred_categories_summary)
else: print_and_accumulate_markdown("No data found for any inferred categories.")

# Campaign Performance Overview (3-Day, from view_campaign_summary_id)
print_and_accumulate_markdown(f"Facebook Campaign Performance Overview (Last 3 Days: {start_date_str_3day} to {your_target_end_date - timedelta(days=1)}) for {client_to_filter}", is_header=True, level=3)
sql_campaign_metrics_3day = f"""
SELECT
    campaign_name, campaign_id, SUM(total_spend) AS spend_3day, SUM(total_conversion_value) AS revenue_3day,
    SUM(total_purchases) AS purchases_3day, SUM(total_impressions) AS impressions_3day, SUM(total_clicks) AS clicks_3day,
    (SUM(total_conversion_value) / NULLIF(SUM(total_spend), 0)) AS roas_3day,
    (SUM(total_spend) / NULLIF(SUM(total_purchases), 0)) AS cpp_3day,
    (SUM(total_clicks) / NULLIF(SUM(total_impressions), 0)) AS ctr_3day
FROM {view_campaign_summary_id}
WHERE DATE(period_start_date) >= '{start_date_str_3day}' AND DATE(period_start_date) < '{end_date_str_3day}'
AND client_name = '{client_to_filter}'
GROUP BY campaign_name, campaign_id ORDER BY roas_3day DESC """
try:
    df_campaign_metrics_3day = client.query(sql_campaign_metrics_3day).to_dataframe()
    if not df_campaign_metrics_3day.empty:
        print_and_accumulate_markdown("Campaign-Level Performance (Last 3 Days, from View):", is_table=True, df=df_campaign_metrics_3day)
        overall_spend_3day = df_campaign_metrics_3day['spend_3day'].sum()
        overall_revenue_3day = df_campaign_metrics_3day['revenue_3day'].sum()
        overall_purchases_3day = df_campaign_metrics_3day['purchases_3day'].sum()
        overall_roas_3day = overall_revenue_3day / overall_spend_3day if overall_spend_3day else 0
        overall_cpp_3day = overall_spend_3day / overall_purchases_3day if overall_purchases_3day else 0
        print_and_accumulate_markdown("Overall Portfolio Performance (Last 3 Days, Calculated from View Data):", is_header=True, level=4)
        summary_3day_text = (f"Total Spend: ${overall_spend_3day:,.2f}\n"
                             f"Total Revenue: ${overall_revenue_3day:,.2f}\n"
                             f"Total Purchases: {overall_purchases_3day:,.0f}\n"
                             f"Overall ROAS: {overall_roas_3day:.2f}\n"
                             f"Average CPP: ${overall_cpp_3day:,.2f}")
        print_and_accumulate_markdown(summary_3day_text)
    else: print_and_accumulate_markdown("No 3-day campaign data from view.")
except Exception as e: print_and_accumulate_markdown(f"An error fetching 3-day campaign metrics from view: {e}")

# Ad Set Analysis (7-Day, from view_adset_summary_id)
print_and_accumulate_markdown(f"Facebook Ad Set Analysis (Last 7 Days) for {client_to_filter}", is_header=True, level=3)
sql_ad_set_metrics_7day = f"""
SELECT
    adset_name, adset_id, SUM(total_spend) AS spend_7day, SUM(total_conversion_value) AS revenue_7day,
    SUM(total_purchases) AS purchases_7day, SUM(total_impressions) AS impressions_7day,
    SUM(total_clicks) AS clicks_7day, SUM(total_leads) AS leads_7day,
    (SUM(total_conversion_value) / NULLIF(SUM(total_spend), 0)) AS roas_7day,
    (SUM(total_spend) / NULLIF(SUM(total_purchases), 0)) AS cpp_7day,
    (SUM(total_spend) / NULLIF(SUM(total_impressions), 0)) * 1000 AS cpm_7day,
    (SUM(total_spend) / NULLIF(SUM(total_clicks), 0)) AS cpc_7day,
    (SUM(total_clicks) / NULLIF(SUM(total_impressions), 0)) AS ctr_7day
FROM {view_adset_summary_id}
WHERE DATE(period_start_date) >= '{start_date_str_7day}' AND DATE(period_start_date) < '{end_date_str_7day}'
AND client_name = '{client_to_filter}'
GROUP BY adset_name, adset_id ORDER BY roas_7day DESC """
try:
    df_ad_set_metrics_7day = client.query(sql_ad_set_metrics_7day).to_dataframe()
    if not df_ad_set_metrics_7day.empty:
        print_and_accumulate_markdown("Ad Set-Level Performance (Last 7 Days, from View):", is_table=True, df=df_ad_set_metrics_7day)
        total_adset_spend_7day = df_ad_set_metrics_7day['spend_7day'].sum()
        total_adset_purchases_7day = df_ad_set_metrics_7day['purchases_7day'].sum()
        total_adset_impressions_7day = df_ad_set_metrics_7day['impressions_7day'].sum()
        total_adset_clicks_7day = df_ad_set_metrics_7day['clicks_7day'].sum()
        
        avg_cpp_7day = total_adset_spend_7day / total_adset_purchases_7day if total_adset_purchases_7day else 0
        avg_cpm_7day = (total_adset_spend_7day / total_adset_impressions_7day) * 1000 if total_adset_impressions_7day else 0
        avg_cpc_7day = total_adset_spend_7day / total_adset_clicks_7day if total_adset_clicks_7day else 0
        avg_ctr_7day = total_adset_clicks_7day / total_adset_impressions_7day if total_adset_impressions_7day else 0
        
        print_and_accumulate_markdown("Overall Ad Set Efficiency Metrics (Last 7 Days, Calculated from View Data):", is_header=True, level=4)
        ad_set_efficiency_text = (f"Average CPP (Cost Per Purchase): ${avg_cpp_7day:,.2f}\n"
                                  f"Average CPM (Cost Per Mille): ${avg_cpm_7day:,.2f}\n"
                                  f"Average CPC (Cost Per Click): ${avg_cpc_7day:,.2f}\n"
                                  f"Average CTR (Click-Through Rate): {avg_ctr_7day:.2%}")
        print_and_accumulate_markdown(ad_set_efficiency_text)
    else: print_and_accumulate_markdown("No 7-day ad set data from view.")
except Exception as e: print_and_accumulate_markdown(f"An error fetching 7-day ad set metrics from view: {e}")

# Ad Set Reach & Frequency (from base_table_id for accurate period reach)
print_and_accumulate_markdown(f"Ad Set Spend, Reach & Frequency (Last 7 Days, from Base Table) for {client_to_filter}", is_header=True, level=4)
sql_ad_set_reach_frequency_7day = bq_queries.get_ad_set_reach_frequency_7day_sql(base_table_id, start_date_str_7day, end_date_str_7day, client_to_filter)
try:
    df_ad_set_rf_7day = client.query(sql_ad_set_reach_frequency_7day).to_dataframe()
    if not df_ad_set_rf_7day.empty:
        print_and_accumulate_markdown("Ad Set Reach & Frequency (from Base Table):", is_table=True, df=df_ad_set_rf_7day)
        overall_impressions_7day_rf = df_ad_set_rf_7day['total_impressions_7day'].sum()
        overall_reach_7day_rf = df_ad_set_rf_7day['total_reach_7day'].sum()
        avg_frequency_7day = overall_impressions_7day_rf / overall_reach_7day_rf if overall_reach_7day_rf else 0
        print_and_accumulate_markdown("Overall Average Ad Set Frequency (Last 7 Days, from Base Table):", is_header=True, level=5)
        print_and_accumulate_markdown(f"Average Frequency: {avg_frequency_7day:.2f}")
    else: print_and_accumulate_markdown("No ad set reach/frequency data from base table.")
except Exception as e: print_and_accumulate_markdown(f"An error fetching 7-day ad set reach & frequency: {e}")

# Executive Summary (relies on df_overall_summary and df_campaign_highlights)
print_and_accumulate_markdown(f"Facebook Ads Performance Executive Summary (Last 7 Days) for {client_to_filter}", is_header=True, level=2)
print_and_accumulate_markdown(f"OVERVIEW: Last 7 Days Performance for {client_to_filter}", is_header=True, level=3)
if not df_overall_summary.empty:
    overall_roas_7d = df_overall_summary['overall_roas'].iloc[0] if 'overall_roas' in df_overall_summary.columns and not df_overall_summary['overall_roas'].empty else 0
    total_spend_7d = df_overall_summary['total_spend'].iloc[0] if 'total_spend' in df_overall_summary.columns and not df_overall_summary['total_spend'].empty else 0
    total_revenue_7d = df_overall_summary['total_revenue'].iloc[0] if 'total_revenue' in df_overall_summary.columns and not df_overall_summary['total_revenue'].empty else 0
    total_purchases_7d = df_overall_summary['total_purchases'].iloc[0] if 'total_purchases' in df_overall_summary.columns and not df_overall_summary['total_purchases'].empty else 0
    total_leads_7d = df_overall_summary['total_leads'].iloc[0] if 'total_leads' in df_overall_summary.columns and not df_overall_summary['total_leads'].empty else 0
    overall_cpl_7d = df_overall_summary['overall_cpl'].iloc[0] if 'overall_cpl' in df_overall_summary.columns and not df_overall_summary['overall_cpl'].empty else 0
    
    overview_text = (f"Overall ROAS: {overall_roas_7d:.2f}\n"
                     f"Total Ad Spend: ${total_spend_7d:,.2f}\n"
                     f"Total Revenue: ${total_revenue_7d:,.2f}\n"
                     f"Total Purchases: {total_purchases_7d:,.0f}\n"
                     f"Total Leads: {total_leads_7d:,.0f}\n"
                     f"Average CPL: ${overall_cpl_7d:,.2f}")
    print_and_accumulate_markdown(overview_text)
    
    if not df_campaign_highlights.empty and 'campaign_roas' in df_campaign_highlights.columns:
        top_campaign_roas = df_campaign_highlights['campaign_roas'].iloc[0]
        top_campaign_name = df_campaign_highlights['campaign_name'].iloc[0]
        print_and_accumulate_markdown(f"Top Campaign ROAS (from View data): {top_campaign_roas:.2f} (from campaign: {top_campaign_name})")
    else: print_and_accumulate_markdown("Top campaign ROAS data not available from view.")
else: print_and_accumulate_markdown("Overall summary data not available for executive summary.")

print_and_accumulate_markdown(f"TOP PERFORMING CAMPAIGNS (Last 7 Days, from View) for {client_to_filter}", is_header=True, level=3)
if not df_campaign_highlights.empty:
    top_n_campaigns = min(3, len(df_campaign_highlights))
    if top_n_campaigns > 0:
        df_top_campaigns_md = df_campaign_highlights.head(top_n_campaigns).copy()
        print_and_accumulate_markdown("Top Campaigns Details (from View):", is_table=True, df=df_top_campaigns_md)
    else: print_and_accumulate_markdown("No campaign highlight data from view.")
else: print_and_accumulate_markdown("Campaign highlights data from view not available for exec summary.")

# Save Markdown
with open(output_md_file, "w", encoding='utf-8') as f:
    f.write(markdown_content)
print(f"\nReport saved to {output_md_file}")

# To run this script:
# 1. Ensure `bq_queries.py` is in the same directory or accessible in PYTHONPATH.
# 2. Make sure the `wsc_...` views have been created in your BigQuery dataset.
# 3. Execute: python notebooks/eda_report_views_organixx.py

pass
