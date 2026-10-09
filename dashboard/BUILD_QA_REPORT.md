# Power BI Build: Final QA Report
Olist e-commerce retention analytics · four-page dashboard · built and checked in Power BI Desktop

## Status
The dashboard is complete, with the limitations listed at the end of this report. **`ecommerce_retention_dashboard_final.pbix` is the authoritative file.**

The last polish pass changed presentation only: number locale, wording, alt text, tab order, and text-box and table sizing. No SQL, measure, relationship or population was changed. The file was refreshed against PostgreSQL, saved at 2:18 PM IST on 9 October 2026, closed and reopened from disk. The page 4 wording was then updated to "p < 0.001".

A final pre-delivery audit followed (see "Final pre-delivery audit"). It opened the saved file again, re-checked the key figures against the raw CSV files, and re-ran the Mann–Whitney test.

## Final files
All files are in `D:\PROGRAMING\Data Analytics\ecommerce retention analytics\code\dashboard\`.

| File | Role |
|---|---|
| `ecommerce_retention_dashboard_final.pbix` | Authoritative report. 24,195,620 bytes. SHA-256 `3361bc56936996c912274accf7997f527702e6b280161a8e260aa7d8c6c32f20` |
| `ecommerce_retention_dashboard.pbix` | Byte-identical copy of the file above (same SHA-256) |
| `BUILD_QA_REPORT.md` | This report |
| `DAX_MEASURES_FINAL.md` | Final list of the 43 measures and the calculated column |
| `screenshots\page1_executive_overview.jpg`, `page2_sales_deep_dive.jpg`, `page3_customers_retention.jpg`, `page4_operations_satisfaction.jpg` | Screenshots of the final file (see Limitations, item 9) |
| `BUILD_SPEC.md`, `dax_measures.md`, `exec_summary.xlsx` | Original project files, unchanged |

Local working copies that are **not** part of the deliverable and are not committed to Git:
- `ecommerce_retention_dashboard_final_BACKUP_pre_polish.pbix`: the file as it was before the polish pass (SHA-256 `8adaca54710ac82347597202ae83ad9c8e826b4525b288827da17ad9550f91db`), kept for rollback.
- `ecommerce_analytics.pbip` with its `.Report` and `.SemanticModel` folders: an older development project that predates the final fixes.
- `final_pbip\`: an earlier PBIP export of the report.
- `..\pw\`: a temporary PBIP work folder used to apply the polish edits. It can be deleted.

## Final pre-delivery audit
This audit worked from the files on disk and the raw data, not from earlier reports.

**Done**
- Both PBIX files exist, are byte-identical (`cmp`), have the same SHA-256, and pass a zip integrity test. The package contains 62 visual containers, 44 with alt text and 18 text boxes. The report locale is `en-US`.
- The saved final file was opened from disk in Power BI Desktop. All four pages rendered without errors or dialogs. Page 4 shows "p < 0.001" and the forecast note. Power BI was closed with "Don't save", and the file hash was unchanged afterwards.
- The Mann–Whitney test was re-run from the raw CSV files with pandas and SciPy 1.15.3 (see "p-value note").
- These figures were recomputed from `data/raw` and `data/processed`: 96,478 delivered orders; 96,470 of them with a delivery date; 7,826 late orders (8.11 % of 96,470); 93,358 customers by `customer_unique_id`, of whom 2,801 are repeat customers (3.00 %); a 28-day forecast total of 6,660 (sum of daily lower bounds 3,585, sum of daily upper bounds 9,943); 8 delivered orders without a delivery date, all 8 with a review.
- Page 4 is the only page that changed in the last edit. Its screenshot (taken after the 2:18 PM save) matches the live file.

**Not done in the audit**
- No new PostgreSQL refresh was run, because the audit made no model change. The last refresh is the one before the 2:18 PM save.
- The notebooks themselves were not re-executed. The test and the figures above were reproduced independently from the CSV files. Wording edits made afterwards to notebooks 03 and 04 (see the documentation-correction note below) were also not re-executed against PostgreSQL.
- The DAX measures were not re-run in the live model during the audit. The values on the pages match the recomputed figures above.

## The 8-order discrepancy
An earlier build showed 88,171 on-time reviewed orders, but notebook 03 reports 88,163. The cause was a defect in the dashboard's `delivery_status` calculated column, not in the SQL, the data or the notebooks.

- `vw_orders` holds the delivered orders (96,478), left-joined to reviews deduplicated to the latest review per order.
- `analytics.fact_orders.is_late` is `delivered_customer_date > estimated_delivery_date`. It is NULL when the delivery date is missing, and notebook 03 excludes those rows (`is_late IS NOT NULL`, n = 95,824).
- The calculated column tested `is_late = FALSE`. In DAX, `BLANK() = FALSE()` is TRUE, so the 8 orders with no delivery date were counted as "On time" (88,163 + 8 = 88,171).
- **Fix:** the column now returns "Unknown (no delivery date)" when `is_late` is blank. The reviewed-orders table shows Late 7,661 / On time 88,163 / Unknown 8 / Total 95,832. The two comparison charts are filtered to Late and On time, so they reproduce the notebook: 54.07 % rated 1–2★ for late orders (n = 7,661) and 9.22 % for on-time orders (n = 88,163).
- The audit confirmed the same split from the raw data: 7,661 late and 88,163 on-time reviewed delivered orders, plus 8 reviewed delivered orders without a delivery date. These 8 orders are never counted as on-time or as late.

## Polish pass decisions
| Item | Finding | Decision |
|---|---|---|
| Revenue card used Indian digit grouping (1,54,19,773.75) | The machine's en-IN locale was applied through the file's default format-string locale | **Fixed.** Set to English (United States) under Options › Current file › Regional settings. The measures are unchanged and still numeric (formats `\R\$#,0.00`, `#,0`, `0.0%`). Values now read R$15,419,773.75, 96,478 and R$159.83 |
| Month-on-month swings in the early months | The axis is capped at −50 % / +100 % because the 2016 to January 2017 base is tiny | **Kept.** The cap is disclosed in the subtitle, and trimming the date range would hide data |
| KPI selection, Pareto chart, state ranking, category matrix | Clear, labelled, and values are shown rather than colour alone | **Kept** |
| Database identifiers and jargon in visible text (`seller_id`, "SQL query 05", `NTILE`) | Not suitable for a business reader | **Reworded** in plain language. The method notes now live in this report and in `DAX_MEASURES_FINAL.md` |
| Page 4 text box and reviewed-orders table clipped | The Mann–Whitney box was cut off. The table hid its Unknown row and 1–2★ share column | **Fixed.** Text box and table resized, headers shortened (Reviewed (n), Avg score, Median score, 1–2★ share), KPI cards made 4 px taller |
| Page 4 subtitle implied causation ("Does delivery performance affect…") | A late delivery is associated with lower scores, but the data cannot show cause | **Reworded** to "How does delivery performance relate to customer satisfaction, and what order volume is expected next month?". The commentary opens with "Association, not proof of cause" |
| Forecast wording | The old note said Holt-Winters "did not beat" seasonal-naive, with the two numbers in ambiguous order | **Reworded.** The 6-fold walk-forward backtest gives a mean WAPE of 0.2308 (seasonal-naive) against 0.2310 (Holt-Winters). Holt-Winters wins 4 of the 6 folds, so "tied" is the accurate word |
| Accessibility | No alt text, and tab order followed creation order | **Added** alt text to 44 visuals and set reading-order tab order on all pages |

**Rejected on purpose:** converting numbers to text, changing display units, changing the month-on-month axis or date range, trimming the matrix or RFM definitions, adding new visuals, bookmarks or drill-through, and changing any SQL, measure, relationship or population. The Mann–Whitney statement stays static text, because the test is computed in notebook 03 and not in DAX.

Guidance consulted: Microsoft Learn on accessible Power BI reports (alt text, tab order, contrast), dashboard design tips (key numbers top-left, avoid clutter) and the default format-string locale setting. Only the principles are applied; no wording is quoted.

## p-value note (Mann–Whitney, notebook 03)
Notebook 03 runs `scipy.stats.mannwhitneyu(late, on_time, alternative="less")` on 7,661 late and 88,163 on-time reviewed delivered orders. It prints U = 150,706,850.5 and `p-value = 0.000e+00`.

That printed zero is **floating-point underflow, not a probability of exactly zero.** The dashboard therefore states **p < 0.001**, which the calculation supports. No exact p-value is quoted.

| Result | Source |
|---|---|
| n = 7,661 late, 88,163 on-time; U = 150,706,850.5; printed p = 0.000e+00 | Notebook 03 output (computed by the notebook) |
| Same n and U; SciPy again returns p = 0.0 | Re-run in this audit from the raw CSV files, with the notebook's population rebuilt in pandas (delivered orders, latest review per order, lateness from the delivery and estimate dates). The notebook itself was not re-executed and the database was not queried |
| Normal approximation, mean U = 337,708,371.5. Without tie correction: SD ≈ 2,322,387.6, z ≈ −80.5 | Calculated from the printed n and U |
| Normal approximation with tie correction (ratings are tied integers 1–5): SD ≈ 2,055,180.4, z ≈ −91.0 | Calculated in this audit from the re-run data |
| Effect size: late orders score lower in 77.7 % of late/on-time pairs (ties counted half); rank-biserial correlation 0.55 | Calculated in this audit |

At |z| of 80 or more, the one-sided p-value is far below 0.001 under any reasonable method. A normal approximation is not reliable far into the tail, so no tail probability is reported. The effect size, not the p-value, is the useful result at this sample size.

The notebook's original printed text said "p-value is effectively 0". In the documentation-correction pass, notebook 03's explanatory markdown and its printed p-value line were reworded to say p < 0.001 and to explain the underflow. The calculation and the statistical test are unchanged, and the stored output cell was edited by hand to match, not regenerated.

## Reference validation
Checks against the live model (earlier passes) and against the raw data (this audit). The reference values were used only as checks and are not stored in the model.

| Check | Dashboard | Reference | Result |
|---|---|---|---|
| Total revenue (delivered orders, price + freight) | R$15,419,773.75 | 15,419,773.75 | Match |
| Delivered orders | 96,478 | 96,478 (raw data) | Match |
| Average order value | R$159.83 | Revenue ÷ orders | Match |
| Late orders / late rate | 7,826 / 8.11 % | 7,826 of 96,470 dated orders = 8.112 % (raw data) | Match |
| Late reviewed orders, 1–2★ share, median | 7,661 · 54.07 % · 2 | Notebook 03 and raw data | Match |
| On-time reviewed orders, 1–2★ share, median | 88,163 · 9.22 % · 5 | Notebook 03 and raw data | Match |
| Orders with no delivery date | 8 (shown as Unknown) | 8 (raw data) | Match |
| Repeat customers / customers / rate | 2,801 / 93,358 / 3.00 % | 2,801 / 93,358 / 3.00 % (raw data) | Match |
| 28-day forecast total and summed bounds | 6,660 / 3,585 / 9,943 | `forecast_28d.csv` | Match |
| Top-5 category share | 39.25 % | 39.25 % | Match |
| Latest-month revenue MoM | −4.1 % | −4.1 % (query 01) | Match |
| Payment records / value | 103,886 / R$16,008,872.12 | Query 05 | Match |
| Top-10 seller share | 12.93 % | 12.93 % (query 06) | Match |
| RFM totals | 93,358 customers / R$15,419,773.75 | Customers and Total Revenue | Match |

The Late Delivery % measure divides by all 96,478 delivered orders, so the 8 orders without a delivery date sit in the denominator but are never counted as late. The result is 8.1117 %, against 8.1124 % over the 96,470 dated orders. Both display as 8.11 %.

Not checked against a documented number: median delivery time (10.0 days) and the weighted month-1 retention (0.48 %, which excludes the newest cohort).

## Model
- **Tables:** `vw_sales`, `vw_orders`, `vw_customers`, `vw_daily_orders`, `order_payments`, `dim_date` and `forecast_28d` (PostgreSQL views and tables in schema `analytics`); `cohort_retention` and `rfm_grid` (read-only native SELECTs of repository queries 12 and 15); `forecast_chart` (DAX calculated table); `_Measures` (43 measures).
- **Relationships:** three many-to-one, single-direction relationships from `vw_sales[order_date]`, `vw_orders[order_date]` and `vw_daily_orders[order_date]` to `dim_date[date]`. There are no others, by design. The remaining tables have no date, state or category key at a compatible grain, so slicers do not affect them.
- **Populations:** sales, orders, delivery and reviews use delivered orders. Customers are unique people (`customer_unique_id`), all time. Payments use all payment records in any status. The forecast uses all placed orders and ignores every slicer.
- **DAX review:** all 43 measures were checked for correct results, blank handling, filter context and divide-by-zero. Three defects were found and fixed during the project: `Pct 1-2 Star` (blank counted as 0), `Seller Rank` (needed `seller_label` in the ALL() set) and the `delivery_status` column. See `DAX_MEASURES_FINAL.md`.

## Refresh notes
- The Docker PostgreSQL container has a 64 MB `/dev/shm`, so parallel queries fail on refresh with error 53100. All seven view and table imports therefore use `Value.NativeQuery` with the prefix `SET max_parallel_workers_per_gather = 0;` before an unchanged `SELECT * FROM analytics.<name>`. `cohort_retention` and `rfm_grid` use the same prefix. Rows and columns are unchanged, and parallel table loading is set to One.
- A permanent alternative is to add `shm_size: 1gb` to the PostgreSQL service in `docker-compose.yml` and recreate the container.
- On the first refresh, Power BI shows a native-query approval dialog (Edit Permission, then Run).
- The container must be running, and the database password is entered by the user at refresh.

## Limitations
1. Revenue MoM % for December 2016 is blank in DAX because there is no prior month, whereas SQL query 01 uses LAG across the gap. The chart axis is capped and says so. The AOV and late-rate charts still show a spike or dip in the late-2016 months, which have only a handful of orders. The subtitles flag this.
2. The 28-day lower and upper cards (3,585 and 9,943) are sums of the daily 95 % bounds. They are **not** a 28-day prediction interval, and the page 4 note says so. Notebook 04 used to print the same sums as a "95% interval". Its print and log labels now read "sum of daily bounds ... (not a 28-day interval)" and a markdown cell explains the point. The forecast, the residual quantiles and the bounds themselves are unchanged, and the stored output cells were edited by hand, not regenerated.
3. The Mann–Whitney statement on page 4 and the "roughly 97 % buy once" box on page 3 are static text, written from notebook 03 and the data at build time. They do not update on refresh.
4. RFM segment names are derived in DAX from the SQL R×F grid using the notebook 02 rules. SQL `NTILE` places ties at quintile boundaries arbitrarily, so segment counts can differ slightly from notebook 02. Totals reconcile (93,358 customers, R$15,419,773.75).
5. Repeat Customer Rate is all-time, and the payment visuals and forecast ignore the sales slicers. All three are labelled on the pages.
6. Digit grouping is stored per file (English US). The model's format strings still apply on a machine with other regional settings, but this was verified only on the author's machine.
7. Accessibility is partial. Alt text, reading-order tab order and non-colour cues (data labels, dashed against solid lines) are in place. Not done: a formal contrast measurement of every colour pair (the lightest grey text, #6B7280 on near-white, is believed to be at least 4.5:1 but was not measured), a screen-reader walk-through and a high-contrast theme test.
8. The page 4 reviewed-orders table is tight, and a thin scrollbar can appear. All five columns and all four rows, including Unknown, are visible. The page 4 cards are compact.
9. The screenshots include the Power BI Desktop window and side panes. The page 1–3 screenshots were taken at about 2:05 PM and their title bar still reads "Last saved 2:04 pm". Their content matches the final file, because the 2:18 PM save changed only page 4 wording. The page 4 screenshot was taken after that save.
10. Pages 2 and 3 use custom page heights (960 and 900). The limit of six analytic visuals per page excludes KPI cards, slicers and text boxes.
11. A saved DAX query tab ("Query 1", the reference-check query) remains in the model. It is harmless.

## Documentation-correction note
A later documentation pass changed text only: the p-value and forecast-bound wording in notebooks 03 and 04, `docs/findings.md` (finding 7), `docs/monitoring_policy.md` and `docs/PLAYBOOK.md`. No SQL, Python module, measure, relationship, population or the `.pbix` was changed. Checks run in that pass: the Mann–Whitney test and the notebook 04 walk-forward backtest were rebuilt from the raw CSV files (seasonal-naive reproduced exactly; Holt-Winters came out at WAPE 0.2312 and bias +2.46 with the current library build, against the recorded 0.2310 and +2.44, so the recorded values are quoted); the edited notebooks were checked for valid JSON and for Python syntax. The notebooks were not re-executed against PostgreSQL and pytest was not run (no database was available).
