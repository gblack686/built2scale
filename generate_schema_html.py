import json

def generate_html_for_schemas(schemas):
    html_content = """
<html>
<head>
    <title>SQL Table Designs</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 1200px; margin: auto; background-color: #fff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        h2 { color: #555; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
        th, td { border: 1px solid #ddd; padding: 10px 12px; text-align: left; }
        th { background-color: #e9e9f3; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .purpose { background-color: #f0f8ff; padding: 10px; margin-bottom: 15px; border-left: 4px solid #7abaff; }
        .grain { font-style: italic; color: #666; margin-bottom: 10px; }
        .pk { font-weight: bold; color: #d9534f; }
        .fk { font-style: italic; color: #5bc0de; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Proposed SQL Table Designs for Client Statistics</h1>
"""

    for table in schemas:
        html_content += f"<h2>Table: <code>{table['name']}</code></h2>"
        if table.get('purpose'):
            html_content += f"<div class='purpose'><strong>Purpose:</strong> {table['purpose']}</div>"
        if table.get('grain'):
            html_content += f"<p class='grain'><strong>Grain:</strong> {table['grain']}</p>"
        
        html_content += """
        <table>
            <thead>
                <tr>
                    <th>Column Name</th>
                    <th>Data Type</th>
                    <th>Mode</th>
                    <th>Constraints / Notes</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
"""
        for col in table['columns']:
            constraints = []
            if col.get('is_pk'):
                constraints.append("<span class='pk'>PK</span>")
            if col.get('fk_reference'):
                constraints.append(f"<span class='fk'>FK -&gt; {col['fk_reference']}</span>")
            
            constraint_str = ", ".join(constraints) if constraints else ""

            html_content += f"""
                <tr>
                    <td>{col['name']}</td>
                    <td>{col['data_type']}</td>
                    <td>{col.get('mode', 'NULLABLE')}</td>
                    <td>{constraint_str}</td>
                    <td>{col['description']}</td>
                </tr>
"""
        html_content += """
            </tbody>
        </table>
"""
        if table.get('source'):
            html_content += f"<p><strong>Source:</strong> {table['source']}</p>"
        html_content += "<hr style='margin-top: 20px; margin-bottom: 40px; border: 0; border-top: 1px solid #ccc;'>"


    html_content += """
    </div>
</body>
</html>
"""
    return html_content

table_schemas = [
    {
        "name": "client_daily_performance_summary",
        "purpose": "To store daily aggregated performance metrics for each client, broken down by client offer and advertising network. This allows for daily trend analysis.",
        "grain": "report_date, client_name, client_offer, ad_network",
        "columns": [
            {"name": "report_date", "data_type": "DATE", "is_pk": True, "description": "The date for which the summary is recorded."},
            {"name": "client_name", "data_type": "STRING", "is_pk": True, "description": "Name of the client."},
            {"name": "client_offer", "data_type": "STRING", "is_pk": True, "description": "Specific offer for the client (e.g., 'Product A', 'All Offers')."},
            {"name": "ad_network", "data_type": "STRING", "is_pk": True, "description": "Advertising network (e.g., 'Facebook/Meta', 'Google Ads')."},
            {"name": "total_spend", "data_type": "FLOAT", "description": "Total amount spent."},
            {"name": "total_impressions", "data_type": "INTEGER", "description": "Total number of impressions."},
            {"name": "total_clicks", "data_type": "INTEGER", "description": "Total number of clicks."},
            {"name": "total_reach", "data_type": "INTEGER", "description": "Total unique users reached."},
            {"name": "total_purchases", "data_type": "INTEGER", "description": "Total number of purchase conversions."},
            {"name": "total_leads", "data_type": "INTEGER", "description": "Total number of lead conversions."},
            {"name": "total_registrations", "data_type": "INTEGER", "description": "Total number of registration conversions."},
            {"name": "total_conversion_value", "data_type": "FLOAT", "description": "Total monetary value from all conversions."},
            {"name": "roas", "data_type": "FLOAT", "description": "Return On Ad Spend (total_conversion_value / total_spend)."},
            {"name": "cpc", "data_type": "FLOAT", "description": "Cost Per Click (total_spend / total_clicks)."},
            {"name": "cpm", "data_type": "FLOAT", "description": "Cost Per Mille (Thousand Impressions) (total_spend / total_impressions * 1000)."},
            {"name": "ctr", "data_type": "FLOAT", "description": "Click-Through Rate (total_clicks / total_impressions)."},
            {"name": "cpa_purchase", "data_type": "FLOAT", "description": "Cost Per Purchase (total_spend / total_purchases)."},
            {"name": "cpa_lead", "data_type": "FLOAT", "description": "Cost Per Lead (total_spend / total_leads)."},
            {"name": "cpa_registration", "data_type": "FLOAT", "description": "Cost Per Registration (total_spend / total_registrations)."},
            {"name": "frequency", "data_type": "FLOAT", "description": "Average number of times ads were shown to each unique person (total_impressions / total_reach)."},
            {"name": "active_campaigns_count", "data_type": "INTEGER", "description": "Number of campaigns active on this day."},
            {"name": "active_adsets_count", "data_type": "INTEGER", "description": "Number of ad sets active on this day."},
            {"name": "active_ads_count", "data_type": "INTEGER", "description": "Number of ads active on this day."},
            {"name": "last_updated", "data_type": "TIMESTAMP", "description": "Timestamp of when the record was last updated."}
        ],
        "source": "Aggregated daily from v1_b2s_all_acquisition_production_report."
    },
    {
        "name": "client_campaign_periodic_summary",
        "purpose": "To store periodic (e.g., Last 7 Days, Last 30 Days, Month-to-Date) performance metrics for each campaign associated with a client and offer.",
        "grain": "client_name, client_offer, campaign_id, period_type, period_start_date, period_end_date",
        "columns": [
            {"name": "client_name", "data_type": "STRING", "is_pk": True, "description": "Name of the client."},
            {"name": "client_offer", "data_type": "STRING", "is_pk": True, "description": "Specific offer for the client."},
            {"name": "campaign_id", "data_type": "STRING", "is_pk": True, "description": "Unique identifier for the campaign."},
            {"name": "period_type", "data_type": "STRING", "is_pk": True, "description": "Type of period (e.g., 'L7D', 'L30D', 'MTD', 'Custom')."},
            {"name": "period_start_date", "data_type": "DATE", "is_pk": True, "description": "Start date of the summary period."},
            {"name": "period_end_date", "data_type": "DATE", "is_pk": True, "description": "End date of the summary period."},
            {"name": "campaign_name", "data_type": "STRING", "description": "Name of the campaign."},
            {"name": "ad_network", "data_type": "STRING", "description": "Advertising network."},
            {"name": "campaign_status", "data_type": "STRING", "description": "Current status of the campaign (e.g., 'Active', 'Paused')."},
            {"name": "total_spend", "data_type": "FLOAT", "description": "Total amount spent in the period."},
            {"name": "total_impressions", "data_type": "INTEGER", "description": "Total impressions in the period."},
            {"name": "total_clicks", "data_type": "INTEGER", "description": "Total clicks in the period."},
            {"name": "total_reach", "data_type": "INTEGER", "description": "Total unique users reached in the period."},
            {"name": "total_purchases", "data_type": "INTEGER", "description": "Total purchase conversions in the period."},
            {"name": "total_leads", "data_type": "INTEGER", "description": "Total lead conversions in the period."},
            {"name": "total_registrations", "data_type": "INTEGER", "description": "Total registration conversions in the period."},
            {"name": "total_conversion_value", "data_type": "FLOAT", "description": "Total monetary value from conversions in the period."},
            {"name": "roas", "data_type": "FLOAT", "description": "ROAS for the period."},
            {"name": "cpc", "data_type": "FLOAT", "description": "CPC for the period."},
            {"name": "cpm", "data_type": "FLOAT", "description": "CPM for the period."},
            {"name": "ctr", "data_type": "FLOAT", "description": "CTR for the period."},
            {"name": "cpa_purchase", "data_type": "FLOAT", "description": "Cost Per Purchase for the period."},
            {"name": "cpa_lead", "data_type": "FLOAT", "description": "Cost Per Lead for the period."},
            {"name": "cpa_registration", "data_type": "FLOAT", "description": "Cost Per Registration for the period."},
            {"name": "frequency", "data_type": "FLOAT", "description": "Average frequency for the period."},
            {"name": "health_score", "data_type": "FLOAT", "mode": "NULLABLE", "description": "Conceptual campaign health score if calculated."},
            {"name": "last_updated", "data_type": "TIMESTAMP", "description": "Timestamp of when the record was last updated."}
        ],
        "source": "Aggregated from v1_b2s_all_acquisition_production_report over the specified period."
    },
    {
        "name": "client_adset_periodic_summary",
        "purpose": "To store periodic performance metrics for each ad set within a campaign for a client and offer.",
        "grain": "client_name, client_offer, campaign_id, adset_id, period_type, period_start_date, period_end_date",
        "columns": [
            {"name": "client_name", "data_type": "STRING", "is_pk": True, "description": "Name of the client."},
            {"name": "client_offer", "data_type": "STRING", "is_pk": True, "description": "Specific offer for the client."},
            {"name": "campaign_id", "data_type": "STRING", "is_pk": True, "fk_reference": "client_campaign_periodic_summary.campaign_id", "description": "Campaign identifier."},
            {"name": "adset_id", "data_type": "STRING", "is_pk": True, "description": "Unique identifier for the ad set."},
            {"name": "period_type", "data_type": "STRING", "is_pk": True, "description": "Type of period."},
            {"name": "period_start_date", "data_type": "DATE", "is_pk": True, "description": "Start date of the summary period."},
            {"name": "period_end_date", "data_type": "DATE", "is_pk": True, "description": "End date of the summary period."},
            {"name": "campaign_name", "data_type": "STRING", "description": "Name of the parent campaign."},
            {"name": "adset_name", "data_type": "STRING", "description": "Name of the ad set."},
            {"name": "ad_network", "data_type": "STRING", "description": "Advertising network."},
            {"name": "adset_status", "data_type": "STRING", "description": "Current status of the ad set."},
            {"name": "total_spend", "data_type": "FLOAT", "description": "Total amount spent in the period."},
            # Common metrics will be inserted here by the script
            {"name": "frequency", "data_type": "FLOAT", "description": "Average frequency for the period."},
            {"name": "last_updated", "data_type": "TIMESTAMP", "description": "Timestamp of when the record was last updated."}
        ],
        "source": "Aggregated from v1_b2s_all_acquisition_production_report over the specified period."
    },
    {
        "name": "client_ad_periodic_summary",
        "purpose": "To store periodic performance metrics for each ad within an ad set for a client and offer.",
        "grain": "client_name, client_offer, campaign_id, adset_id, ad_id, period_type, period_start_date, period_end_date",
        "columns": [
            {"name": "client_name", "data_type": "STRING", "is_pk": True, "description": "Name of the client."},
            {"name": "client_offer", "data_type": "STRING", "is_pk": True, "description": "Specific offer for the client."},
            {"name": "campaign_id", "data_type": "STRING", "is_pk": True, "fk_reference": "client_campaign_periodic_summary.campaign_id", "description": "Campaign identifier."},
            {"name": "adset_id", "data_type": "STRING", "is_pk": True, "fk_reference": "client_adset_periodic_summary.adset_id", "description": "Ad set identifier."},
            {"name": "ad_id", "data_type": "STRING", "is_pk": True, "description": "Unique identifier for the ad."},
            {"name": "period_type", "data_type": "STRING", "is_pk": True, "description": "Type of period."},
            {"name": "period_start_date", "data_type": "DATE", "is_pk": True, "description": "Start date of the summary period."},
            {"name": "period_end_date", "data_type": "DATE", "is_pk": True, "description": "End date of the summary period."},
            {"name": "campaign_name", "data_type": "STRING", "description": "Name of the parent campaign."},
            {"name": "adset_name", "data_type": "STRING", "description": "Name of the parent ad set."},
            {"name": "ad_name", "data_type": "STRING", "description": "Name of the ad."},
            {"name": "ad_network", "data_type": "STRING", "description": "Advertising network."},
            {"name": "ad_status", "data_type": "STRING", "description": "Current status of the ad."},
            {"name": "total_spend", "data_type": "FLOAT", "description": "Total amount spent in the period."},
            # Common metrics will be inserted here by the script
            {"name": "frequency", "data_type": "FLOAT", "description": "Average frequency for the period."},
            {"name": "last_updated", "data_type": "TIMESTAMP", "description": "Timestamp of when the record was last updated."}
        ],
        "source": "Aggregated from v1_b2s_all_acquisition_production_report over the specified period."
    },
    {
        "name": "client_overall_snapshot",
        "purpose": "Provides a high-level snapshot of performance for each client and offer over standard reporting periods (e.g., L7D, L30D, MTD). This is useful for dashboards and executive summaries.",
        "grain": "client_name, client_offer, period_type",
        "columns": [
            {"name": "client_name", "data_type": "STRING", "is_pk": True, "description": "Name of the client."},
            {"name": "client_offer", "data_type": "STRING", "is_pk": True, "description": "Specific offer (or 'All Offers')."},
            {"name": "period_type", "data_type": "STRING", "is_pk": True, "description": "The period this snapshot represents (e.g., 'L7D', 'L30D', 'MTD', 'LastMonth')."},
            {"name": "period_start_date", "data_type": "DATE", "description": "Start date of the snapshot period."},
            {"name": "period_end_date", "data_type": "DATE", "description": "End date of the snapshot period."},
            {"name": "ad_network", "data_type": "STRING", "description": "Advertising network."},
            {"name": "total_spend", "data_type": "FLOAT", "description": "Total amount spent in the period."},
            {"name": "total_impressions", "data_type": "INTEGER", "description": "Total impressions in the period."},
            {"name": "total_clicks", "data_type": "INTEGER", "description": "Total clicks in the period."},
            {"name": "total_reach", "data_type": "INTEGER", "description": "Total unique users reached in the period."},
            {"name": "total_purchases", "data_type": "INTEGER", "description": "Total purchase conversions in the period."},
            {"name": "total_leads", "data_type": "INTEGER", "description": "Total lead conversions in the period."},
            {"name": "total_registrations", "data_type": "INTEGER", "description": "Total registration conversions in the period."},
            {"name": "total_conversion_value", "data_type": "FLOAT", "description": "Total monetary value from conversions in the period."},
            {"name": "roas", "data_type": "FLOAT", "description": "ROAS for the period."},
            {"name": "cpc", "data_type": "FLOAT", "description": "CPC for the period."},
            {"name": "cpm", "data_type": "FLOAT", "description": "CPM for the period."},
            {"name": "ctr", "data_type": "FLOAT", "description": "CTR for the period."},
            {"name": "cpa_purchase", "data_type": "FLOAT", "description": "Cost Per Purchase for the period."},
            {"name": "cpa_lead", "data_type": "FLOAT", "description": "Cost Per Lead for the period."},
            {"name": "cpa_registration", "data_type": "FLOAT", "description": "Cost Per Registration for the period."},
            {"name": "frequency", "data_type": "FLOAT", "description": "Average frequency for the period."},
            {"name": "number_of_active_campaigns", "data_type": "INTEGER", "description": "Total active campaigns in the period."},
            {"name": "number_of_active_adsets", "data_type": "INTEGER", "description": "Total active ad sets in the period."},
            {"name": "number_of_active_ads", "data_type": "INTEGER", "description": "Total active ads in the period."},
            {"name": "top_roas_campaign_name", "data_type": "STRING", "mode": "NULLABLE", "description": "Name of the campaign with the highest ROAS."},
            {"name": "top_roas_campaign_value", "data_type": "FLOAT", "mode": "NULLABLE", "description": "Highest ROAS value."},
            {"name": "lowest_cpl_campaign_name", "data_type": "STRING", "mode": "NULLABLE", "description": "Name of the campaign with the lowest CPL."},
            {"name": "lowest_cpl_campaign_value", "data_type": "FLOAT", "mode": "NULLABLE", "description": "Lowest CPL value."},
            {"name": "highest_ctr_campaign_name", "data_type": "STRING", "mode": "NULLABLE", "description": "Name of the campaign with the highest CTR."},
            {"name": "highest_ctr_campaign_value", "data_type": "FLOAT", "mode": "NULLABLE", "description": "Highest CTR value."},
            {"name": "last_updated", "data_type": "TIMESTAMP", "description": "Timestamp of when the record was last updated."}
        ],
        "source": "Aggregated from v1_b2s_all_acquisition_production_report or the periodic summary tables for standard periods."
    }
]

# Define common metrics to be inserted into adset and ad summary tables
common_metrics_definition = [
    {"name": "total_impressions", "data_type": "INTEGER", "description": "Total impressions in the period."},
    {"name": "total_clicks", "data_type": "INTEGER", "description": "Total clicks in the period."},
    {"name": "total_reach", "data_type": "INTEGER", "description": "Total unique users reached in the period."},
    {"name": "total_purchases", "data_type": "INTEGER", "description": "Total purchase conversions in the period."},
    {"name": "total_leads", "data_type": "INTEGER", "description": "Total lead conversions in the period."},
    {"name": "total_registrations", "data_type": "INTEGER", "description": "Total registration conversions in the period."},
    {"name": "total_conversion_value", "data_type": "FLOAT", "description": "Total monetary value from conversions in the period."},
    {"name": "roas", "data_type": "FLOAT", "description": "ROAS for the period."},
    {"name": "cpc", "data_type": "FLOAT", "description": "CPC for the period."},
    {"name": "cpm", "data_type": "FLOAT", "description": "CPM for the period."},
    {"name": "ctr", "data_type": "FLOAT", "description": "CTR for the period."},
    {"name": "cpa_purchase", "data_type": "FLOAT", "description": "Cost Per Purchase for the period."},
    {"name": "cpa_lead", "data_type": "FLOAT", "description": "Cost Per Lead for the period."},
    {"name": "cpa_registration", "data_type": "FLOAT", "description": "Cost Per Registration for the period."}
]

# Inject common metrics into adset and ad summary table definitions
for schema in table_schemas:
    if schema["name"] in ["client_adset_periodic_summary", "client_ad_periodic_summary"]:
        # Find the index of total_spend to insert common_metrics after it
        spend_index = -1
        for i, col_def in enumerate(schema["columns"]):
            if col_def["name"] == "total_spend":
                spend_index = i
                break
        
        if spend_index != -1:
            # Get columns before total_spend, total_spend itself, then common_metrics, then columns after
            cols_before_spend = schema["columns"][:spend_index+1]
            cols_after_spend_placeholder = [col for col in schema["columns"][spend_index+1:] if col["name"] not in [m["name"] for m in common_metrics_definition]] # Avoid duplicating common_metrics if already there
            
            # Reconstruct the columns list
            new_columns_list = cols_before_spend + common_metrics_definition[:] # Use a copy
            
            # Add back the remaining original columns (like frequency, last_updated) if they weren't in common_metrics
            # Ensure 'frequency' and 'last_updated' are preserved and placed correctly at the end (or before last_updated for frequency)
            
            # Extract frequency and last_updated if they exist in original cols_after_spend_placeholder
            original_frequency = next((col for col in cols_after_spend_placeholder if col["name"] == "frequency"), None)
            original_last_updated = next((col for col in cols_after_spend_placeholder if col["name"] == "last_updated"), None)

            # Add other unique columns from cols_after_spend_placeholder
            for col in cols_after_spend_placeholder:
                if col["name"] not in ["frequency", "last_updated"] and col["name"] not in [m["name"] for m in new_columns_list]:
                    new_columns_list.append(col)

            if original_frequency and original_frequency["name"] not in [m["name"] for m in new_columns_list]:
                 new_columns_list.append(original_frequency)
            elif "frequency" not in [m["name"] for m in new_columns_list] and "frequency" in [c["name"] for c in schema["columns"]]: # If it was supposed to be there
                 new_columns_list.append(next(c for c in schema["columns"] if c["name"] == "frequency"))


            if original_last_updated and original_last_updated["name"] not in [m["name"] for m in new_columns_list]:
                new_columns_list.append(original_last_updated)
            elif "last_updated" not in [m["name"] for m in new_columns_list] and "last_updated" in [c["name"] for c in schema["columns"]]: # If it was supposed to be there
                 new_columns_list.append(next(c for c in schema["columns"] if c["name"] == "last_updated"))
            
            schema["columns"] = new_columns_list


html_output = generate_html_for_schemas(table_schemas)

output_file_name = "sql_table_designs.html"
with open(output_file_name, "w", encoding='utf-8') as f:
    f.write(html_output)

print(f"HTML schema documentation saved to {output_file_name}")

# For the tool to see an output, print a snippet.
print("\n--- Start of HTML Output Snippet ---")
print(html_output[:1000])
print("--- End of HTML Output Snippet ---") 