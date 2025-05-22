# BigQuery Client Performance Views Summary

This document provides a brief overview of the custom BigQuery views created for analyzing client advertising performance. These views are derived from the `v1_b2s_all_acquisition_production_report` table and present data on a daily aggregated basis.

## 1. `wsc_client_daily_performance_summary`

*   **Definition:** Provides a daily snapshot of overall performance metrics for each client, further broken down by client offer and advertising network.
*   **Key Metrics:**
    *   `report_date`, `client_name`, `client_offer`, `ad_network`
    *   `total_spend`, `total_impressions`, `total_clicks`, `total_reach`
    *   `total_purchases` (derived from `conversions`), `total_leads`, `total_registrations`
    *   `total_conversion_value`
    *   Calculated KPIs: `roas`, `cpc`, `cpm`, `ctr`, `cpa_purchase`, `cpa_lead`, `cpa_registration`, `frequency`
    *   Counts: `active_campaigns_count`, `active_adsets_count`, `active_ads_count`
*   **Analytical Uses:**
    *   Track daily trends in spending, engagement, and conversion for specific clients and their offers.
    *   Monitor overall account health at a glance.
    *   Compare performance across different ad networks for the same client offer.
    *   Identify sudden drops or spikes in key metrics that may require attention.

## 2. `wsc_client_campaign_periodic_summary`

*   **Definition:** Aggregates performance metrics at the campaign level for each client and offer, on a daily basis. (Note: `period_type` is static 'Daily', `period_start_date` and `period_end_date` are the report date).
*   **Key Metrics:**
    *   `period_start_date` (report_date), `client_name`, `client_offer`, `campaign_id`, `campaign_name`, `ad_network`, `campaign_status`
    *   Core performance metrics: `total_spend`, `total_impressions`, `total_clicks`, `total_reach`, `total_purchases`, `total_leads`, `total_registrations`, `total_conversion_value`
    *   Calculated KPIs: `roas`, `cpc`, `cpm`, `ctr`, `cpa_purchase`, `cpa_lead`, `cpa_registration`, `frequency`
*   **Analytical Uses:**
    *   Analyze daily performance of individual campaigns.
    *   Compare campaign effectiveness for a specific client offer.
    *   Identify top and bottom performing campaigns based on ROAS, CPA, or other KPIs.
    *   Track daily changes in campaign status and their impact.

## 3. `wsc_client_adset_periodic_summary`

*   **Definition:** Aggregates performance metrics at the ad set level within each campaign, client, and offer, on a daily basis.
*   **Key Metrics:**
    *   `period_start_date` (report_date), `client_name`, `client_offer`, `campaign_id`, `campaign_name`, `adset_id`, `adset_name`, `ad_network`, `adset_status`
    *   Core performance metrics and calculated KPIs similar to the campaign summary.
*   **Analytical Uses:**
    *   Dive deeper into campaign performance by examining individual ad sets.
    *   Identify which audiences or targeting strategies (represented by ad sets) are driving results.
    *   Optimize budget allocation by shifting spend towards higher-performing ad sets.
    *   Monitor daily ad set delivery and status.

## 4. `wsc_client_ad_periodic_summary`

*   **Definition:** Provides the most granular daily performance view, aggregating metrics at the individual ad level within each ad set, campaign, client, and offer.
*   **Key Metrics:**
    *   `period_start_date` (report_date), `client_name`, `client_offer`, `campaign_id`, `campaign_name`, `adset_id`, `adset_name`, `ad_id`, `ad_name`, `ad_network`, `ad_status`
    *   Core performance metrics and calculated KPIs similar to ad set and campaign summaries.
*   **Analytical Uses:**
    *   Analyze the performance of specific ad creatives and copy.
    *   Identify winning ads to scale and underperforming ads to pause or iterate on.
    *   Understand which ad elements (visuals, headlines, CTAs) resonate best with the target audience.
    *   Track daily ad delivery and status.

## 5. `wsc_client_overall_snapshot`

*   **Definition:** Offers a daily high-level performance summary for each client and their offers, across different ad networks. (Note: `period_type` is static 'Daily', `period_start_date` and `period_end_date` are the report date).
*   **Key Metrics:**
    *   `period_start_date` (report_date), `client_name`, `client_offer`, `ad_network`
    *   Aggregated core performance metrics: `total_spend`, `total_impressions`, `total_clicks`, `total_reach`, `total_purchases`, `total_leads`, `total_registrations`, `total_conversion_value`
    *   Aggregated calculated KPIs: `roas`, `cpc`, `cpm`, `ctr`, `cpa_purchase`, `cpa_lead`, `cpa_registration`, `frequency`
    *   Aggregated counts: `number_of_active_campaigns`, `number_of_active_adsets`, `number_of_active_ads`
*   **Analytical Uses:**
    *   Quickly assess the daily overall health and performance of a client's advertising efforts for specific offers.
    *   Compare performance across different client offers or ad networks at a high level.
    *   Suitable for daily dashboarding or quick reporting needs.

---

These views provide a structured way to query and analyze advertising data from the most granular ad level up to an overall client snapshot, all based on daily aggregations from your primary data source. 