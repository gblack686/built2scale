# Comprehensive Multi-Channel Performance Report Blueprint
*(Based on schema_summary_20250515_102856.json)*

**Date of Report:** {{Current Date}}
**Reporting Period:** {{Default: Last 7 Days, with comparisons to previous periods where applicable}}

---

## I. Executive Summary

This section provides a high-level overview of advertising performance across all channels, highlighting key achievements, areas for improvement, and strategic recommendations.

### A. Overall Performance Snapshot (Selected Period, e.g., Last 7 Days)
*This data would primarily be aggregated from `v1_b2s_all_acquisition_production_report` or drawn from `client_offer_compare_table` for the relevant period (e.g., `l7_...` fields).*

*   **Total Advertising Spend:** \$[Sum of `spend`]
*   **Total Impressions:** [Sum of `impressions`]
*   **Total Clicks:** [Sum of `clicks`]
*   **Average Click-Through Rate (CTR):** [Calculated: (Total Clicks / Total Impressions) * 100]%
*   **Average Cost Per Click (CPC):** \$[Calculated: Total Spend / Total Clicks]
*   **Total Conversions (Primary Goal):** [Sum of `conversions`]
*   **Average Cost Per Conversion (CPA):** \$[Calculated: Total Spend / Total Conversions]
*   **Total Conversion Value (Revenue):** \$[Sum of `conversion_value`]
*   **Overall Return on Ad Spend (ROAS):** [Calculated: Total Conversion Value / Total Spend]
*   **Total Leads (If applicable):** [Sum of `leads`]
*   **Average Cost Per Lead (CPL):** \$[Calculated: Total Spend / Total Leads]

### B. Key Highlights & Achievements
*   **Top Performing Advertising Channel (by ROAS/Conversion Volume):** [Identify based on `advertising_channel` from `v1_b2s_all_acquisition_production_report`]
*   **Most Profitable Client/Offer (by ROAS/Net Profit if COGS available):** [Identify based on `client_name`, `client_offer` from relevant tables]
*   **Campaign with Highest Improvement (WoW/MoM ROAS/CPA):** [Identify using `client_offer_compare_table` comparing `l7_total_spend` with `xl7_total_spend` etc. for campaigns]
*   **Successful New Launches/Tests (if identifiable via `campaign_name` conventions and recent `date`):**

### C. Performance Trends (vs. Previous Period, e.g., Last 7 Days vs. Prior 7 Days)
*Powered by `client_offer_compare_table` (e.g., `l7_total_spend` vs `xl7_total_spend`).*

*   **Overall Spend:** X% [Up/Down]
*   **Overall Conversions:** Y% [Up/Down]
*   **Overall ROAS:** Z% [Up/Down]
*   **Channel-Specific Trends:**
    *   Facebook: Spend [Up/Down], ROAS [Up/Down]
    *   Google Ads: Spend [Up/Down], ROAS [Up/Down]
    *   Other Channels: ...

### D. Key Observations & Areas for Attention
*   **Observation 1:** e.g., "While overall ROAS remains strong at X, Channel Y is underperforming with a ROAS of Z, significantly below target." (Based on channel breakdown)
*   **Observation 2:** e.g., "Client A's Offer B shows a 30% decline in conversion volume WoW, despite consistent spend, indicating potential creative fatigue or audience saturation." (Based on `client_offer_compare_table`)
*   **Observation 3:** e.g., "High CPA noted on Campaigns X, Y, Z, requiring immediate review." (Based on campaign-level analysis)

### E. Top Recommendations
1.  **Capitalize on Winners:** "Allocate additional budget to top-performing campaigns in [Channel A] and for [Client X / Offer Y] which consistently deliver high ROAS."
2.  **Investigate Underperformers:** "Conduct a deep-dive analysis into campaigns/ad sets in [Channel B] with CPA above \$[Target] to identify optimization opportunities (e.g., targeting, creative, landing page)."
3.  **Creative Refresh & Testing:** "For campaigns showing declining CTR or conversion rates (e.g., Client A Offer B), initiate a creative refresh and A/B test new ad copy and visuals."
4.  **Audience Refinement:** "Review demographic (age, gender) and technical (device, platform) performance breakdowns to identify highly responsive segments for scaling and poorly performing segments for exclusion or bid reduction."

---

## II. Detailed Performance Analysis (Selected Period, e.g., Last 30 Days)

This section breaks down performance by key dimensions to uncover deeper insights.
*Data aggregated from `v1_b2s_all_acquisition_production_report`, `client_offer_compare_table`, `media_buyers_table`.*

### A. Performance by Advertising Channel
| Channel (`advertising_channel`) | Spend | Impressions | Clicks | CTR   | CPC  | Conversions | CPA  | Conv. Value | ROAS | Leads | CPL  |
| :------------------------------ | :---- | :---------- | :----- | :---- | :--- | :---------- | :--- | :---------- | :--- | :---- | :--- |
| Facebook                        |       |             |        |       |      |             |      |             |      |       |      |
| Google Ads                      |       |             |        |       |      |             |      |             |      |       |      |
| (Other Channels)                |       |             |        |       |      |             |      |             |      |       |      |
| **Total**                       |       |             |        |       |      |             |      |             |      |       |      |

### B. Performance by Client & Offer
| Client (`client_name`) | Offer (`client_offer`) | Spend | Conversions | CPA  | Conv. Value | ROAS |
| :--------------------- | :--------------------- | :---- | :---------- | :--- | :---------- | :--- |
| Client A               | Offer 1                |       |             |      |             |      |
| Client A               | Offer 2                |       |             |      |             |      |
| Client B               | Offer 1                |       |             |      |             |      |
| **Total**              |                        |       |             |      |             |      |

### C. Performance by Media Buyer
*Data primarily from `media_buyers_table` or `v1_b2s_all_acquisition_production_report` grouped by `media_buyer`.*
| Media Buyer (`media_buyer`) | Total Spend Managed | Total Conversions Generated | Average ROAS Achieved |
| :-------------------------- | :------------------ | :-------------------------- | :-------------------- |
| Buyer 1                     |                     |                             |                       |
| Buyer 2                     |                     |                             |                       |
| **Total**                   |                     |                             |                       |

### D. Trend Analysis (WoW & MoM using `client_offer_compare_table`)
*This section would feature tables or charts showing week-over-week and month-over-month changes for key metrics like Spend, Conversions, and ROAS, possibly broken down by `client_offer` or `advertising_channel`.*
*   **Example Metric: Overall ROAS**
    *   Last 7 Days: X
    *   Previous 7 Days: Y (Change: Z%)
    *   Last 30 Days: A
    *   Previous 30 Days: B (Change: C%)

---

## III. Campaign Level Analysis (Selected Period, e.g., Last 7 Days)

Detailed breakdown of individual campaign performance.
*Data from `v1_b2s_all_acquisition_production_report` grouped by `campaign_id`, `campaign_name`.*

### A. Top Performing Campaigns (e.g., by ROAS or Conversion Volume)
| Campaign Name (`campaign_name`) | Spend | Impressions | Clicks | CTR  | CPC  | Conversions | CPA  | Conv. Value | ROAS |
| :------------------------------ | :---- | :---------- | :----- | :--- | :--- | :---------- | :--- | :---------- | :--- |
| Campaign Alpha                  |       |             |        |      |      |             |      |             |      |
| Campaign Beta                   |       |             |        |      |      |             |      |             |      |

### B. Lowest Performing Campaigns (e.g., by CPA or low ROAS with significant spend)
| Campaign Name (`campaign_name`) | Spend | Impressions | Clicks | CTR  | CPC  | Conversions | CPA  | Conv. Value | ROAS |
| :------------------------------ | :---- | :---------- | :----- | :--- | :--- | :---------- | :--- | :---------- | :--- |
| Campaign Gamma                  |       |             |        |      |      |             |      |             |      |
| Campaign Delta                  |       |             |        |      |      |             |      |             |      |

### C. Campaign Health & Status Overview (Conceptual)
*This section would categorize campaigns based on predefined KPI targets (e.g., ROAS target > 3, CPA target < $50). The schema does not provide a direct 'health score'. This would be a derived analysis.*
*   **Healthy Campaigns (Meeting/Exceeding Targets):** [List Campaigns]
*   **Needs Optimization (Slightly Below Targets):** [List Campaigns]
*   **Critical Attention (Significantly Below Targets / High Spend, Low Return):** [List Campaigns]
*   **Active & Testing (New campaigns - `campaign_delivery` status if useful):** [List Campaigns]

### D. Observations & Campaign-Specific Recommendations
*   **Observation:** "Campaign Alpha (ROAS: X) continues to be a top performer, primarily driven by Ad Set A1. Consider budget scaling."
*   **Recommendation:** "For Campaign Gamma (CPA: Y), review ad set targeting and creative effectiveness as CTR is Z% below average."

---

## IV. Ad Set / Ad Group Level Analysis (Selected Period, e.g., Last 7 Days)

Performance breakdown at the ad set/ad group level.
*Data from `v1_b2s_all_acquisition_production_report` grouped by `adset_id`, `adset_name` (within campaigns).*

### A. Top Performing Ad Sets (e.g., by Conversions, CPA within key campaigns)
| Campaign Name | Ad Set Name (`adset_name`) | Spend | Impressions | Clicks | CTR  | Conversions | CPA  | Conv. Value | ROAS |
| :------------ | :------------------------- | :---- | :---------- | :----- | :--- | :---------- | :--- | :---------- | :--- |
| Campaign Alpha| Ad Set A1                  |       |             |        |      |             |      |             |      |
| Campaign Beta | Ad Set B2                  |       |             |        |      |             |      |             |      |

### B. Ad Set Delivery & Pacing
*Analyze `adset_delivery` status if it provides insights into learning phase, budget exhaustion, etc.*

### C. Observations & Ad Set Specific Recommendations
*   **Observation:** "In Campaign Alpha, Ad Set A1 focusing on [Targeting detail if in name] shows a CPA 50% lower than Ad Set A2."
*   **Recommendation:** "Pause Ad Set Gamma-3 due to zero conversions in the last 7 days despite \$X spend. Re-evaluate audience or creative."

---

## V. Ad Level Analysis (Selected Period, e.g., Last 7 Days)

Performance of individual ads.
*Data from `v1_b2s_all_acquisition_production_report` grouped by `ad_id`, `ad_name` (within ad sets).*

### A. Top Performing Ads (e.g., by CTR, Conversion Rate, ROAS within key ad sets)
| Ad Set Name | Ad Name (`ad_name`) | Spend | Impressions | Clicks | CTR  | Conversions | CPA  | Conv. Value | ROAS |
| :---------- | :------------------ | :---- | :---------- | :----- | :--- | :---------- | :--- | :---------- | :--- |
| Ad Set A1   | Ad Creative X       |       |             |        |      |             |      |             |      |
| Ad Set B2   | Ad Creative Y       |       |             |        |      |             |      |             |      |

### B. Ad Delivery & Fatigue Indicators
*Analyze `ad_delivery`. Look for high frequency (if available - not directly in schema, but impressions/reach could be a proxy if reach is at ad level) or declining CTR over time for long-running ads.*

### C. Creative Insights & Recommendations (Conceptual)
*While the schema provides `ad_name` and `ad_id`, it doesn't detail creative components (e.g., headline, body text, image/video asset). This section would be more robust if such data were available and linkable.*
*   **Observation:** "Ads with 'Discount' in `ad_name` within [Campaign Z] have a 20% higher CTR." (Hypothetical based on naming conventions)
*   **Observation:** "Top performing ads consistently feature [theme identifiable from `ad_name` or linked creative data]."
*   **Recommendation:** "Test new ad variations for Ad Set Gamma-3, focusing on benefit-driven copy as seen in top performer Ad Creative X."
*   **Recommendation:** "If specific creative elements (e.g., image styles, video lengths, headline types) were tracked, further analysis could determine which components drive the best performance, similar to a Creative Strategy Report."

---

## VI. Audience & Technical Breakdown Insights (Selected Period, e.g., Last 30 Days)

Understanding performance across different audience segments and technical factors.

### A. Demographic Performance
*Data from `b2s_meta_acquisition_demo_breakdown_by_date_report`.*
| Age (`age`) | Gender (`gender`) | Spend | Impressions | Clicks | CTR  | Conversions | CPA  | Conv. Value | ROAS |
| :---------- | :---------------- | :---- | :---------- | :----- | :--- | :---------- | :--- | :---------- | :--- |
| 18-24       | Male              |       |             |        |      |             |      |             |      |
| 18-24       | Female            |       |             |        |      |             |      |             |      |
| 25-34       | Male              |       |             |        |      |             |      |             |      |
| ...         | ...               |       |             |        |      |             |      |             |      |

### B. Technical Performance
*Data from `b2s_meta_acquisition_tech_breakdown_by_date_report`.*
*   **By Impression Device (`impression_device`):**
    | Device  | Spend | Conversions | CPA  | ROAS |
    | :------ | :---- | :---------- | :--- | :--- |
    | Mobile  |       |             |      |      |
    | Desktop |       |             |      |      |
    | Tablet  |       |             |      |      |
*   **By Platform (`platform_name`, `platform_position` - if granular enough):**
    | Platform          | Position          | Spend | Conversions | CPA  | ROAS |
    | :---------------- | :---------------- | :---- | :---------- | :--- | :--- |
    | Facebook          | Feed              |       |             |      |      |
    | Instagram         | Stories           |       |             |      |      |
    | Google Search     | Top               |       |             |      |      |

### C. Observations & Targeting Recommendations
*   **Observation:** "The 25-34 Male segment shows the highest ROAS (X), while the 55-64 Female segment has the highest CPA (Y)."
*   **Observation:** "Desktop users convert at a 15% higher rate than mobile users for [Client A Offer B], though mobile drives 70% of clicks."
*   **Recommendation:** "Consider bid adjustments or dedicated campaigns for the 25-34 Male segment. Investigate landing page experience on mobile for Client A Offer B."
*   **Recommendation:** "If specific `platform_position` (e.g., Instagram Stories) is significantly underperforming, review creative suitability or consider excluding."

---

## VII. Funnel Performance Analysis (Conceptual - Based on Available Metrics)

Analyzing the flow if `leads` and `registrations` represent distinct funnel stages leading to `conversions`.
*Data from `v1_b2s_all_acquisition_production_report`.*

### A. Lead & Registration Flow
| Metric                     | Volume |
| :------------------------- | :----- |
| Total Clicks               |        |
| Total Leads (`leads`)      |        |
| Total Registrations (`registrations`)|        |
| Total Conversions (`conversions`)|        |

### B. Conversion Rates Between Stages (Calculated)
*   Click-to-Lead Rate: (Total Leads / Total Clicks) %
*   Lead-to-Registration Rate: (Total Registrations / Total Leads) %
*   Registration-to-Conversion Rate: (Total Conversions / Total Registrations) %
*   Overall Click-to-Conversion Rate: (Total Conversions / Total Clicks) %

### C. Observations on Funnel Bottlenecks
*   **Observation:** "A significant drop-off is observed between Leads and Registrations (X% rate), suggesting the registration step may have friction."
*   **Recommendation:** "Review the lead nurturing process and the registration page/form for potential improvements to increase the Lead-to-Registration rate."

---

## VIII. Key Learnings & Action Plan

Summary of critical findings and a proposed plan for the upcoming period.

### A. Summary of Key Learnings
1.  Learning 1: e.g., "[Channel X] is the most efficient for [Objective Y]."
2.  Learning 2: e.g., "Audiences segmented by [Age/Gender/Device] perform best for [Client/Offer Z]."
3.  Learning 3: e.g., "Campaigns with [Specific Naming Convention/Theme] are underperforming."

### B. Proposed Action Plan (Next 7-14 Days)
1.  **Budget Adjustments:**
    *   Increase budget for [Top Campaign/Ad Set 1] by X%.
    *   Pause or significantly reduce budget for [Underperforming Campaign 1].
2.  **Optimization Tasks:**
    *   Refine targeting for [Campaign X Ad Set Y] based on demographic performance.
    *   A/B test new ad creatives (headline/visuals) for [Campaign Z Ad Set W].
    *   Review landing page for [Offer Q] to improve Lead-to-Registration rate.
3.  **New Tests/Initiatives:**
    *   Launch a new campaign on [Platform M] targeting [Audience Segment N] for [Offer P].
4.  **Monitoring & Reporting:**
    *   Closely monitor CPA and ROAS for adjusted campaigns daily.
    *   Track impact of new creatives/tests.

---

**Glossary (Optional):**
*   **ROAS:** Return on Ad Spend
*   **CPA:** Cost Per Acquisition/Conversion
*   **CPC:** Cost Per Click
*   **CTR:** Click-Through Rate
*   **CPL:** Cost Per Lead


</rewritten_file> 