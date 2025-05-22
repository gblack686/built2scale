# bq_queries.py

"""
This module provides functions to generate SQL queries for the EDA report.
"""

def get_overall_summary_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL for overall 7-day summary metrics, filtered by client_name."""
    return f"""
SELECT
    COUNT(DISTINCT campaign_id) AS number_of_active_campaigns,
    SUM(spend) AS total_spend,
    SUM(conversion_value) AS total_revenue,
    SUM(conversions) AS total_purchases,
    SUM(impressions) AS total_impressions,
    SUM(reach) AS total_reach,
    SUM(clicks) AS total_clicks,
    SUM(leads) AS total_leads,
    (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS overall_roas,
    (SUM(spend) / NULLIF(SUM(conversions), 0)) AS overall_cpp,
    (SUM(spend) / NULLIF(SUM(leads), 0)) AS overall_cpl,
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS overall_ctr,
    (SUM(impressions) / NULLIF(SUM(reach), 0)) AS overall_frequency,
    (SUM(spend) / NULLIF(SUM(impressions), 0)) * 1000 AS overall_cpm
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
"""

def get_campaign_highlights_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL for campaign performance highlights (7-Day), filtered by client_name."""
    return f"""
SELECT
    campaign_name,
    campaign_id,
    SUM(spend) AS campaign_spend,
    SUM(conversion_value) AS campaign_revenue,
    SUM(conversions) AS campaign_purchases,
    SUM(impressions) AS campaign_impressions,
    SUM(clicks) AS campaign_clicks,
    (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS campaign_roas,
    (SUM(spend) / NULLIF(SUM(conversions), 0)) AS campaign_cpp,
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS campaign_ctr
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
GROUP BY
    campaign_name, campaign_id
ORDER BY
    campaign_roas DESC
LIMIT 10
"""

def get_highest_ctr_campaign_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL for the campaign with the highest CTR (7-Day), filtered by client_name."""
    return f"""
SELECT
    campaign_name,
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS campaign_ctr
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
GROUP BY
    campaign_name
HAVING
    SUM(impressions) > 0
ORDER BY
    campaign_ctr DESC
LIMIT 1
"""

def get_lowest_cpl_campaign_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL for the campaign with the most efficient (lowest) CPL (7-Day), filtered by client_name."""
    return f"""
SELECT
    campaign_name,
    (SUM(spend) / NULLIF(SUM(leads), 0)) AS campaign_cpl
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
GROUP BY
    campaign_name
HAVING
    SUM(leads) > 0
ORDER BY
    campaign_cpl ASC
LIMIT 1
"""

def get_category_performance_sql(table_id: str, category_name: str, like_conditions: list, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL for performance by inferred product categories, filtered by client_name."""
    conditions_sql_str = " OR ".join([f"LOWER(campaign_name) LIKE '{condition.lower()}'" for condition in like_conditions])
    return f"""
    SELECT
        '{category_name}' AS inferred_category,
        SUM(spend) AS total_spend,
        SUM(conversion_value) AS total_revenue,
        SUM(conversions) AS total_purchases,
        (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS roas
    FROM
        {table_id}
    WHERE
        DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
        AND ({conditions_sql_str})
        AND client_name = '{client_name}'
    """

def get_campaign_metrics_3day_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL for campaign-level metrics (Last 3 Days), filtered by client_name."""
    return f"""
SELECT
    campaign_name,
    campaign_id,
    SUM(spend) AS spend_3day,
    SUM(conversion_value) AS revenue_3day,
    SUM(conversions) AS purchases_3day,
    SUM(impressions) AS impressions_3day,
    SUM(clicks) AS clicks_3day,
    (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS roas_3day,
    (SUM(spend) / NULLIF(SUM(conversions), 0)) AS cpp_3day,
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS ctr_3day
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
GROUP BY
    campaign_name, campaign_id
ORDER BY
    roas_3day DESC
"""

def get_ad_set_metrics_7day_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL for ad set-level metrics (Last 7 Days), filtered by client_name."""
    return f"""
SELECT
    adset_name,
    adset_id,
    SUM(spend) AS spend_7day,
    SUM(conversion_value) AS revenue_7day,
    SUM(conversions) AS purchases_7day,
    SUM(impressions) AS impressions_7day,
    SUM(clicks) AS clicks_7day,
    SUM(leads) AS leads_7day,
    (SUM(conversion_value) / NULLIF(SUM(spend), 0)) AS roas_7day,
    (SUM(spend) / NULLIF(SUM(conversions), 0)) AS cpp_7day, -- Cost Per Purchase
    (SUM(spend) / NULLIF(SUM(impressions), 0)) * 1000 AS cpm_7day, -- Cost Per Mille (Thousand Impressions)
    (SUM(spend) / NULLIF(SUM(clicks), 0)) AS cpc_7day, -- Cost Per Click
    (SUM(clicks) / NULLIF(SUM(impressions), 0)) AS ctr_7day -- Click-Through Rate
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
GROUP BY
    adset_name, adset_id
ORDER BY
    roas_7day DESC
"""

def get_ad_set_reach_frequency_7day_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL for ad set reach and frequency (Last 7 Days), filtered by client_name."""
    return f"""
SELECT
    adset_name,
    adset_id,
    SUM(reach) AS total_reach_7day,
    SUM(impressions) AS total_impressions_7day,
    (SUM(impressions) / NULLIF(SUM(reach), 0)) AS frequency_7day
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
GROUP BY
    adset_name, adset_id
ORDER BY
    total_reach_7day DESC
"""

def get_active_ad_set_count_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str) -> str:
    """Generates SQL to count distinct active ad sets within the date range, filtered by client_name."""
    return f"""
SELECT
    COUNT(DISTINCT adset_id) AS active_ad_set_count
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND adset_id IS NOT NULL AND adset_id != ''
    AND client_name = '{client_name}'
"""

def get_client_offers_sql(monitor_table_id: str, client_name: str) -> str:
    """Generates SQL to fetch distinct client_offer values for a given client_name."""
    return f"""
SELECT DISTINCT
    client_offer
FROM
    {monitor_table_id}
WHERE
    client_name = '{client_name}'
    AND client_offer IS NOT NULL AND client_offer != ''
ORDER BY
    client_offer
"""

def get_campaign_count_for_offer_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str, client_offer: str) -> str:
    """Generates SQL to count active campaigns for a specific client_name and client_offer."""
    return f"""
SELECT
    COUNT(DISTINCT campaign_id) AS campaign_count
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
    AND client_offer = '{client_offer}'
"""

def get_ad_set_count_for_offer_sql(table_id: str, start_date_str: str, end_date_str: str, client_name: str, client_offer: str) -> str:
    """Generates SQL to count active ad sets for a specific client_name and client_offer."""
    return f"""
SELECT
    COUNT(DISTINCT adset_id) AS ad_set_count
FROM
    {table_id}
WHERE
    DATE(date) >= '{start_date_str}' AND DATE(date) < '{end_date_str}'
    AND client_name = '{client_name}'
    AND client_offer = '{client_offer}'
    AND adset_id IS NOT NULL AND adset_id != ''
""" 