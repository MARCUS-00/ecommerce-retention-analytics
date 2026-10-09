# Final DAX measure list — ecommerce_analytics

Source of truth: the `_Measures` table of the saved model (`ecommerce_retention_dashboard_final.pbix`; `ecommerce_retention_dashboard.pbix` is an identical copy). Reference values from the project documents are not stored in the model.

**Status after the final polish pass.** No measure, calculated column or relationship was changed (43 measures, unchanged). The pass changed presentation only:
- The file's default format-string locale is now English (United States), so the existing format strings show `R$15,419,773.75`, `96,478` and `R$159.83` instead of Indian digit grouping.
- The reviewed-orders table uses shorter column display names (Reviewed (n), Avg score, Median score, 1–2★ share). The measures keep their own names.
- Alt text, tab order and text-box wording were updated.

**Method notes moved out of the page footers**
- RFM scores run from 1 to 5. Recency is SQL `NTILE(5)` over the last-order date; frequency and spend follow the repository's query 15, unchanged. SQL places ties at quintile boundaries arbitrarily, so segment counts can differ slightly from notebook 02, which uses `method='first'`.
- The payment visuals use the query 05 population: all payment records, in any order status.

## Revenue

### Total Revenue

```dax
Total Revenue =
SUM ( vw_sales[line_revenue] )
```
Format: `\R\$#,0.00`

### Total Orders

```dax
Total Orders =
DISTINCTCOUNT ( vw_sales[order_id] )
```
Format: `#,0`

### AOV

```dax
AOV =
DIVIDE ( [Total Revenue], [Total Orders] )
```
Format: `\R\$#,0.00`

### Revenue MoM %

```dax
Revenue MoM % =
VAR CurrentRevenue = [Total Revenue]
VAR PriorRevenue =
    CALCULATE ( [Total Revenue], DATEADD ( dim_date[date], -1, MONTH ) )
RETURN
    DIVIDE ( CurrentRevenue - PriorRevenue, PriorRevenue )
```
Format: `0.0%;-0.0%;0.0%`

### Latest Month Revenue MoM %

```dax
Latest Month Revenue MoM % =
VAR _d = MAX ( vw_sales[order_date] )
VAR _ms = DATE ( YEAR ( _d ), MONTH ( _d ), 1 )
VAR _cur = CALCULATE ( [Total Revenue], dim_date[month_start] = _ms )
VAR _prev = CALCULATE ( [Total Revenue], REMOVEFILTERS ( dim_date ), dim_date[month_start] = EDATE ( _ms, -1 ) )
RETURN
    DIVIDE ( _cur - _prev, _prev )
```
Format: `0.0%;-0.0%;0.0%`

### Category Rank

```dax
Category Rank =
RANKX (
    ALL ( vw_sales[product_category_name_english] ),
    CALCULATE ( [Total Revenue], REMOVEFILTERS ( dim_date[month_start] ) ),
    ,
    DESC,
    DENSE
)
```
Format: `0`

### Top Category Revenue

```dax
Top Category Revenue =
IF ( [Category Rank] <= 15, [Total Revenue] )
```
Format: `\R\$#,0.00`

### Category Cumulative Share %

```dax
Category Cumulative Share % =
VAR _rank = [Category Rank]
VAR _tot = CALCULATE ( [Total Revenue], REMOVEFILTERS ( vw_sales[product_category_name_english] ) )
RETURN
    IF (
        _rank <= 15,
        DIVIDE (
            SUMX ( FILTER ( ALL ( vw_sales[product_category_name_english] ), [Category Rank] <= _rank ), [Total Revenue] ),
            _tot
        )
    )
```
Format: `0.0%;-0.0%;0.0%`

### Top 5 Category Share %

```dax
Top 5 Category Share % =
VAR _t = TOPN ( 5, ALL ( vw_sales[product_category_name_english] ), [Total Revenue], DESC )
VAR _tot = CALCULATE ( [Total Revenue], REMOVEFILTERS ( vw_sales[product_category_name_english] ) )
RETURN
    DIVIDE ( SUMX ( _t, [Total Revenue] ), _tot )
```
Format: `0.00%;-0.00%;0.00%`

### Seller Rank

```dax
Seller Rank =
RANKX ( ALL ( vw_sales[seller_id], vw_sales[seller_label] ), [Total Revenue], , DESC, DENSE )
```
Format: `0`

### Top 10 Seller Revenue

```dax
Top 10 Seller Revenue =
IF ( [Seller Rank] <= 10, [Total Revenue] )
```
Format: `\R\$#,0.00`

### Top 10 Seller Share %

```dax
Top 10 Seller Share % =
VAR _t = TOPN ( 10, ALL ( vw_sales[seller_id] ), [Total Revenue], DESC )
VAR _tot = CALCULATE ( [Total Revenue], REMOVEFILTERS ( vw_sales[seller_id] ) )
RETURN
    DIVIDE ( SUMX ( _t, [Total Revenue] ), _tot )
```
Format: `0.00%;-0.00%;0.00%`


## Payments (all payment records)

### Payment Records

```dax
Payment Records =
COUNTROWS ( order_payments )
```
Format: `#,0`

### Payment Record Share %

```dax
Payment Record Share % =
DIVIDE ( COUNTROWS ( order_payments ), CALCULATE ( COUNTROWS ( order_payments ), ALL ( order_payments ) ) )
```
Format: `0.00%;-0.00%;0.00%`

### Avg Installments

```dax
Avg Installments =
AVERAGE ( order_payments[payment_installments] )
```
Format: `0.00`

### Total Payment Value

```dax
Total Payment Value =
SUM ( order_payments[payment_value] )
```
Format: `\R\$#,0.00`


## Customers & Retention

### Customers

```dax
Customers =
DISTINCTCOUNT ( vw_customers[customer_unique_id] )
```
Format: `#,0`

### Repeat Customers

```dax
Repeat Customers =
CALCULATE ( DISTINCTCOUNT ( vw_customers[customer_unique_id] ), vw_customers[is_repeat] = TRUE () )
```
Format: `#,0`

### One-Time Customers

```dax
One-Time Customers =
[Customers] - [Repeat Customers]
```
Format: `#,0`

### Repeat Cust %

```dax
Repeat Cust % =
DIVIDE (
    CALCULATE (
        DISTINCTCOUNT ( vw_customers[customer_unique_id] ),
        vw_customers[is_repeat] = TRUE ()
    ),
    DISTINCTCOUNT ( vw_customers[customer_unique_id] )
)
```
Format: `0.00%;-0.00%;0.00%`

### Cohort Active Customers

```dax
Cohort Active Customers =
SUM ( cohort_retention[active_customers] )
```
Format: `#,0`

### Retention %

```dax
Retention % =
DIVIDE ( SUM ( cohort_retention[active_customers] ), CALCULATE ( SUM ( cohort_retention[active_customers] ), cohort_retention[month_offset] = 0 ) )
```
Format: `0.0%;-0.0%;0.0%`

### Month-1 Retention % (weighted)

```dax
Month-1 Retention % (weighted) =
VAR _lastCohort = MAX ( cohort_retention[cohort] )
VAR _m1 = CALCULATE ( SUM ( cohort_retention[active_customers] ), cohort_retention[month_offset] = 1, cohort_retention[cohort] < _lastCohort )
VAR _m0 = CALCULATE ( SUM ( cohort_retention[active_customers] ), cohort_retention[month_offset] = 0, cohort_retention[cohort] < _lastCohort )
RETURN
    DIVIDE ( _m1, _m0 )
```
Format: `0.00%;-0.00%;0.00%`

### RFM Customers

```dax
RFM Customers =
SUM ( rfm_grid[customers] )
```
Format: `#,0`

### RFM Revenue

```dax
RFM Revenue =
SUM ( rfm_grid[segment_revenue] )
```
Format: `\R\$#,0.00`

### RFM Customer Share %

```dax
RFM Customer Share % =
DIVIDE ( SUM ( rfm_grid[customers] ), CALCULATE ( SUM ( rfm_grid[customers] ), ALL ( rfm_grid ) ) )
```
Format: `0.00%;-0.00%;0.00%`

### RFM Revenue Share %

```dax
RFM Revenue Share % =
DIVIDE ( SUM ( rfm_grid[segment_revenue] ), CALCULATE ( SUM ( rfm_grid[segment_revenue] ), ALL ( rfm_grid ) ) )
```
Format: `0.00%;-0.00%;0.00%`


## Operations & Satisfaction

### Delivered Orders

```dax
Delivered Orders =
COUNTROWS ( vw_orders )
```
Format: `#,0`

### Late Orders

```dax
Late Orders =
CALCULATE ( COUNTROWS ( vw_orders ), vw_orders[is_late] = TRUE () )
```
Format: `#,0`

### Late Delivery %

```dax
Late Delivery % =
DIVIDE (
    CALCULATE ( COUNTROWS ( vw_orders ), vw_orders[is_late] = TRUE () ),
    COUNTROWS ( vw_orders )
)
```
Format: `0.00%;-0.00%;0.00%`

### Median Delivery Days

```dax
Median Delivery Days =
MEDIAN ( vw_orders[delivery_days] )
```
Format: `0.0`

### Avg Review Score

```dax
Avg Review Score =
AVERAGE ( vw_orders[review_score] )
```
Format: `0.00`

### Median Review Score

```dax
Median Review Score =
MEDIAN ( vw_orders[review_score] )
```
Format: `0.0`

### Reviewed Orders

```dax
Reviewed Orders =
CALCULATE ( COUNTROWS ( vw_orders ), NOT ISBLANK ( vw_orders[review_score] ) )
```
Format: `#,0`

### Pct 1-2 Star

```dax
Pct 1-2 Star =
DIVIDE (
    CALCULATE ( COUNTROWS ( vw_orders ), vw_orders[review_score] IN { 1, 2 } ),
    CALCULATE ( COUNTROWS ( vw_orders ), NOT ISBLANK ( vw_orders[review_score] ) )
)
```
Format: `0.00%;-0.00%;0.00%`

### Orders With Delivery Time

```dax
Orders With Delivery Time =
CALCULATE ( COUNTROWS ( vw_orders ), NOT ISBLANK ( vw_orders[delivery_days] ) )
```
Format: `#,0`


## Forecast (all placed orders)

### Actual (last 90 d)

```dax
Actual (last 90 d) =
SUM ( forecast_chart[actual] )
```
Format: `#,0`

### Forecast

```dax
Forecast =
SUM ( forecast_chart[forecast] )
```
Format: `#,0.0`

### Lower 95%

```dax
Lower 95% =
SUM ( forecast_chart[lower] )
```
Format: `#,0.0`

### Upper 95%

```dax
Upper 95% =
SUM ( forecast_chart[upper] )
```
Format: `#,0.0`

### Forecast Total (28 days)

```dax
Forecast Total (28 days) =
SUM ( forecast_28d[forecast] )
```
Format: `#,0`

### Forecast Lower Sum

```dax
Forecast Lower Sum =
SUM ( forecast_28d[lower] )
```
Format: `#,0`

### Forecast Upper Sum

```dax
Forecast Upper Sum =
SUM ( forecast_28d[upper] )
```
Format: `#,0`

## Calculated columns and calculated table

### vw_orders[delivery_status] (calculated column) — corrected in final QA

```dax
delivery_status =
IF (
    ISBLANK ( vw_orders[is_late] ),
    "Unknown (no delivery date)",
    IF ( vw_orders[is_late] = TRUE (), "Late", "On time" )
)
```
The first build used `IF ( is_late = TRUE, "Late", IF ( is_late = FALSE, "On time", "Unknown" ) )`. In DAX, `BLANK() = FALSE()` evaluates to TRUE, so the 8 delivered orders whose `is_late` is NULL (no delivered-customer date, so lateness is undefined) were classified as "On time". That is the cause of the 88,171 vs 88,163 discrepancy (see BUILD_QA_REPORT.md). The review-score chart and the 1-2 star share chart additionally carry a visual-level filter `delivery_status in {Late, On time}` so they compare only orders with a defined lateness; the reviewed-orders table intentionally shows the "Unknown" row (8 orders) so totals reconcile (95,832 = 95,824 + 8).

### Other model objects
- `dim_date[month_start]` (calculated column): first day of month; used for the monthly axes, `Category Rank` and `Latest Month Revenue MoM %`.
- `forecast_chart` (DAX calculated table): the last 90 days of actual daily placed-order counts before the forecast start plus the 28 forecast rows (forecast, lower, upper); not related to any other table, so the date/state slicers cannot affect it.

## Notes on blank / divide-by-zero handling
All ratio measures use `DIVIDE`. `Pct 1-2 Star` uses `IN { 1, 2 }` and a non-blank denominator (the spec's `<= 2` counted BLANK as 0). `Late Orders` / `Late Delivery %` use `is_late = TRUE ()` so NULL rows are never counted as late, but they remain in the `COUNTROWS ( vw_orders )` denominator (see "Reference validation" in BUILD_QA_REPORT.md; the result, 7,826 late orders and 8.11 %, matches the raw data).

## Static statements on the report that are not measures
These were checked against the notebooks and the raw data. They do not update on refresh.
- Page 4, reviewed-orders commentary: Mann–Whitney U, one-sided (late < on-time), notebook 03 — n = 7,661 late vs 88,163 on-time reviewed delivered orders, U = 150,706,850.5, p < 0.001 on the dashboard (the notebook printed 0.000e+00, a floating-point underflow; see the p-value note in BUILD_QA_REPORT.md); medians 2 vs 5; 1–2★ share 54.1 % vs 9.2 %.
- Page 4, forecast note: seasonal-naive against Holt-Winters in a 6-fold walk-forward backtest, mean WAPE 0.2308 against 0.2310 (notebook 04). The lower and upper cards are sums of daily bounds, not a 28-day interval.
- Page 3: "roughly 97 % of customers buy once" (live: 90,557 of 93,358 = 97.0 %).
