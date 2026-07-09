# Architecture

## Pipeline diagram (MASTER_DOC section 5)

```
Kaggle CSVs (data/raw, gitignored)
      | src/ingest.py - loads verbatim, no cleaning
      v
stg.* (raw mirror, all TEXT)
      | src/validate.py - INPUT data-quality checks (blocking + logged)
      | sql/02_transform/*.sql - typed, deduplicated, derived columns
      v
analytics.* (star schema) - facts, dims, typed reviews/payments
      | src/validate.py - OUTPUT checks: reconcile counts, orphan FKs, revenue tie-out
      +--> sql/03_analysis/ - 18 business queries (+ saved outputs)
      +--> notebooks/01-03 - EDA, cohorts/RFM, statistical test
      +--> notebooks/04 - forecast -> analytics.forecast_28d
      +--> sql/04_dashboard_views/ -> Power BI (4 pages) -> executive memo
```

Two environments only: local (Docker Postgres, real Kaggle data) and CI (GitHub Actions
service Postgres, synthetic fixtures from `tests/fixtures/generate_fixtures.py` - see
`.github/workflows/ci.yml`).

## Why a star schema, not one flat table

`stg.*` mirrors the 9 source CSVs verbatim (all `TEXT`, no cleaning) so ingest is trivially
idempotent and every anomaly downstream is traceable to an unmodified source row. `analytics.*`
is a conventional star: `fact_orders` and `fact_order_items` at the center, `dim_customers` /
`dim_products` / `dim_sellers` / `dim_date` around them, `order_payments` and `order_reviews`
as typed side tables joined at query time (grain doesn't match the order fact 1:1, so they
aren't dimension-joined facts). This mirrors how real analytics teams separate "raw" from
"modeled" and gives standard interview vocabulary (staging layer, grain, star schema) - a flat
single table would hide the grain mismatches (one order has many items, many payments,
sometimes many reviews) that are exactly what makes this dataset non-trivial.

## The `customer_id` vs. `customer_unique_id` trap

`stg.customers` (and therefore `analytics.dim_customers`) is **order-scoped**: `customer_id`
is unique per *order*, not per person. The actual person key is `customer_unique_id`. Every
retention, repeat-purchase, and RFM calculation in this repo joins through
`customer_unique_id`, never `customer_id` - getting this backwards makes repeat-purchase rate
read as ~0% (every `customer_id` looks like a first-time buyer by construction). See
`sql/03_analysis/12_cohort_retention_matrix.sql`, `13_repeat_purchase_rate.sql`, and
`14_rfm_customer_scores.sql` for the pattern; `analytics.dim_customers`'s two ID columns are
kept side by side specifically so this join is explicit at every use site, not hidden behind
a view that silently picks one.

## Revenue definition (MASTER_DOC section 11, query D)

Revenue = item `price` + `freight_value`, on **delivered** orders. Reconciled against
`order_payments`: 303 of 99,441 orders (0.30%) show a >0.01 difference between summed item
total and summed payment total (`sql/03_analysis/16_items_vs_payments_reconciliation.sql`) -
expected from vouchers, split/installment payments, and cancellation edge cases, not a data
error. `analytics.fact_order_items` total item revenue matches `stg.order_items`'s total
exactly (15,843,553.24, both sides - `src/validate.py`'s `_check_revenue_tie_out`, blocking),
so the typing/transform step introduces zero revenue drift; the 0.30% mismatch is entirely a
source-data phenomenon between items and payments, not an ETL bug.

## Population rule: delivered vs. all placed

Two deliberately different populations are used, never mixed silently (MASTER_DOC section
11): revenue, retention, repeat-rate, and RFM are computed on **delivered** orders only
(`order_status = 'delivered'`); the demand forecast (`notebooks/04_demand_forecast.ipynb`) uses
**all placed** orders, because ops must plan capacity for every order regardless of eventual
status. `sql/04_dashboard_views/04_vw_daily_orders.sql` is the only view built on the
all-placed population; every other view filters to delivered.

## Dedup decisions (MASTER_DOC section 8)

- **`order_reviews`**: source can hold multiple reviews per order (confirmed: 547 orders have
  >1 review, 789 `review_id` values repeat across rows - `sql/03_analysis/17_duplicate_review_count.sql`).
  Rule: keep the latest by `review_answer_timestamp`
  (`sql/02_transform/07_order_reviews.sql`, `DISTINCT ON (order_id) ... ORDER BY order_id,
  review_answer_timestamp DESC, review_id`). Reconciled: `analytics.order_reviews` has exactly
  `COUNT(DISTINCT order_id)` rows from staging (98,673 - `src/validate.py`'s
  `_check_row_reconciliation`, blocking).
- **`geolocation`**: source has many rows per zip prefix (1,000,163 rows, 19,015 distinct
  prefixes). Rule: average `lat`/`lng`, take the most common (`MODE()`) city/state label per
  prefix (`sql/02_transform/08_geolocation.sql`). Reconciled the same way as reviews.

## Stable window for trend/forecast claims (MASTER_DOC section 14)

Derived empirically in `notebooks/01_eda.ipynb` by inspecting daily order volume directly, not
assumed: **2017-01-05 to 2018-08-22** (595 days). Excludes a sparse, gappy 2016 ramp (real gap
days, including 2017-01-01 through 01-04's New Year zero-order stretch) and a continuously
decaying tail from 2018-08-23 onward (a data-collection cutoff, not a demand drop). Verified
zero gap days inside the window. Reused verbatim by the forecast's walk-forward backtest -
never re-derived.

## Temporal anomalies (left as-is in source, not silently fixed)

Quantified in `src/validate.py` (Phase 2/3) and `sql/03_analysis/18_temporal_violation_count.sql`:
1,359 orders show `order_delivered_carrier_date < order_approved_at`; 23 show
`order_delivered_customer_date < order_delivered_carrier_date`; 6 canceled orders carry a
non-null delivery date. All are logged anomalies (not blocking), kept verbatim in
`analytics.fact_orders` since "fixing" them would fabricate data the source doesn't support.

## Indexes (MASTER_DOC section 8)

Primary keys on all natural id columns (`sql/02_transform/*.sql`, `ALTER TABLE ... ADD PRIMARY
KEY`) plus explicit foreign keys between every fact/dim pair - meaning a referential-integrity
violation would fail the transform itself, not just get reported after the fact. B-tree
indexes on `fact_orders(order_purchase_timestamp)`, `fact_order_items(order_id)`, and
`fact_order_items(product_id)` - the columns every join and date-range filter in
`sql/03_analysis/*.sql` actually uses.
