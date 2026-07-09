# Power BI Build Specification

This repository produces the feeding views, DAX measures, and this build spec only - never a
`.pbix` file (MASTER_DOC section 4.3, hard boundary #3). Building the actual dashboard is a
human task using Power BI Desktop, following this document exactly.

## 1. Data source

Connect Power BI Desktop to the local PostgreSQL instance (`make db-up`, then `make pipeline`
and `make views` to populate `analytics.*`), **Import mode** (dataset is small enough that
DirectQuery adds nothing). Import these objects only:

| Object | Type | Role |
|---|---|---|
| `analytics.vw_sales` | View | Revenue, category, seller analysis |
| `analytics.vw_orders` | View | Delivery performance, review scores |
| `analytics.vw_customers` | View | Retention, repeat-purchase |
| `analytics.vw_daily_orders` | View | Actuals for the forecast band |
| `analytics.forecast_28d` | Table | 28-day forecast + interval band |
| `analytics.dim_date` | Table | Marked date table (see below) |

Do not import `stg.*`, `fact_orders`, `fact_order_items`, or the raw dim/fact tables directly -
the views already bake in the correct population filters (delivered vs. all-placed) so the
model can't accidentally mix populations.

## 2. Model relationships

- `dim_date[date]` → `vw_sales[order_date]`, `vw_orders[order_date]`, `vw_daily_orders[order_date]`,
  `forecast_28d[date]` - one-to-many, single direction. Use `order_date` (a `DATE` column), not
  `order_purchase_timestamp` (`TIMESTAMP`) - relating a date table to a timestamp column with a
  time component silently matches zero rows in Power BI.
- Mark `dim_date` as the model's official Date Table (Table Tools -> Mark as Date Table),
  using the `date` column - required for the `Revenue MoM %` time-intelligence measure in
  `dax_measures.md`.
- No relationship is needed between `vw_sales` and `vw_orders`/`vw_customers` - each page uses
  whichever view(s) answer that page's question directly, avoiding cross-filtering surprises.

## 3. Pages

Page titles ARE the stakeholder questions (MASTER_DOC section 15). ≤6 visuals per page,
slicers for date / state / category, no 3D or pie-chart visuals.

### Page 1 — "Where is our revenue coming from, and is it growing?" (CFO)
- KPI cards: `Total Revenue`, `Total Orders`, `AOV`, `Repeat Cust %`, `Avg Review Score`.
- Line chart: monthly revenue with `Revenue MoM %` as a secondary line/label.
- Bar chart: category Pareto (revenue by `vw_sales[product_category_name_english]`, sorted
  descending, cumulative % line overlay).
- Map or bar chart: revenue by `vw_sales[customer_state]`.
- Slicers: date range (via `dim_date`), state, category.

### Page 2 — "What's driving sales, and how concentrated is it?" (CFO)
- Matrix: category x month revenue (`vw_sales`).
- Line chart: AOV trend by month.
- Stacked bar: payment type mix (needs `analytics.order_payments` added to the model for this
  one visual only - installments/payment mix isn't in `vw_sales`; import it as a Import-mode
  table, related to `vw_sales[order_id]` many-to-one).
- Bar chart: top-10 seller GMV concentration (`vw_sales[seller_id]`, top N filter).

### Page 3 — "Who returns, and which segments matter?" (CMO)
- Matrix/heatmap: cohort retention - **precomputed in SQL**
  (`sql/03_analysis/12_cohort_retention_matrix.sql`), imported as its own Import-mode query
  rather than modeled live, since the cohort pivot is exactly the kind of complex logic that
  belongs in SQL, not DAX (MASTER_DOC section 15).
- Bar chart: RFM segment sizes and revenue share - import
  `sql/03_analysis/15_rfm_segment_share.sql`'s output the same way.
- Donut replaced with a simple bar: one-time vs. repeat split (`vw_customers[is_repeat]`,
  `Repeat Cust %`).
- KPI card: `Repeat Cust %`.

### Page 4 — "Does delivery performance affect satisfaction, and what's next-month capacity?" (Ops)
- Histogram: `vw_orders[delivery_days]` distribution.
- Line chart: `Late Delivery %` trend by month, and by state (two visuals or a slicer toggle).
- Clustered bar: `Avg Review Score` and `Pct 1-2 Star` split by `vw_orders[is_late]` - this is
  the tested finding (Mann-Whitney U, `notebooks/03_delivery_reviews.ipynb`); the visual should
  cite the p-value and n in a text box, not just show the bars.
- Line + area (forecast band): `vw_daily_orders[orders]` (actuals, last ~90 days) plus
  `forecast_28d[forecast]` with `lower`/`upper` as a shaded band. State in a text box that
  Holt-Winters did not beat the seasonal-naive baseline in the walk-forward backtest, so the
  seasonal-naive forecast is what's plotted (`docs/monitoring_policy.md`) - don't let the chart
  imply a fancier model than what was actually recommended.

## 4. Design rules

- Consistent theme across all 4 pages (one custom Power BI theme JSON, or a built-in theme
  applied uniformly).
- Marked date table (section 2) - required before any time-intelligence measure works.
- Every visual sources from a view or the forecast table, never a base fact/dim table.
- No visual should mix delivered-only and all-placed-order populations in the same chart
  (MASTER_DOC section 11's population rule) - `vw_daily_orders` is the only all-placed source
  and it's used only on the forecast band.

## 5. Publishing

Power BI service needs a work/school email; personal Gmail typically can't sign up, and
tenant admins can disable "Publish to web". If blocked: high-quality screenshots plus a
2-minute walkthrough video in the README are fully acceptable (MASTER_DOC section 21), or
rebuild in Tableau Public.

## 6. Manual QA checklist (MASTER_DOC section 19 - BI visuals are not automated)

- [ ] Every KPI card matches the reference values in `dax_measures.md` within rounding.
- [ ] Slicers on one page don't silently affect another page's visuals unexpectedly.
- [ ] Late-vs-review comparison visual states the Mann-Whitney p-value and n, not just bars.
- [ ] Forecast band visual states the seasonal-naive verdict, not an implied "AI forecast".
- [ ] No page exceeds 6 visuals; no 3D/pie/donut visuals anywhere.
