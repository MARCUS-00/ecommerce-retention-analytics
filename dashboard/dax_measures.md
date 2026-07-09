# DAX Measures

Complex logic (population filters, `is_late`, `is_repeat`, `line_revenue`, `review_score`
join) is precomputed in `sql/04_dashboard_views/*.sql`. DAX stays minimal - simple
aggregations over those views, per MASTER_DOC section 15's feeding-layer rule. Every measure
below references only columns that exist in the views built by `make views`
(verified against the live schema, not assumed).

## Revenue (Executive Overview, Sales Deep-Dive)

```dax
Total Revenue = SUM ( vw_sales[line_revenue] )

Total Orders = DISTINCTCOUNT ( vw_sales[order_id] )

AOV = DIVIDE ( [Total Revenue], [Total Orders] )
```

## Operations & Satisfaction

```dax
Late Delivery % =
DIVIDE (
    CALCULATE ( COUNTROWS ( vw_orders ), vw_orders[is_late] = TRUE () ),
    COUNTROWS ( vw_orders )
)

Median Delivery Days = MEDIAN ( vw_orders[delivery_days] )

Avg Review Score = AVERAGE ( vw_orders[review_score] )

Pct 1-2 Star =
DIVIDE (
    CALCULATE ( COUNTROWS ( vw_orders ), vw_orders[review_score] <= 2 ),
    CALCULATE ( COUNTROWS ( vw_orders ), NOT ISBLANK ( vw_orders[review_score] ) )
)
```

## Customers & Retention

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

## Forecast (Operations page, forecast band)

`analytics.forecast_28d` (date, forecast, lower, upper) is imported directly - no DAX needed,
plot `forecast`/`lower`/`upper` as three line/area series against `vw_daily_orders[orders]`
on a shared date axis.

## Time intelligence (MoM growth, Executive Overview)

Requires `dim_date` marked as the model's date table (Mark as Date Table, using `dim_date[date]`),
related to `vw_sales[order_date]` - the `DATE` column, not `order_purchase_timestamp`
(`TIMESTAMP`); relating to the timestamp column silently matches zero rows (see `BUILD_SPEC.md`).

```dax
Revenue MoM % =
VAR CurrentRevenue = [Total Revenue]
VAR PriorRevenue =
    CALCULATE ( [Total Revenue], DATEADD ( dim_date[date], -1, MONTH ) )
RETURN
    DIVIDE ( CurrentRevenue - PriorRevenue, PriorRevenue )
```

## Reference values (from the live schema, for build-time sanity checks - not dashboard output)

Computed once against the real local database, `dashboard/BUILD_SPEC.md` has the full list;
spot values here so a builder can sanity-check the model wires up correctly:
`Total Revenue` ≈ 15,419,773.75 · `Late Delivery %` ≈ 8.1% · `Repeat Cust %` ≈ 3.0%.
