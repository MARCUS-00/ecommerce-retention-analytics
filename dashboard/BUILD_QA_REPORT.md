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
| `ecommerce_retention_dashboard_final.pbix` | Authoritative report. 24,185,944 bytes. SHA-256 `16a2401e8e88350428442a2b349e397b22b9f647d02b9f2c638f985b51841560` (October 2026 presentation fix; see "Presentation fix, October 2026"). The previous version, SHA-256 `3361bc56936996c912274accf7997f527702e6b280161a8e260aa7d8c6c32f20`, is kept in `archive\` |
| `BUILD_QA_REPORT.md` | This report |
| `DAX_MEASURES_FINAL.md` | Final list of the 43 measures and the calculated column |
| `screenshots\page1_executive_overview.jpg`, `page2_sales_deep_dive.jpg`, `page3_customers_retention.jpg`, `page4_operations_satisfaction.jpg` | The four pages of the final file, exported with File → Export → PDF and cropped to the report canvas (see Limitations, item 9) |
| `BUILD_SPEC.md`, `dax_measures.md`, `exec_summary.xlsx` | Original project files, unchanged |

Superseded files are kept locally in `archive\` (ignored by Git, described in `archive\README.md`): the pre-polish backup `.pbix` (SHA-256 `8adaca54710ac82347597202ae83ad9c8e826b4525b288827da17ad9550f91db`), an older PBIP development project, a PBIP export of the final report, and the PBIP work copy used for the polish edits. None of them has been checked against the final report, and they are not part of the deliverable. A byte-identical duplicate of the final `.pbix` that used to sit next to it was removed in the release cleanup.

## Final pre-delivery audit
This audit worked from the files on disk and the raw data, not from earlier reports.

**Done**
- The final PBIX and its then-duplicate were byte-identical (`cmp`) with the same SHA-256, and the file passes a zip integrity test. The package contains 62 visual containers, 44 with alt text and 18 text boxes. The report locale is `en-US`.
- The saved final file was opened from disk in Power BI Desktop. All four pages rendered without errors or dialogs. Page 4 shows "p < 0.001" and the forecast note. Power BI was closed with "Don't save", and the file hash was unchanged afterwards.
- The Mann–Whitney test was re-run from the raw CSV files with pandas and SciPy 1.15.3 (see "p-value note").
- These figures were recomputed from `data/raw` and `data/processed`: 96,478 delivered orders; 96,470 of them with a delivery date; 7,826 late orders (8.11 % of 96,470); 93,358 customers by `customer_unique_id`, of whom 2,801 are repeat customers (3.00 %); a 28-day forecast total of 6,660 (sum of daily lower bounds 3,585, sum of daily upper bounds 9,943); 8 delivered orders without a delivery date, all 8 with a review.
- Page 4 is the only page that changed in the last edit. Its screenshot matches the live file.

**Not done in the audit**
- No new PostgreSQL refresh was run, because the audit made no model change. The last refresh is the one before the 2:18 PM save.
- The notebooks themselves were not re-executed. The test and the figures above were reproduced independently from the CSV files. Notebooks 03 and 04 were executed later, in the closure pass (see the closure note at the end of this report).
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
| Same n and U; SciPy again returns p = 0.0 | Re-run in this audit from the raw CSV files, with the notebook's population rebuilt in pandas (delivered orders, latest review per order, lateness from the delivery and estimate dates). At that point the notebook had not been re-executed and the database had not been queried; both were done in the closure pass (see the closure note at the end of this report) |
| Normal approximation, mean U = 337,708,371.5. Without tie correction: SD ≈ 2,322,387.6, z ≈ −80.5 | Calculated from the printed n and U |
| Normal approximation with tie correction (ratings are tied integers 1–5): SD ≈ 2,055,180.4, z ≈ −91.0 | Calculated in this audit from the re-run data |
| Effect size: late orders score lower in 77.7 % of late/on-time pairs (ties counted half); rank-biserial correlation 0.55 | Calculated in this audit |

At |z| of 80 or more, the one-sided p-value is far below 0.001 under any reasonable method. A normal approximation is not reliable far into the tail, so no tail probability is reported. The effect size, not the p-value, is the useful result at this sample size.

The notebook's original printed text said "p-value is effectively 0". In the documentation-correction pass, notebook 03's explanatory markdown and its printed p-value line were reworded to say p < 0.001 and to explain the underflow. The calculation and the statistical test are unchanged, and in the closure pass the notebook was executed in full against a rebuilt database, so its saved outputs now come from a real run.

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
2. The 28-day lower and upper cards (3,585 and 9,943) are sums of the daily 95 % bounds. They are **not** a 28-day prediction interval, and the page 4 note says so. Notebook 04 used to print the same sums as a "95% interval". Its print and log labels now read "sum of daily bounds ... (not a 28-day interval)" and a markdown cell explains the point. The forecast, the residual quantiles and the bounds themselves are unchanged, and in the closure pass the notebook was executed in full against a rebuilt database, so its saved outputs now come from a real run.
3. The Mann–Whitney statement on page 4 and the "roughly 97 % buy once" box on page 3 are static text, written from notebook 03 and the data at build time. They do not update on refresh.
4. RFM segment names are derived in DAX from the SQL R×F grid using the notebook 02 rules. SQL `NTILE` places ties at quintile boundaries arbitrarily, so another scoring method can move a few customers between segments (an earlier `pandas.qcut` version of notebook 02 gave 1,201 Champions instead of 1,204). Notebook 02 now reads the same query 15 grid, so its segment table matches the dashboard. Totals reconcile (93,358 customers, R$15,419,773.75).
5. Repeat Customer Rate is all-time, and the payment visuals and forecast ignore the sales slicers. All three are labelled on the pages.
6. Digit grouping is stored per file (English US), and the format strings (`#,0`, `\R\$#,0.00`) apply on any regional setting. An earlier version of the page 1 and page 3 KPI cards showed dots instead of commas at some zoom levels (R$15.419.773.75, 96.478); the cause and fix are under "Presentation fix, October 2026".
7. Accessibility is partial. Alt text, reading-order tab order and non-colour cues (data labels, dashed against solid lines) are in place. Contrast computed from the stored colours (WCAG 2 formula): the subtitles and footnotes that sit directly on the #F3F5F8 page background use #5B6472 (5.48:1, passes AA 4.5:1; until October 2026 they used #6B7280 at 4.43:1); #6B7280 grey on the white visual backgrounds is 4.83:1; dark text (#1F2937, 14.68:1) and navy (#1F3A5F, 11.48:1) pass. Not done: a screen-reader walk-through and a high-contrast theme test.
8. The page 4 reviewed-orders table is tight, and a thin scrollbar can appear. All five columns and all four rows, including Unknown, are visible. The page 4 cards are compact.
9. The four screenshots are File → Export → PDF renders of the saved final report (October 2026 version), rasterised and cropped to the report canvas (1600 px wide). The earlier window captures are kept locally in `archive\screenshots_pre_oct2026_fix\` and `archive\screenshots_original\`.
10. Pages 2 and 3 use custom page heights (960 and 900). The limit of six analytic visuals per page excludes KPI cards, slicers and text boxes.
11. The AOV line (page 2) and the late-delivery line (page 4) are drawn in the theme's default blue (#118DFF). The file also stores teal #2A9D8F and coral #E76F51 for them, but as a series-wide fill that line charts do not apply; Power BI Desktop's Format pane shows blue, matching the screenshots.
12. A saved DAX query tab ("Query 1", the reference-check query) remains in the model. It is harmless.

## Documentation-correction note
A later documentation pass changed text only: the p-value and forecast-bound wording in notebooks 03 and 04, `docs/findings.md` (finding 7), `docs/monitoring_policy.md` and `docs/PLAYBOOK.md`. No SQL, Python module, measure, relationship, population or the `.pbix` was changed. Checks run in that pass: the Mann–Whitney test and the notebook 04 walk-forward backtest were rebuilt from the raw CSV files (seasonal-naive reproduced exactly; Holt-Winters came out at WAPE 0.2312 and bias +2.46 with the current library build, against the recorded 0.2310 and +2.44, so the recorded values are quoted); the edited notebooks were checked for valid JSON and for Python syntax.

## Closure note
A final closure pass checked the notebooks by running them.

- **Environment:** a throwaway PostgreSQL 16.2 was created outside the repository, and the pipeline (`python -m src.run_pipeline`) was run on a copy of the repository against the raw CSV files. Ingest, input validation, transform and output validation all passed (0 blocking failures). The Python was 3.10.12 with the pinned library versions (pandas 2.2.3, SciPy 1.13.1, statsmodels 0.14.6), not the 3.12 used for the original build.
- **Tests:** `pytest` ran against that database: 10 passed.
- **Notebooks 03 and 04:** executed top to bottom without errors. Their source cells are identical to the committed ones, and the printed text outputs are identical to the previously saved ones, apart from log timestamps: n = 7,661 / 88,163, U = 150,706,850.5, the 54.07 % / 9.22 % shares, WAPE 0.2308 and 0.2310, bias -10.14 and +2.44, a forecast of 6,660 and summed daily bounds of 3,585-9,943. This time Holt-Winters reproduced exactly (the earlier pandas rebuild had differed by about 0.0002 in WAPE). The executed copies are the ones now committed, replacing outputs that had been edited by hand earlier in the documentation pass.
- **Saved results:** `python -m src.run_analysis` regenerated all 18 SQL output files, and the executed notebook 04 regenerated `forecast_28d.csv`. All 19 files match the committed versions byte for byte once line endings are ignored.
- **Derived figures quoted in the notebook text** (tie-corrected z of about -91, untied z of about -80.5, effect size 77.7 % and 0.55, residual quantiles -109.8 and +117.3, fold total misses from -2,363 to +731) were recomputed on the rebuilt database and match.
- **Not covered:** the Power BI report was not refreshed or reopened in this pass, and nothing was run on the Windows machine or under Python 3.12. Notebooks 01 and 02 were executed later, in the release pass below.

## Release verification record
The final release pass repeated the checks in a throwaway PostgreSQL 16.2 database outside the repository (Linux, Python 3.10.12, the pinned libraries, the raw CSV files in `data/raw`; no Kaggle download). Each line says what was done and whether it passed.

| Check | Result |
|---|---|
| `python -m src.run_pipeline` (ingest, input checks, transform, output checks) | **Pass.** 0 blocking failures |
| `pytest` (10 tests) | **Pass.** 10 passed |
| `python -m src.run_analysis` (18 SQL outputs) and `forecast_28d.csv` | **Pass.** Identical to the committed files once line endings are ignored |
| Dashboard views (`vw_sales`, `vw_orders`, `vw_customers`, `vw_daily_orders`) | **Pass.** 110,197, 96,478, 93,358 and 634 rows. Line revenue sums to R$15,419,773.75, with 7,826 late of 96,478 delivered orders and 2,801 repeat of 93,358 customers |
| Notebooks 01 to 04 executed top to bottom | **Pass.** Source cells identical, printed outputs identical apart from timestamps. Only 03 and 04 outputs were replaced in the repository (closure pass); 01 and 02 already matched |
| Derived figures quoted in notebook text (z, effect size, residual quantiles, fold misses) | **Pass.** Recomputed independently |
| `exec_summary.xlsx` rebuilt with `make excel` logic | **Pass with a note.** The pivot sheets are identical. The "Raw Extract" sheet takes the first 5,000 rows of an unordered query (`src/build_excel_summary.py`), so its row selection can differ between runs. It is a sample, not an exact extract. The code was not changed |
| Final `.pbix` opened in Power BI Desktop | **Pass in the pre-delivery audit.** Repeated for the October 2026 version (see below) |
| Power BI refresh against the Docker database | **Not performed in this pass.** Last refresh was before the 2:18 PM IST save on 9 October 2026 |
| Docker Compose, md5 authentication and the `make` targets on Windows | **Not performed.** The scratch run used a local PostgreSQL 16.2, not the Docker container |
| Kaggle download and GitHub Actions CI | **Not performed.** No Kaggle credentials were used and nothing was pushed |

Release cleanup in the same pass: the duplicate `ecommerce_retention_dashboard.pbix` was removed, the superseded dashboard files were moved to `dashboard/archive/` (local only), and stale zero-byte Git lock files, leftover temporary object files and Python and pytest caches were deleted. `docs/MASTER_DOC.md` stays where it is, as the design record that other documents cite by section number. `docs/BLUEPRINT.md`, a trimmed planning extract, was removed from the working tree in the October 2026 release review and remains in Git history.

## Presentation fix, October 2026
**Problem.** On pages 1 and 3 the KPI cards sometimes showed dots where commas belong (R$15.419.773.75, 96.478, 93.358) while the page 4 cards showed commas. It depended on zoom: the same card could show commas at 70 % and dots at 78 % or 110 %.

**Cause.** Not the number format and not the locale. All affected measures use `#,0` or `\R\$#,0.00`, the report locale is en-US, and no card overrides the format. The eight affected cards are 78 px high with the default padding (16 px bottom); the 18 pt value fills that space, so its bottom edge is clipped and each comma loses its tail and looks like a dot. The page 4 cards are 80 px high, which is enough. Setting the cards to 80 px helped in some views but did not survive reopening the file, so it was rejected.

**Fix.** Bottom padding of 8 px on the eight 78 px KPI cards (page 1: Total Revenue, Total Orders, AOV, Revenue MoM Growth; page 3: Customers, Repeat customers, One-time customers, Repeat Customer Rate). Heights, positions, fonts and measures are unchanged. In the same release:
- the subtitles and footnotes that sit directly on the page background were recoloured from #6B7280 to #5B6472 (seven text boxes: page subtitles on pages 1 to 4 and the footnotes on pages 1 to 3);
- the page 3 footnote now reads "... Ties at a score boundary are placed arbitrarily. Alternative RFM scoring methods can produce slightly different segment counts. ...". The previous wording pointed at notebook 02, which now reads the same query 15 grid as the report.

**Verification.**
- Edits were made in Power BI Desktop on a copy of the approved file. After each save the file on disk was checked for a new modification time, size, SHA-256 and a clean zip test.
- The saved copy was closed, reopened from disk and inspected on all four pages: page 1 and page 3 cards show commas at 70 %, 78 %/80 % and 110 % zoom and after switching pages. Page 2 and page 4 render unchanged.
- One slicer was checked: customer state AL on page 1 gives R$94,172.49 revenue and R$237.21 AOV, matching the model data.
- Package comparison with the previous version: only card padding, seven text colours, the page 3 footnote wording and Power BI's automatic schema-version updates differ. All 43 measures (formulas, formats, folders), 8 calculated columns, 2 calculated tables, 3 relationships, 9 Power Query queries, all column settings and every data row in the 11 tables are identical.
- The rendered subtitle colour in the exported report is RGB 91, 100, 114 (#5B6472).
- The promoted file was reopened from its final path and the page 1 and page 3 cards and footnote were checked again.

**Not done.** No refresh against the Docker database (the cached data were not changed), only one slicer checked, no screen-reader test.

## Release verification, October 2026
Checks run on the release files before publishing. Environment: Linux, Python 3.12.3 with the pinned `requirements.txt` (versions matched exactly, `pip check` clean), PostgreSQL 16.15 in a disposable local cluster, and the nine raw CSV files (SHA-256 identical to the project copies).

**Executed**
- `src/run_pipeline.py` on the full data: input validation passed with 0 blocking failures and 9 logged anomalies; output validation passed with 0 blocking failures and 1 logged anomaly.
- `pytest`: 10 passed. `compileall` and `pyflakes` on `src/` and `tests/`: clean.
- `src/run_analysis.py`: all 18 saved results in `sql/03_analysis/outputs/` were reproduced byte for byte. `src/build_dashboard_views.py` and `src/build_excel_summary.py` ran without errors.
- Notebooks 01-04 executed top to bottom without errors. Notebook 04 reproduced `data/processed/forecast_28d.csv` byte for byte; seasonal-naive WAPE 0.2308, Holt-Winters WAPE 0.2310 and a 6,660-order forecast. This run printed a Holt-Winters bias of +2.46 against the saved +2.44, the library-numerics difference described above; the saved value is quoted in the documents.
- KPI reconciliation from the views: revenue R$15,419,773.75; 96,478 delivered orders; AOV R$159.83; 7,826 late orders (8.11%) and 8 without a delivery date; 93,358 customers, 2,801 repeat (3.00%), 90,557 one-time (97.00%); top-5 category share 39.25% of 74 categories; top-10 seller share 12.93%; 103,886 payment records totalling R$16,008,872.12; 7,661 late and 88,163 on-time reviewed orders. Notebook 02 now returns 1,204 Champions (2.52% of revenue) and 55.88% for Lapsed One-Time, matching the dashboard query.
- The final `.pbix` hash was compared with the approved value (`16a2401e...1560`) and the package passed a zip test (81 entries). A copy re-saved in Power BI Desktop after the last commit (different `DataModel` and `SecurityBindings` parts, identical report layout) was kept in the local archive, and the verified file was restored.

**Not verified in this review**
- A full run on Windows with Docker Desktop and GNU Make, the Kaggle download, and a Power BI refresh against the Docker database.
- Slicer interactions beyond the single slicer checked earlier, and a screen-reader test.
- The Power BI Desktop reopening and the GitHub Actions result, which could only be done after publication, are recorded in the next section.

## Post-publication checks, 16 October 2026
Run after release commit `972c5f7` was pushed to `origin/main`.

- **GitHub Actions:** the CI workflow run for `972c5f7` completed successfully (synthetic-fixture pipeline and the 10 tests; the notebooks are not part of CI).
- **Power BI Desktop on Windows:** a disposable copy of the final `.pbix` (same SHA-256 as the repository file) was opened and all four pages were inspected. The page 1 cards showed R$15,419,773.75, 96,478, R$159.83 and -4.1% with no clipped separators. Values on pages 2 to 4 matched this report: top-10 seller share 12.93%; 93,358 customers, 2,801 repeat, 90,557 one-time and a 3.00% repeat rate; month-1 retention 0.48%; late rate 8.11% on 7,826 orders; RFM shares as published; and the 6,660-order forecast with the note that summed daily bounds are not a 28-day interval. The copy was closed without saving and its hash was unchanged. No data refresh was run.
- **Published file:** the `.pbix` downloaded from the public repository has SHA-256 `16a2401e8e88350428442a2b349e397b22b9f647d02b9f2c638f985b51841560`, identical to the local file. The README, its four screenshots and its documentation links were loaded on github.com and resolved.
- **Report structure:** the saved report has 4 pages, 44 visuals (excluding text boxes) and 18 text boxes, matching the rebuild guide.

**Still not verified:** a full run on Windows with Docker Desktop and GNU Make, the Kaggle download, a refresh against the Docker database, and a screen-reader test.
