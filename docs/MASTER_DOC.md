# Master Project Documentation

E-Commerce Revenue & Customer Retention Analytics

*End-to-end Data Analyst portfolio project on the Olist Brazilian e-commerce dataset*

| **Field**               | **Value**                                                                       |
|-------------------------|---------------------------------------------------------------------------------|
| Document role           | Single source of truth for development (supersedes conflicting Blueprint lines) |
| Authoritative baseline  | Built from the locked Blueprint v2 scope; this document is now authoritative in full (docs/BLUEPRINT.md is a trimmed archive) |
| Version / date          | 1.0 - July 2026                                                                 |
| Owner                   | Manoj (builder, analyst, author of record)                                      |
| Target outcome          | Shortlist-grade fresher Data Analyst portfolio; interview-defensible end to end |
| Estimated effort / cost | 5 weeks, ~60 hours / Rs. 0 (all tooling free)                                   |

Contents

*Note: in Word, right-click the table of contents and choose Update Field after opening.*

## 1. Executive Summary

This project is a production-grade analytics build on real marketplace data (~100K orders, 9 relational tables, Olist / Kaggle): a PostgreSQL staging-plus-star-schema warehouse, a validated and idempotent Python ETL pipeline, 15-25 business-question SQL analyses, a statistically tested operational insight (late delivery vs. review score), a 28-day demand forecast with walk-forward validation and a written monitoring policy, a 4-page Power BI dashboard, and a one-page executive memo. Scope is locked (per the locked Blueprint v2 scope this document was built from); nothing is added until v1 ships.

It exists to get a fresher Data Analyst shortlisted and through interviews. Every design choice optimizes for two signals hiring managers screen for: end-to-end workflow competence and business communication. The Definition of Done is mechanical: CI green, clean-room rebuild passes, every published number reproducible from code with a source path, forecast reported against its baseline with bias, and a README a stranger understands in 3 minutes.

## 2. Project Overview

**Deliverables.** A public GitHub repository (pipeline, SQL, executed notebooks, tests, CI badge, docs), a Power BI dashboard (published or screenshots + walkthrough video), an executive insights memo (human-authored), one Excel pivot summary, and resume bullets whose every number is self-computed.

Six differentiators separate this from the typical fresher submission - protect them during development:

- Real relational data (9 messy tables), not a single clean CSV.

- A modeled warehouse: staging layer to star schema, with documented grain and keys.

- Documented data-quality checks on input AND output layers, plus a revenue reconciliation.

- A statistical hypothesis test, not just charts.

- A forecast governed by a baseline comparison, bias tracking, and a written monitoring policy.

- One-command reproducibility from a clean database, proven in CI.

## 3. Business Problem & Objectives

Framing (use verbatim in the README): Olist is a Brazilian e-commerce marketplace connecting small sellers to customers. Leadership has three questions ahead of annual planning:

- Revenue (CFO): what drives growth - more customers, bigger baskets, or specific categories/regions - and where is revenue concentrated and therefore at risk?

- Retention (CMO): what share of customers ever return, what does monthly cohort retention look like, and which RFM segments deserve targeted spend?

- Operations (Head of Ops): does delivery performance measurably affect satisfaction and repeat purchase, and is the effect statistically significant?

**Objectives / success criteria.** Each dashboard page answers a named stakeholder question in its title; the memo carries 5-7 quantified findings with recommendations; every metric follows the KPI contract in Section 15; the operational finding is tested, not eyeballed; a 28-day capacity view exists with honest uncertainty.

## 4. Project Scope & Out-of-Scope

### 4.1 Locked core (build all of this, nothing else first)

- PostgreSQL 16: stg mirror schema, analytics star schema (facts, dims, typed order_reviews / order_payments), dim_date, indexes.

- Python ETL: ingest, validate (input + output layers), transform; idempotent, logged, .env-configured; pytest suite; GitHub Actions CI with badge.

- SQL analysis layer: 15-25 saved queries (quality over count) including cohorts, rule-based RFM, Pareto, and the items-vs-payments reconciliation.

- Statistics: Mann-Whitney U on late delivery vs. review score, with medians and 1-2 star shares.

- Forecasting Module A: seasonal-naive baseline, Holt-Winters, intervals (SARIMA or empirical), walk-forward backtest, WAPE + bias, accuracy chart, monitoring policy.

- Power BI: 4 pages incl. forecast band; simple DAX; complex logic precomputed in SQL views. One Excel pivot deliverable.

- Documentation: README, data dictionary + anomaly log, findings.md, architecture.md, monitoring_policy.md, human-authored insights memo.

- Publication: pinned GitHub repo, dashboard link or screenshots + video, LinkedIn post, resume bullets.

### 4.2 Optional ladder (only after core ships, in this order)

1\) K-Means segmentation benchmarked against rule-based RFM. 2) Power BI Decomposition Tree on the revenue page. 3) Streamlit demo. 4) dbt refactor of transforms. 5) Logistic-regression driver analysis (late delivery to repeat purchase). None of these appear on the resume unless actually built and defensible.

### 4.3 Rejected register (do not add; each has an interview-ready reason)

| **Rejected item**                                     | **One-line reason**                                                                                                   |
|-------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| LLM-generated summaries / automated insights          | The memo is the proof of the most-valued analyst skill; delegating it deletes the signal and risks fabricated numbers |
| Text-to-SQL / chat-with-data bot                      | App engineering, not analysis; quality undefendable in a DA interview                                                 |
| Model-monitoring dashboard                            | Nothing is deployed; backtest chart + written policy achieves the legitimate goal at a fraction of the cost           |
| Orchestrators (Airflow/Prefect/Dagster)               | One-machine batch job; Makefile is the right scale - know when orchestration earns its keep                           |
| Great Expectations / DQ frameworks                    | Hand-rolled pytest shows deeper understanding here; frameworks add config surface                                     |
| Cloud-warehouse migration                             | Zero added analytical signal; note ANSI portability in README instead                                                 |
| Semantic / metrics layer products                     | The KPI contract table IS the metrics layer at this scale                                                             |
| ML anomaly detection                                  | A rolling z-score in EDA achieves the objective; complexity without evidence                                          |
| Deep learning; churn/propensity models; NLP sentiment | No churn construct in marketplace data; labeled scores already exist; scale does not justify DL                       |

**Scope-change rule.** No additions before v1 ships. Any change requires a written technical reason documented alongside the change. Slip rule: cut the optional ladder top-down; never cut documentation, validation, or the baseline comparison.

## 5. High-Level Architecture

> Kaggle CSVs (data/raw, gitignored)
>
> \| src/ingest.py - loads verbatim, no cleaning
>
> v
>
> stg.\* (raw mirror, all TEXT)
>
> \| src/validate.py - INPUT data-quality checks (blocking + logged)
>
> \| sql/02_transform/\*.sql - typed, deduplicated, derived columns
>
> v
>
> analytics.\* (star schema) - facts, dims, typed reviews/payments
>
> \| src/validate.py - OUTPUT checks: reconcile counts, orphan FKs, revenue tie-out
>
> +--\> sql/03_analysis/ - 15-25 business queries (+ saved outputs)
>
> +--\> notebooks/01-03 - EDA, cohorts/RFM, statistical test
>
> +--\> notebooks/04 - forecast -\> analytics.forecast_28d
>
> +--\> sql/04_dashboard_views/ -\> Power BI (4 pages) -\> executive memo

Principles: (1) staging/analytics separation mirrors real analytics teams and gives interview vocabulary; (2) every script is idempotent and re-runnable; (3) computation lives in SQL, presentation in the BI layer; (4) two environments only - local (Docker Postgres, real data) and CI (GitHub Actions service Postgres, synthetic fixtures).

## 6. Technology Stack & Justification

| **Layer**   | **Choice**                                   | **Why / alternative considered / why preferred**                                                                                                                                                 |
|-------------|----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Database    | PostgreSQL 16 (Docker)                       | Window functions + CTEs are exactly what SQL interviews test. Alt: MySQL/SQLite (weaker analytics surface), cloud DW (setup cost, zero added signal). Postgres is free, local, industry-current. |
| Language    | Python 3.11+ (pinned)                        | pandas, SQLAlchemy, psycopg2-binary, scipy, statsmodels, matplotlib. Alt: R - viable, but Python dominates Indian analyst JDs and the builder's stack.                                           |
| BI          | Power BI Desktop (free)                      | Leads Indian analyst postings; DAX is a screening topic. Alt: Tableau Public - use it if not on Windows (Power BI Desktop is Windows-only) and say so in the README.                             |
| Spreadsheet | Excel (one deliverable)                      | Still explicitly listed in most fresher JDs; a pivot summary costs ~2 hours and checks the box.                                                                                                  |
| VCS / CI    | Git + GitHub + Actions                       | The repo IS the portfolio; CI on data-quality tests is core scope (promoted in v2 - builder already knows Actions).                                                                              |
| Excluded    | dbt, GE, orchestrators, Spark, ML frameworks | See rejected register (Section 4.3). Exclusions are deliberate and defensible - that is the point.                                                                                               |

## 7. Project Folder Structure

Canonical tree (harmonized; supersedes minor Blueprint variations):

> ecommerce-retention-analytics/
>
> \|- README.md \# the 3-minute pitch
>
> \|- LICENSE \# MIT + dataset attribution note
>
> \|- Makefile \# setup \| db-up \| pipeline \| test \| notebooks \| clean
>
> \|- requirements.txt \# exact pinned versions
>
> \|- docker-compose.yml \# postgres:16, healthcheck, named volume
>
> \|- .env.example .gitignore \# .env, data/raw/, caches are ignored
>
> \|- .github/workflows/ci.yml \# service Postgres + fixtures + pytest
>
> \|- data/raw/ (gitignored) data/processed/
>
> \|- sql/01_schema/ 02_transform/ 03_analysis/ (+outputs/) 04_dashboard_views/
>
> \|- src/ingest.py validate.py transform.py run_pipeline.py utils.py
>
> \|- notebooks/01_eda 02_retention_rfm 03_delivery_reviews 04_demand_forecast
>
> \|- dashboard/BUILD_SPEC.md dax_measures.md exec_summary.xlsx screenshots/
>
> \|- docs/BLUEPRINT.md architecture.md data_dictionary.md findings.md
>
> \| insights_memo.md (human-authored) monitoring_policy.md
>
> \|- tests/test_input_quality.py test_output_quality.py fixtures/

## 8. Database Design & Star Schema

Two schemas: stg (verbatim TEXT mirror of the 9 CSVs) and analytics (typed star schema).

> dim_date
>
> \|
>
> dim_customers - fact_orders - fact_order_items - dim_products
>
> \| \|
>
> order_reviews, order_payments dim_sellers
>
> (typed side tables, joined at query time)

| **Table**              | **Grain**                            | **Keys / notable columns and derivations**                                                                                                              |
|------------------------|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| fact_orders            | 1 row per order                      | order_id (PK), customer_id (FK); status + 5 timestamps; derived delivery_days, is_late = delivered_customer_date \> estimated_delivery_date             |
| fact_order_items       | 1 row per item line                  | (order_id, order_item_id) PK; product_id, seller_id FKs; price, freight_value                                                                           |
| dim_customers          | 1 row per customer_id (ORDER-scoped) | customer_unique_id is the PERSON key - all retention/repeat math uses it. Grain documented deliberately: this is the dataset's famous trap              |
| dim_products           | 1 row per product                    | English category joined in from the translation table                                                                                                   |
| dim_sellers / dim_date | per seller / per calendar day        | dim_date generated: date, month, year, weekday, is_weekend                                                                                              |
| order_reviews (typed)  | 1 row per ORDER after dedup          | Source can hold multiple reviews per order (verify count in profiling); rule: keep latest by review answer timestamp; log duplicates in the anomaly log |
| order_payments (typed) | 1 row per payment record             | Multiple rows per order are legitimate (installments, vouchers); aggregate at query time                                                                |
| geolocation handling   | 1 row per zip prefix after dedup     | Average lat/lng per prefix; decision documented in data_dictionary.md                                                                                   |

**Indexes.** PKs on all ids; b-tree on fact_orders(order_purchase_timestamp), fact_order_items(order_id), fact_order_items(product_id). Rationale: join and filter columns. Be ready for the EXPLAIN ANALYZE follow-up.

## 9. ETL Workflow

| **Module**          | **Responsibility**  | **Key behaviors**                                                                                                                                                                 |
|---------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| src/ingest.py       | Download + load raw | kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip (stop and ask on 404); load 9 CSVs verbatim to stg via to_sql(chunksize=10000); log row counts in/out |
| src/validate.py     | Quality gates       | Input checks after ingest; output checks after transform; blocking failures exit non-zero                                                                                         |
| src/transform.py    | Build the star      | Executes sql/01_schema then sql/02_transform in order; DROP IF EXISTS + CREATE AS pattern                                                                                         |
| src/run_pipeline.py | Orchestrate         | ingest -\> validate(input) -\> transform -\> validate(output); single entry point behind make pipeline                                                                            |
| src/utils.py        | Shared              | get_engine() from .env (python-dotenv), logger factory                                                                                                                            |

**Properties (name these in the README - each is an interview talking point).** Idempotent: any step re-runs safely (drop-and-recreate staging; rebuildable analytics). Validated: pipeline fails loudly, never ships silently wrong tables. Logged: counts at every stage via the logging module. Configured: credentials only in .env (gitignored); .env.example committed. Tradeoff noted: to_sql is simple but slow; Postgres COPY is ~10x faster - simplicity chosen at ~1M rows, faster path known.

## 10. Data Validation & Data Quality Strategy

### 10.1 Input layer (staging)

| **Check**             | **Example**                                                                                      | **Severity** |
|-----------------------|--------------------------------------------------------------------------------------------------|--------------|
| Row counts            | Each staging table \> 0 and matches CSV line count minus header                                  | Blocking     |
| PK uniqueness         | order_id unique in orders; (order_id, order_item_id) unique in items                             | Blocking     |
| Referential integrity | Every order_items.order_id exists in orders; every product_id in products                        | Blocking     |
| Domain checks         | review_score between 1 and 5; price \>= 0                                                        | Blocking     |
| Temporal sanity       | delivered_customer_date \>= purchase_timestamp - count and log violations (they exist in source) | Logged       |
| Null policy           | Critical-column null rates below documented thresholds                                           | Logged       |

### 10.2 Output layer (analytics) - added in v2

- Row reconciliation: fact/dim counts tie to staging after documented dedup rules.

- Zero orphan foreign keys after build.

- Revenue tie-out: total item revenue (staging) equals fact_order_items total; items-vs-payments mismatch quantified and explained (Section 11, query D).

**Severity policy.** Blocking = pipeline exits non-zero and CI fails. Logged = recorded in the anomaly log with counts and a handling decision. Anomaly log format (in data_dictionary.md): date \| table \| check \| count \| decision. Never silently drop or fix data; the anomalies are interview gold.

## 11. SQL Implementation Plan

**Conventions.** One business question per file, header comment '-- QUESTION: ...'; uppercase keywords; snake_case; CTEs over nesting; no SELECT \* in final queries; trimmed result samples saved to sql/03_analysis/outputs/ for traceability. Target 15-25 queries - quality over count.

| **Theme**       | **Queries (business questions)**                                                                                                                   |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Revenue (CFO)   | Monthly revenue + MoM growth (A); AOV trend; category Pareto; revenue by state; payment mix + installments; seller concentration (top-N GMV share) |
| Operations      | Order-status funnel; delivery-days distribution; late-% by month and by state; late vs. review score summary                                       |
| Customers (CMO) | Cohort retention matrix (B); repeat-purchase rate; rule-based RFM (C) - all on customer_unique_id, DELIVERED orders only                           |
| Integrity       | Items-vs-payments reconciliation (D); duplicate-review count; temporal-violation count                                                             |

**Metric-population rule (v2 clarification).** Revenue, retention, repeat rate, and RFM are computed on DELIVERED orders; the forecast series uses ALL PLACED orders (ops must process them regardless of final status). Every KPI carries its population explicitly in the Section 15 contract - two defensible definitions, never mixed silently.

Reference query A - monthly revenue with MoM growth

> WITH monthly AS (
>
> SELECT date_trunc('month', o.order_purchase_timestamp)::date AS month,
>
> SUM(oi.price + oi.freight_value) AS revenue
>
> FROM analytics.fact_orders o
>
> JOIN analytics.fact_order_items oi USING (order_id)
>
> WHERE o.order_status = 'delivered'
>
> GROUP BY 1
>
> )
>
> SELECT month, revenue,
>
> ROUND(100.0 \* (revenue - LAG(revenue) OVER (ORDER BY month))
>
> / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 1) AS mom_growth_pct
>
> FROM monthly ORDER BY month;

Reference query B - monthly cohort retention (delivered orders, person key)

> WITH first_purchase AS (
>
> SELECT c.customer_unique_id,
>
> MIN(date_trunc('month', o.order_purchase_timestamp)) AS cohort_month
>
> FROM analytics.fact_orders o
>
> JOIN analytics.dim_customers c USING (customer_id)
>
> WHERE o.order_status = 'delivered' -- v2: population fix
>
> GROUP BY 1
>
> ),
>
> activity AS (
>
> SELECT DISTINCT c.customer_unique_id,
>
> date_trunc('month', o.order_purchase_timestamp) AS activity_month
>
> FROM analytics.fact_orders o
>
> JOIN analytics.dim_customers c USING (customer_id)
>
> WHERE o.order_status = 'delivered' -- v2: population fix
>
> )
>
> SELECT f.cohort_month::date AS cohort,
>
> (EXTRACT(YEAR FROM age(a.activity_month, f.cohort_month)) \* 12
>
> \+ EXTRACT(MONTH FROM age(a.activity_month, f.cohort_month)))::int AS month_offset,
>
> COUNT(DISTINCT a.customer_unique_id) AS active_customers
>
> FROM first_purchase f JOIN activity a USING (customer_unique_id)
>
> GROUP BY 1, 2 ORDER BY 1, 2;

Expected shape: repeat rates are very low single digits. That IS the finding - analyze it, do not hide it. Frequency quintiles will therefore be tie-dominated: NTILE splits identical values arbitrarily, so bucket F as 1 / 2 / 3+ and document the choice.

Reference query C - RFM scoring (delivered orders)

> WITH rfm AS (
>
> SELECT c.customer_unique_id,
>
> MAX(o.order_purchase_timestamp)::date AS last_order,
>
> COUNT(DISTINCT o.order_id) AS frequency,
>
> SUM(oi.price + oi.freight_value) AS monetary
>
> FROM analytics.fact_orders o
>
> JOIN analytics.dim_customers c USING (customer_id)
>
> JOIN analytics.fact_order_items oi USING (order_id)
>
> WHERE o.order_status = 'delivered'
>
> GROUP BY 1
>
> )
>
> SELECT customer_unique_id,
>
> NTILE(5) OVER (ORDER BY last_order) AS r_score,
>
> CASE WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 2 ELSE 3 END AS f_bucket,
>
> NTILE(5) OVER (ORDER BY monetary) AS m_score
>
> FROM rfm;

Reference query D - revenue reconciliation (the data-integrity showpiece)

> WITH item_totals AS (
>
> SELECT order_id, SUM(price + freight_value) AS item_total
>
> FROM analytics.fact_order_items GROUP BY order_id
>
> ),
>
> payment_totals AS (
>
> SELECT order_id, SUM(payment_value) AS payment_total
>
> FROM analytics.order_payments GROUP BY order_id
>
> )
>
> SELECT o.order_id, i.item_total, p.payment_total,
>
> ROUND(p.payment_total - i.item_total, 2) AS diff
>
> FROM analytics.fact_orders o
>
> JOIN item_totals i USING (order_id)
>
> JOIN payment_totals p USING (order_id)
>
> WHERE ABS(p.payment_total - i.item_total) \> 0.01
>
> ORDER BY ABS(p.payment_total - i.item_total) DESC;

Quantify the mismatch rate, explain causes found (vouchers, installments, cancellations), and state the standardized revenue definition: item price + freight on delivered orders, reconciled against payments.

## 12. Python Module Design

| **Module / notebook** | **Public surface (sketch)**                                                                     | **Notes**                                                                                                                     |
|-----------------------|-------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| src/utils.py          | get_engine() -\> Engine; get_logger(name) -\> Logger                                            | Reads .env; never hardcode credentials                                                                                        |
| src/ingest.py         | download_dataset(dest: Path) -\> None; load_staging(engine, raw_dir: Path) -\> dict\[str, int\] | Returns row counts for logging/tests                                                                                          |
| src/validate.py       | run_input_checks(engine) -\> Report; run_output_checks(engine) -\> Report                       | Report dataclass: passed, blocking_failures, logged_anomalies                                                                 |
| src/transform.py      | run_sql_dir(engine, path: Path) -\> None                                                        | Executes \*.sql in filename order inside a transaction per file                                                               |
| notebooks/01-03       | EDA + stable-window derivation; cohorts/RFM heatmaps; Mann-Whitney test                         | Read from analytics only; restart-and-run-all before commit; executed via jupyter nbconvert --to notebook --execute --inplace |
| notebooks/04          | Forecast (Section 14)                                                                           | Only notebook with a declared side effect: writes analytics.forecast_28d + CSV                                                |

Division of labor (defend this in interviews): aggregation and modeling live in SQL (auditable, portable); Python handles statistics, reshaping, and time series. Do not re-implement SQL work in pandas.

## 13. Statistical Analysis Plan

**Question.** Do late deliveries receive lower review scores than on-time deliveries? H0: the score distributions do not differ; H1 (one-sided): late scores are stochastically lower.

**Test.** Mann-Whitney U (scipy.stats.mannwhitneyu, alternative='less'), alpha = 0.05. Why not a t-test: scores are ordinal (1-5) and heavily skewed; comparing means assumes an interval scale and near-normality - the textbook-wrong choice an interviewer will probe.

**Reporting standard.** p-value PLUS group medians PLUS share of 1-2 star reviews per group. With n in the tens of thousands, p will be tiny almost regardless - the effect size is the insight, not the p-value. Join uses the deduplicated one-review-per-order table (Section 8) so orders are not double-counted.

**Causal humility (verbatim in the memo).** This is an observational association, not proof of causation; late delivery correlates with distance, seller, and freight. Stating this signals maturity, not weakness.

## 14. Forecasting Module Design (Module A)

**Business problem.** Ops plans carrier capacity and support staffing 2-4 weeks out. Deliver a 28-day daily order-volume forecast with uncertainty, and quantify the lift over the rule of thumb (same as last week).

| **Element**       | **Specification**                                                                                                                                                                                                                                                                              |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Series            | Daily count of orders PLACED (all statuses - ops processes everything), from fact_orders.order_purchase_timestamp; asfreq('D'); assert no gaps inside the window (investigate before filling)                                                                                                  |
| Stable window     | Derived in 01_eda, never assumed: exclude the sparse 2016 ramp and the truncated final weeks; record exact bounds in the notebook and reuse everywhere                                                                                                                                         |
| Event handling    | Expect at least one extreme promotional spike (Black Friday 2017); choose and document treatment: SARIMAX event dummy, or exclusion from error windows                                                                                                                                         |
| Technique ladder  | 1\) naive + seasonal naive (repeat last observed week across horizon) 2) Holt-Winters additive, seasonal_periods=7 3) SARIMA only for proper intervals - justify orders with residual diagnostics. Escape hatch: HW point forecasts + empirical intervals from walk-forward residual quantiles |
| Validation        | Walk-forward backtest, expanding origin, \>= 6 folds x 28 days. NEVER shuffled CV on time series - temporal leakage, same error class as patient leakage in medical ML                                                                                                                         |
| Metrics           | WAPE = sum\|error\| / sum\|actual\| (headline); bias = mean(forecast - actual), positive = over-forecasting (v2 sign convention); MAE supporting                                                                                                                                               |
| Acceptance rule   | Report the model only if walk-forward WAPE beats seasonal naive; otherwise the baseline is the recommendation - also a valid, defensible result                                                                                                                                                |
| Exports           | analytics.forecast_28d (date, forecast, lower, upper) + data/processed/forecast_28d.csv                                                                                                                                                                                                        |
| Monitoring policy | docs/monitoring_policy.md: refit cadence; investigate if rolling WAPE exceeds seasonal-naive WAPE or \|bias\| exceeds a threshold set from the actual backtest. Written policy only - nothing is deployed and the README says so                                                               |
| Rejected here     | Prophet (extra dependency, harder to defend than classical methods); gradient boosting / LSTMs (~600-700 points with one weekly cycle does not warrant them)                                                                                                                                   |

## 15. Dashboard Design & KPIs

**Feeding-layer rule (v2 consistency fix).** Power BI imports dedicated views in sql/04_dashboard_views/ that bake in the population filters: vw_sales (delivered item lines with line_revenue = price + freight), vw_orders (delivered orders with is_late, delivery_days), vw_customers (person grain with precomputed is_repeat), vw_daily_orders (all placed, for the forecast page), analytics.forecast_28d. DAX stays minimal; complex logic is precomputed in SQL - the mature interview answer.

| **Page**                      | **Audience** | **Question / key visuals**                                                                                                                               |
|-------------------------------|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1\. Executive Overview        | CFO          | KPI cards (revenue, orders, AOV, repeat %, avg review); monthly revenue + MoM; category Pareto; revenue by state                                         |
| 2\. Sales Deep-Dive           | CFO          | Category x month matrix; AOV trend; payment mix + installments; seller concentration                                                                     |
| 3\. Customers & Retention     | CMO          | Cohort heatmap (matrix visual); RFM segment sizes + revenue share; one-time vs repeat split                                                              |
| 4\. Operations & Satisfaction | Ops          | Delivery-days histogram; late-% trend and by state; late vs on-time review comparison (the tested finding); actuals + 28-day forecast with interval band |

Core DAX (measures reference feeding views)

> Total Revenue = SUM ( vw_sales\[line_revenue\] )
>
> Total Orders = DISTINCTCOUNT ( vw_sales\[order_id\] )
>
> AOV = DIVIDE ( \[Total Revenue\], \[Total Orders\] )
>
> Late Delivery % = DIVIDE (
>
> CALCULATE ( COUNTROWS ( vw_orders ), vw_orders\[is_late\] = TRUE() ),
>
> COUNTROWS ( vw_orders ) )
>
> Repeat Cust % = DIVIDE (
>
> CALCULATE ( DISTINCTCOUNT ( vw_customers\[customer_unique_id\] ),
>
> vw_customers\[is_repeat\] = TRUE() ),
>
> DISTINCTCOUNT ( vw_customers\[customer_unique_id\] ) )

KPI contract (definitions are exact; vague KPIs fail interviews)

| **KPI**                 | **Definition**                                                  | **Population**      | **Owner** |
|-------------------------|-----------------------------------------------------------------|---------------------|-----------|
| Revenue                 | Sum of item price + freight                                     | Delivered orders    | CFO       |
| Orders / AOV            | Distinct orders; revenue / orders                               | Delivered           | CFO       |
| MoM growth %            | Window-function query A                                         | Delivered           | CFO       |
| Repeat-customer %       | Persons (customer_unique_id) with \>= 2 orders / all persons    | Delivered           | CMO       |
| Cohort retention M1/M3  | % of cohort active in offset month                              | Delivered           | CMO       |
| RFM segment share       | Customers and revenue per segment                               | Delivered           | CMO       |
| Median delivery days    | Purchase to delivered                                           | Delivered           | Ops       |
| Late-delivery %         | Delivered after estimated date / delivered                      | Delivered           | Ops       |
| Avg review + % 1-2 star | Overall and split by lateness (deduped reviews)                 | Delivered w/ review | Ops       |
| Forecast WAPE / bias    | Walk-forward, vs seasonal naive; bias = mean(forecast - actual) | All placed orders   | Ops       |

Design rules: \<= 6 visuals per page; slicers for date / state / category; import mode; marked date table; page titles ARE the stakeholder questions. Excel deliverable: one pivot workbook (dashboard/exec_summary.xlsx) built from a processed extract. Publishing caveat: the Power BI service needs a work/school email and tenant admins can disable Publish to web - test with the university email in Week 1; fallback is screenshots + a 2-minute walkthrough video, or Tableau Public.

## 16. Development Workflow

Phase-gate model - identical whether building manually or via Claude Code. A red gate blocks progress; fix and re-run the full gate.

| **Phase**                   | **Output**                                                        | **Gate**                                            |
|-----------------------------|-------------------------------------------------------------------|-----------------------------------------------------|
| 0 Scaffold                  | Repo tree, docker-compose, Makefile, pinned requirements, LICENSE | make db-up healthy; pip install clean               |
| 1 Ingest                    | 9 staging tables + logged counts                                  | Counts match CSV lines minus headers                |
| 2 Input validation          | Checks + anomaly log (\>= 5 real anomalies)                       | pytest input suite green                            |
| 3 Transform + output checks | Star schema + reconciliations                                     | make clean -\> pipeline end-to-end; pytest green    |
| 4 SQL layer                 | 15-25 queries + saved outputs                                     | Runner executes all; outputs business-plausible     |
| 5 Notebooks 1-3             | EDA (stable window), cohorts/RFM, statistical test                | All execute top-to-bottom clean                     |
| 6 Forecast + monitoring     | Backtest table, accuracy chart, policy doc, exports               | Verdict vs baseline stated either way               |
| 7 CI                        | Fixtures + workflow + badge                                       | Exact CI steps green locally                        |
| 8 Dashboard enablement      | Views, DAX file, BUILD_SPEC                                       | Views query clean; DAX references existing columns  |
| 9 Documentation             | README, findings.md, dictionary, architecture                     | Zero placeholders; every number has a source path   |
| 10 Clean-room verify        | Full rebuild evidence, Definition-of-Done checklist                | Full rebuild + tests + notebooks green from scratch |

## 17. Coding Standards

- Python: PEP 8; type hints on public functions; docstrings state what AND why; pathlib over string paths; logging module (never print) ; no bare except; f-strings; constants/config isolated.

- SQL: uppercase keywords; snake_case identifiers; explicit JOIN ... USING/ON; CTEs over deep nesting; every analysis file starts with '-- QUESTION: ...'.

- Notebooks: restart-and-run-all before every commit; seeds set where randomness exists; read-only against analytics except declared exports.

- General: one purpose per module/file; names describe business meaning (is_late, line_revenue), not mechanics.

## 18. Git & CI Workflow

**Git.** Solo project: commit to main in small, imperative-message commits ('feat: staging ingest with row-count logging'); at least one commit per phase; never commit data/raw, .env, kaggle.json, or notebook checkpoints. Tag v1.0 at Definition of Done.

**CI (GitHub Actions - core scope).** postgres:16 service container with health options; install pinned requirements; run the pipeline against tests/fixtures; pytest -q; README badge. Fixtures keep CI free of Kaggle credentials - no secrets required. Tradeoff: CI proves mechanics on synthetic data; real-data correctness is proven locally by the clean-room gate (Phase 10).

## 19. Testing Strategy

| **Level**           | **What / where**                                                                    | **Runs in**           |
|---------------------|-------------------------------------------------------------------------------------|-----------------------|
| Unit                | utils + validation helpers (pure functions)                                         | Local + CI            |
| Data tests (input)  | tests/test_input_quality.py against stg                                             | Local + CI (fixtures) |
| Data tests (output) | tests/test_output_quality.py against analytics: reconciliation, orphan FKs, tie-out | Local + CI (fixtures) |
| Pipeline smoke      | Full make pipeline on fixtures                                                      | CI                    |
| Integration smoke   | nbconvert --execute on all notebooks                                                | Local (real data)     |
| Not automated       | BI visuals - manual checklist in dashboard/BUILD_SPEC.md                            | Manual                |

**Fixture design.** Synthetic, schema-faithful, small (\<= 200 rows/table), generated by a script, never copied real rows - and with planted defects (one duplicate review, one payment mismatch, one temporal violation) so the checks are demonstrably exercised.

## 20. Documentation Standards

- README order is fixed: summary -\> dashboard image -\> business problem -\> architecture + key decisions -\> quantified findings -\> how to run (3 commands) -\> repo map, data credit + license, limitations.

- findings.md entry format: quantified observation -\> business implication -\> producing query/notebook path. The human-authored insights_memo.md selects 5-7 and adds recommendations in the builder's own voice - the memo is never machine-authored (Section 4.3).

- Hard rule: no placeholder brackets anywhere in final docs; every number is reproducible or the claim is removed.

- data_dictionary.md: every table/column plus the anomaly log; architecture.md: the Section 5 diagram plus decisions (revenue definition, trap handling, stable window).

## 21. Risks & Assumptions

| **Risk / assumption**                                                         | **Mitigation**                                                                                     |
|-------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Kaggle download fails / slug changes                                          | Manual download path documented in README; stop-and-verify rule, never guess mirrors               |
| Power BI service blocked (work-email rule; tenant may disable Publish to web) | Test with university email in Week 1; fallback: screenshots + walkthrough video, or Tableau Public |
| Power BI Desktop is Windows-only                                              | Non-Windows: build in Tableau Public and state the substitution in the README                      |
| Dataset quirks (duplicate reviews, payment mismatches, impossible timestamps) | Defined dedup/handling rules + anomaly log; quirks become interview material                       |
| Short history limits forecasting                                              | Weekly seasonality on daily data only; limitation stated openly in notebook and README             |
| Model fails to beat baseline                                                  | Acceptable outcome by design - report the baseline as the recommendation                           |
| Scope creep                                                                   | Locked register (Section 4.3) + written-reason rule for any change                                 |
| Schedule slip                                                                 | Cut optional ladder top-down; never cut documentation, validation, or the baseline comparison      |

## 22. Development Roadmap (5 weeks, ~2-2.5 h/day)

| **Week**           | **Build**                                                                                                                                | **Done when**                                                 |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| 1 Foundation       | Environment (Docker Postgres, venv, repo); ingest all 9 tables; profiling; start dictionary + anomaly log; test Power BI service sign-in | 9 tables queryable; counts logged; \>= 5 anomalies documented |
| 2 Model + SQL core | Star schema + transforms; input AND output validation green; reconciliation writeup; first ~10 queries                                   | make pipeline rebuilds from a clean DB                        |
| 3 Analysis         | Remaining queries; notebooks 1-3; draft findings                                                                                         | Every finding has a number and a reproducible source          |
| 4 Forecast + CI    | Module A + monitoring policy; fixtures + Actions workflow + badge                                                                        | Backtest table exists; verdict vs baseline written; CI green  |
| 5 Communicate      | Dashboard (incl. forecast band); README + findings; memo (human); publish; resume + LinkedIn                                             | A stranger understands the project in 3 minutes               |

## 23. Definition of Done

☐ CI green on synthetic fixtures (badge visible in README).

☐ Clean-room rebuild passes: make clean && make db-up && make pipeline && pytest -q && make notebooks.

☐ Every number in README / findings / resume bullets carries a source path and reproduces.

☐ No placeholder brackets anywhere in final documents.

☐ Forecast reported WITH baseline comparison and bias; monitoring policy written.

☐ README passes the 3-minute stranger test; dashboard published or screenshots + video linked.

☐ Scope equals Section 4.1 exactly - no unbuilt claims on the resume.

## 24. Interview Highlights

Every question below is earned by building this project. Prepare 2-3 minute answers; the pointer says where the material lives.

| **Theme**     | **Questions (answer source)**                                                                                                                                                                                                                                                          |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Data modeling | Star vs one flat table? (S8) - customer_id vs customer_unique_id trap and its effect on retention math? (S8) - grain of dim_customers? (S8)                                                                                                                                            |
| Data quality  | What did the reconciliation show and what revenue definition did you standardize? (S11-D) - blocking vs logged checks? (S10) - how did you handle duplicate reviews? (S8)                                                                                                              |
| SQL           | What does NTILE do with heavy ties and what did you do about it? (S11-C) - walk through the cohort query (S11-B) - how would you find a slow query? EXPLAIN ANALYZE + indexes (S8)                                                                                                     |
| Statistics    | Why Mann-Whitney over a t-test? (S13) - why is the p-value not the insight at this sample size? (S13) - what would make the association causal? (S13)                                                                                                                                  |
| Forecasting   | Why baseline-first? Why WAPE over MAPE? What is bias and your sign convention? (S14) - why never shuffled CV on time series - and the capstone patient-leakage parallel? (S14) - when would you NOT trust this forecast? (S14, S21)                                                    |
| Engineering   | How is the pipeline idempotent? (S9) - how would you do daily incremental loads? (deliberate non-feature: full rebuild is correct at this scale) - what breaks at 100M rows? (partitioning, warehouse engines, pre-aggregation) - when do orchestration or dbt earn their keep? (S4.3) |
| Communication | Walk one insight from question to recommendation (findings.md -\> memo) - why is the memo human-authored? (S4.3, S20)                                                                                                                                                                  |