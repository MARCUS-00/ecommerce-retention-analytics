# Findings

Format per finding: quantified observation -> business implication -> producing query/notebook
path (MASTER_DOC section 20). Every number here is reproducible by running the cited path
against this repository's pipeline output - none are estimated. This file is machine-written;
`docs/insights_memo.md` (human-authored, selects 5-7 of these and adds recommendations in the
builder's own voice) is a separate, later deliverable and is never written by this build
(MASTER_DOC section 4.3).

## 1. Repeat-purchase rate is 3.0%

Only 2,801 of 93,358 customers (by `customer_unique_id`, the person key) ever place a second
delivered order. Monthly cohort retention past month 0 is in the low single digits or zero for
essentially every cohort with a statistically meaningful size (hundreds to thousands of
customers).

**Implication:** this marketplace is acquisition-dependent, not retention-driven - the near-empty
retention curve is the finding, not a data gap.

**Source:** `sql/03_analysis/13_repeat_purchase_rate.sql`, `sql/03_analysis/12_cohort_retention_matrix.sql`, `notebooks/02_retention_rfm.ipynb`.

## 2. Late deliveries are associated with significantly and materially lower review scores

Late orders: median review score 2/5, 54.07% rated 1-2 stars (n=7,661). On-time orders: median
5/5, 9.22% rated 1-2 stars (n=88,163). Mann-Whitney U, one-sided (late < on-time), p ≈ 0.

**Implication:** delivery reliability is a measurable lever on customer satisfaction, not just an
operational metric in isolation - though this is an observational association, not proof of
causation (late delivery correlates with distance, seller, and freight cost).

**Source:** `notebooks/03_delivery_reviews.ipynb`, `sql/03_analysis/11_late_vs_review_score.sql`.

## 3. Late deliveries affect 8.11% of all delivered orders

7,826 of 96,478 delivered orders arrived after `order_estimated_delivery_date`.

**Implication:** quantifies the scale of the population behind finding #2 - roughly 1 in 12
delivered orders carries this satisfaction risk.

**Source:** `sql/04_dashboard_views/02_vw_orders.sql`, `sql/03_analysis/09_late_pct_by_month.sql`.

## 4. Top 5 of 74 categories generate 39.25% of delivered revenue

`health_beauty` (9.16%), `watches_gifts` (8.20%), `bed_bath_table` (7.95%), `sports_leisure`
(7.25%), and `computers_accessories` (6.70%) lead; the remaining 69 categories split the other
60.75%.

**Implication:** meaningful revenue concentration in a handful of categories - both a focus
opportunity (double down on what already works) and a concentration risk (a demand shock in any
one category has outsized impact).

**Source:** `sql/03_analysis/03_category_pareto.sql`.

## 5. Item-vs-payment totals reconcile within 0.30% of orders, and the gap is fully explained

303 of 99,441 orders (0.30%) show a >R$0.01 difference between summed item total
(price + freight) and summed payment total. Item-level revenue itself ties out **exactly** to
staging (15,843,553.24 both sides) - the mismatch is a source-data phenomenon (vouchers,
installment/split payments, cancellations), not an ETL error.

**Implication:** the standardized revenue definition (item price + freight, delivered orders) is
reconciled and defensible in front of a stakeholder who asks "why doesn't revenue match
payments received?"

**Source:** `sql/03_analysis/16_items_vs_payments_reconciliation.sql`, `docs/architecture.md`.

## 6. RFM segments show a small "Champions" group punching above its weight

"Lapsed One-Time" (58.29% of customers, 55.89% of revenue) and "Recent One-Time" (38.71%,
38.51%) dominate by construction (97% of customers buy exactly once or twice). "Champions"
(repeat, recent buyers) are only 1.29% of customers but 2.51% of revenue; "At-Risk Repeat"
customers are 1.71% of customers and 3.09% of revenue.

**Implication:** the largest addressable lever isn't the tiny existing repeat-buyer pool - it's
converting the 38.71%-strong "Recent One-Time" segment into second-time buyers, since that pool
is both large and still recent enough to be reachable.

**Source:** `notebooks/02_retention_rfm.ipynb`, `sql/03_analysis/14_rfm_customer_scores.sql`, `sql/03_analysis/15_rfm_segment_share.sql`.

## 7. The simple baseline forecast beat the more sophisticated model

In a 6-fold, 28-day walk-forward backtest, seasonal-naive (mean WAPE 0.2308) was not beaten by
Holt-Winters (0.2310) - WAPE is effectively tied, so the simpler model is preferred per the
acceptance rule. (Holt-Winters' bias, +2.44, is closer to zero than seasonal-naive's -10.14 -
a point in the fancier model's favor that WAPE alone doesn't capture, but not enough on its own
to overturn the tie on the headline metric.) The recommended 28-day forecast (2018-08-23 to
2018-09-19) is 6,660 orders, 95% empirical interval 3,585-9,943.

**Implication:** ops capacity planning should use the simple, auditable baseline - not a fancier
model that adds complexity without evidence of better accuracy - and should treat the wide
interval as a real signal of demand volatility, not a modeling weakness to hide.

**Source:** `notebooks/04_demand_forecast.ipynb`, `docs/monitoring_policy.md`.
