# B2S Reporting Database Schema Overview

This document provides a comprehensive overview of the tables in the `built2scale.b2sreporting` dataset, including their schema, purpose, and how they contribute to performance reporting and analysis.

## Overview of Database Structure

The B2S Reporting database consists of six primary tables designed to track and analyze advertising performance across various platforms, with detailed breakdowns available, particularly for Meta (Facebook/Instagram) campaigns. These tables work together to provide a comprehensive view of client performance, campaign effectiveness, media buyer efficiency, and audience engagement.

## Table Relationships and Data Flow

The tables are structured to provide both summarized and highly granular views of performance data. `v1_b2s_all_acquisition_production_report` serves as a core detailed data source. The breakdown tables expand upon this data with specific dimensions. Comparative and monitoring tables offer aggregated views for trend analysis and high-level tracking.

```
┌───────────────────────────────────────────┐
│ v1_b2s_all_acquisition_production_report  │
│ (Core daily performance data at ad level) │
└────────────────────┬──────────────────────┘
                     │
                     ├──────────────────────────────────────────┐
                     │                                          │
┌────────────────────▼──────────────────────┐  ┌─────────────────▼─────────────────────┐
│ b2s_meta_acquisition_demo_breakdown_      │  │ b2s_meta_acquisition_tech_breakdown_  │
│ by_date_report                            │  │ by_date_report                        │
│ (Meta performance by Age, Gender)         │  │ (Meta performance by Device, Platform)│
└───────────────────────────────────────────┘  └───────────────────────────────────────┘
                     ┌──────────────────────────────────────────┐
                     │ Linkages primarily on campaign, adset, ad IDs, date, client, offer
                     ▼
┌───────────────────────────────────────────┐  ┌───────────────────────────────────────┐
│ client_offer_compare_table                │  │ client_offer_monitor_table            │
│ (Comparative performance over time)       │  │ (High-level client/offer monitoring)  │
└────────────────────┬──────────────────────┘  └────────────────────┬──────────────────┘
                     │                                          │
                     └─────────────────┬──────────────────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────┐
                         │    media_buyers_table    │
                         │ (Performance by media    │
                         │          buyer)          │
                         └──────────────────────────┘
```

## Detailed Table Descriptions

### 1. `v1_b2s_all_acquisition_production_report`

**Purpose**: This is a core table containing detailed daily acquisition data at the ad level across various advertising channels. It forms the foundation for most performance reporting.

**Key Features**:
- Tracks performance by `date` at `client_name`, `client_offer`, `campaign_name`, `adset_name`, and `ad_name` levels.
- Contains essential metrics: `spend`, `impressions`, `clicks`, `conversions`, `conversion_value`, `leads`, `registrations`.
- Includes identifiers for `advertising_account_name`, `advertising_channel`, and `media_buyer`.
- Fields like `campaign_delivery`, `adset_delivery`, `ad_delivery`, and `active` provide operational status.

**Row Count**: 118,847 (example)

**Key Columns for Reporting**:
- `date` (TIMESTAMP): Essential for all time-based analysis.
- `client_name`, `client_offer`: For segmenting performance by client and specific offerings.
- `advertising_channel`: To compare performance across different ad platforms (e.g., Facebook, Google Ads).
- `campaign_name`, `campaign_id`: For campaign-level analysis.
- `adset_name`, `adset_id`: For ad set/ad group level analysis.
- `ad_name`, `ad_id`: For individual ad creative performance analysis.
- `spend`, `impressions`, `clicks`, `conversions`, `conversion_value`, `leads`, `registrations`, `reach`: Core raw metrics for calculating KPIs (ROAS, CPA, CTR, CPL, etc.).
- `media_buyer`: To attribute performance to specific team members.

### 2. `b2s_meta_acquisition_demo_breakdown_by_date_report`

**Purpose**: Provides detailed demographic breakdowns (age and gender) for Meta (Facebook/Instagram) advertising performance, augmenting the data from the core acquisition report.

**Key Features**:
- Segments core acquisition metrics (`spend`, `impressions`, `clicks`, `conversions`, etc.) by `age` and `gender` for Meta campaigns.
- Used for analyzing audience performance and optimizing demographic targeting on Meta platforms.

**Row Count**: 395,037 (example)

**Key Columns for Reporting**:
- All key metrics and identifiers from `v1_b2s_all_acquisition_production_report` (conceptually joined on common keys like `date`, `ad_id`, `campaign_id`, etc.).
- `age` (STRING): Age demographic targeted/reached.
- `gender` (STRING): Gender demographic targeted/reached.

### 3. `b2s_meta_acquisition_tech_breakdown_by_date_report`

**Purpose**: Provides technical breakdowns for Meta advertising performance, focusing on impression device, platform, and placement.

**Key Features**:
- Segments core acquisition metrics by `impression_device`, `platform_name`, and `platform_position` for Meta campaigns.
- Helps understand which devices, platforms (Facebook, Instagram), and placements (Feed, Stories) perform best.
- Aids in optimizing technical targeting and creative suitability for different environments.

**Row Count**: 693,110 (example)

**Key Columns for Reporting**:
- All key metrics and identifiers from `v1_b2s_all_acquisition_production_report`.
- `impression_device` (STRING): Device type (e.g., mobile, desktop).
- `platform_name` (STRING): Platform where ads were shown (e.g., Facebook, Instagram).
- `platform_position` (STRING): Specific placement on the platform (e.g., Feed, Stories).

### 4. `client_offer_compare_table`

**Purpose**: Facilitates comparative performance analysis of client offers across various pre-defined time periods (e.g., last 3, 7, 30 days and their preceding periods).

**Key Features**:
- Contains aggregated metrics for specific `client_name`, `client_offer`, and potentially `campaign_name`, `ad_network`.
- Uses prefixed column names (e.g., `l3_total_spend`, `xl3_total_spend`, `xxl3_total_spend`) to represent current, previous, and pre-previous period data.
- Includes `date_range_*` fields to clarify the periods being compared.
- Allows for direct calculation of week-over-week, month-over-month, etc., trends.

**Row Count**: 5,480 (example)

**Key Columns for Reporting**:
- `client_name`, `client_offer`, `ad_network`, `campaign_name`: Dimensions for comparison.
- `l3_total_spend`, `l7_total_spend`, `l30_total_spend` (and corresponding `impressions`, `clicks`, `conversions`, `conv_value`): Metrics for the most recent period.
- `xl3_total_spend`, `xl7_total_spend`, `xl30_total_spend` (and corresponding metrics): Metrics for the period prior to the most recent.
- `xxl3_total_spend`, `xxl7_total_spend`, `xxl30_total_spend` (and corresponding metrics): Metrics for the period two times prior.
- `yesterday_total_spend` (and corresponding metrics): Metrics for the immediately preceding day.
- `date_range_3_1`, `date_range_7_1`, etc.: Define the actual date spans for clarity.

### 5. `client_offer_monitor_table`

**Purpose**: A summarized monitoring table for tracking key performance indicators (KPIs) for client offers over standard timeframes (3, 7, 14, 30 days).

**Key Features**:
- Provides a high-level, aggregated view, likely for dashboards or quick checks.
- Contains `l3_total_spend`, `l7_total_spend`, `l14_total_spend`, `l30_total_spend` and corresponding `_total_conversions`.
- Includes `color` and `target` fields, likely used for internal goal tracking and visual cues in dashboards.

**Row Count**: 34 (example)

**Key Columns for Reporting**:
- `client_name`, `client_offer`, `ad_network`: Key dimensions.
- `l3_total_spend`, `l7_total_spend`, `l14_total_spend`, `l30_total_spend`: Spend over various periods.
- `l3_total_conversions`, `l7_total_conversions`, `l14_total_conversions`, `l30_total_conversions`: Conversions over various periods.
- `color`, `target`: For internal status/goal visualization, not typically for calculating core metrics in a standard report but could inform qualitative assessments.

### 6. `media_buyers_table`

**Purpose**: Tracks the performance of individual media buyers, associating them with clients, offers, campaigns, and their respective aggregated metrics.

**Key Features**:
- Links `media_buyer` to `client_name`, `client_offer`, and `campaign_name`/`id`.
- Aggregates `spend` and `conversions` over standard timeframes (3, 7, 14, 30 days) per media buyer.
- Useful for evaluating team member performance and identifying top-performing buyers for specific accounts or strategies.

**Row Count**: 641 (example)

**Key Columns for Reporting**:
- `media_buyer` (STRING): The primary dimension for this table.
- `client_name`, `client_offer`, `campaign_name`: Context for the media buyer's performance.
- `l3_total_spend`, `l7_total_spend`, `l14_total_spend`, `l30_total_spend`: Spend attributed to the buyer.
- `l3_total_conversions`, `l7_total_conversions`, `l14_total_conversions`, `l30_total_conversions`: Conversions attributed to the buyer.

## Insights and Observations from Schema Structure

1.  **Comprehensive Performance Tracking**: The schema is designed for robust, multi-level performance tracking from high-level summaries down to daily ad-level details and specific demographic/technical breakdowns.
2.  **Emphasis on Time-Based Analysis & Trends**: The `client_offer_compare_table` and the `l*_` prefixed columns in several tables highlight a strong focus on trend analysis and performance comparison over time.
3.  **Client-Offer Centricity**: The `client_name` and `client_offer` fields are pervasive, underscoring their importance as core business dimensions.
4.  **Granular Meta Platform Insights**: Dedicated tables for Meta demographic and technical breakdowns indicate that Meta platforms are key advertising channels and that deep optimization within them is a priority.
5.  **Accountability & Team Performance**: The `media_buyers_table` allows for assessing performance at an individual contributor level.
6.  **Data Model for Reporting Blueprint**: This schema directly supports the generation of the `comprehensive_data_driven_report_blueprint.md`, providing the necessary fields for almost all outlined metrics and analyses.
    *   **Strengths:** Strong for overall KPI reporting, channel comparisons, client/offer performance, campaign/ad set/ad breakdowns, demographic/technical segmentation, and trend analysis.
    *   **Conceptual Areas in Blueprint:** "Health Scores" would be a derived calculation based on KPI targets. Deep "Creative Insights" beyond `ad_name` would require linking to a separate creative asset management system or more detailed ad component fields.

## Common Fields Across Tables

These fields serve as common keys or dimensions, facilitating joins and integrated analysis:

- `date` (in time-series tables)
- `client_name`
- `client_offer`
- `advertising_channel` / `ad_network`
- `campaign_name`, `campaign_id`
- `adset_name`, `adset_id`
- `ad_name`, `ad_id`
- `media_buyer`
- Core metrics (`spend`, `impressions`, `clicks`, `conversions`, `conversion_value`, `leads`) are present or aggregated in various forms across tables.

## Clarification on Table Relationships and Data Granularity

-   **`v1_b2s_all_acquisition_production_report`**: This is the most granular daily performance table, typically at the `date`, `ad_id` level. It serves as the primary source for detailed performance metrics.
-   **Breakdown Tables (`b2s_meta_acquisition_demo_breakdown_by_date_report`, `b2s_meta_acquisition_tech_breakdown_by_date_report`)**: These tables take the performance data (conceptually from the main acquisition report for Meta campaigns) and "explode" it across additional dimensions (age/gender or device/platform). Thus, one row in the main report for a Meta ad on a specific day might correspond to multiple rows in these breakdown tables if that ad reached multiple demographic segments or appeared on multiple devices/placements.
-   **Aggregated/Comparative Tables (`client_offer_compare_table`, `client_offer_monitor_table`, `media_buyers_table`)**: These tables contain data that is pre-aggregated over specific time windows (e.g., last 3 days, last 7 days). They are useful for quick summaries, trend analysis, and monitoring without needing to re-aggregate from the most granular daily data for every query.

This structure allows for both deep, flexible analysis from the granular tables and efficient reporting of common summaries and trends from the pre-aggregated tables. 