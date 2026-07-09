# Data Dictionary

Every table/view and column below is confirmed against the live schema
(`information_schema.columns`), not written from memory. See `docs/architecture.md` for the
grain/dedup/population decisions this dictionary references.

## Staging (`stg.*`) — verbatim TEXT mirror of the 9 source CSVs, no cleaning

All columns are `TEXT`. Row counts match each source CSV's data-row count exactly (verified
two independent ways in Phase 1 - quote-aware CSV parsing and a live `COUNT(*)` query).

| Table | Grain | Columns |
|---|---|---|
| `stg.customers` | 1 row per order-scoped customer | `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state` |
| `stg.geolocation` | many rows per zip prefix (duplicated in source) | `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state` |
| `stg.order_items` | 1 row per item line | `order_id`, `order_item_id`, `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value` |
| `stg.order_payments` | 1 row per payment record (multiple per order legit) | `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value` |
| `stg.order_reviews` | 1+ rows per order (dedup happens downstream) | `review_id`, `order_id`, `review_score`, `review_comment_title`, `review_comment_message`, `review_creation_date`, `review_answer_timestamp` |
| `stg.orders` | 1 row per order | `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date` |
| `stg.products` | 1 row per product | `product_id`, `product_category_name`, `product_name_lenght`, `product_description_lenght`, `product_photos_qty`, `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm` |
| `stg.sellers` | 1 row per seller | `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state` |
| `stg.product_category_translation` | 1 row per category | `product_category_name`, `product_category_name_english` |

## Analytics star schema (`analytics.*`)

| Table | Grain | Notable columns |
|---|---|---|
| `dim_customers` | 1 row per `customer_id` (**order-scoped** - `customer_unique_id` is the person key, see architecture.md) | same columns as `stg.customers` |
| `dim_products` | 1 row per product | `product_category_name_english` (falls back to the Portuguese name for 610 uncategorized products - `COALESCE`), typed length/weight/dimension columns |
| `dim_sellers` | 1 row per seller | zip/city/state |
| `dim_date` | 1 row per calendar day, 2016-01-01 to 2018-12-31 | `date` (PK), `year`, `month`, `weekday`, `is_weekend` |
| `fact_orders` | 1 row per order (PK `order_id`) | `delivery_days` (derived, `int`), `is_late` (derived `boolean`, NULL where lateness can't be determined - not coerced to `false`) |
| `fact_order_items` | 1 row per item line (PK `order_id, order_item_id`) | `price`, `freight_value` (`numeric`) |
| `order_payments` | 1 row per payment record (PK `order_id, payment_sequential`) | multiple rows per order are legitimate |
| `order_reviews` | 1 row per order **after dedup** (PK `order_id`) | kept latest by `review_answer_timestamp` (547 duplicate orders resolved this way) |
| `geolocation` | 1 row per zip prefix **after dedup** (PK `zip_code_prefix`) | `avg_lat`/`avg_lng` (averaged), `city`/`state` (`MODE()`, most common) |
| `forecast_28d` | 1 row per forecast day (PK `date`) | `forecast`, `lower`, `upper` - written only by `notebooks/04_demand_forecast.ipynb` |

## Dashboard feeding views (`analytics.vw_*`, `sql/04_dashboard_views/`)

| View | Population | Notable columns |
|---|---|---|
| `vw_sales` | delivered order-item lines | `line_revenue` = `price + freight_value` |
| `vw_orders` | delivered orders | `delivery_days`, `is_late`, `review_score` (`LEFT JOIN` - not every order has one) |
| `vw_customers` | person grain (`customer_unique_id`), delivered orders | `is_repeat` (`delivered_orders >= 2`) |
| `vw_daily_orders` | **all placed** orders (any status) - the forecast population | `order_date`, `orders` |

## Anomaly log (MASTER_DOC section 10.2 format: date | table | check | count | decision)

All entries below were computed by this repository's validation suite (`src/validate.py`) and
verified against the live data - not estimated.

| Date | Table | Check | Count | Decision |
|---|---|---|---|---|
| 2026-07-05 | `stg.order_reviews` | Embedded newlines inside quoted `review_comment_message` fields | - | `wc -l`-style line counting overcounts this file; use quote-aware CSV parsing (pandas/csv module), confirmed in Phase 1 |
| 2026-07-05 | `orders` | `delivered_carrier_date < approved_at` | 1,359 | Source data quirk; left as-is (verbatim staging mirror) |
| 2026-07-05 | `orders` | `delivered_customer_date < delivered_carrier_date` | 23 | Impossible ordering in source; left as-is |
| 2026-07-05 | `orders` | Canceled order with a non-null `delivered_customer_date` | 6 | Minor, rare; no action |
| 2026-07-05 | `orders` | `order_approved_at` null rate | 160 (0.16%) | Orders likely abandoned before payment approval; expected |
| 2026-07-05 | `orders` | `order_delivered_customer_date` null rate | 2,965 (2.98%) | Matches non-delivered `order_status` counts almost exactly; expected |
| 2026-07-05 | `order_reviews` | `review_comment_title` null rate | 87,656 (88.34%) | Optional field; most customers skip it |
| 2026-07-05 | `order_reviews` | `review_comment_message` null rate | 58,247 (58.70%) | Optional field; most customers leave no comment |
| 2026-07-05 | `order_reviews` | Duplicate `review_id` values | 789 | `review_id` is not a reliable standalone dedup key |
| 2026-07-05 | `order_reviews` | Orders with >1 review | 547 | Legitimate source behavior; Phase 3 dedups by latest `review_answer_timestamp` |
| 2026-07-05 | `products` | `product_category_name` null | 610 | Genuinely uncategorized in source; surfaced as `'unknown'` in category-facing queries, not dropped |
| 2026-07-05 | `fact_order_items` / `order_payments` | Item total vs. payment total mismatch (>0.01) | 303 orders (0.30%) | Vouchers, installments, cancellations; quantified in `sql/03_analysis/16_items_vs_payments_reconciliation.sql`, not an ETL error (item-level revenue ties out exactly to staging - see architecture.md) |
