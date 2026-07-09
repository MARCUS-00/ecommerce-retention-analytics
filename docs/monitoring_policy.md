# Forecast Monitoring Policy

Module A (28-day demand forecast, `notebooks/04_demand_forecast.ipynb`). This is a **written
policy only** - nothing here is deployed or automated. The data is frozen (2016-2018 Olist
history); there is no live pipeline feeding new orders into this forecast. The policy states
what a team running this in production would do, and the exact thresholds are set from this
project's own walk-forward backtest, not arbitrary round numbers.

## Backtest result and current recommendation

Walk-forward backtest (MASTER_DOC section 14): expanding-origin, 6 folds x 28 days, over the
stable window `2017-01-05` to `2018-08-22`.

| Model | Mean WAPE | Mean bias |
|---|---|---|
| Seasonal naive (repeat last observed week) | **0.2308** | -10.14 |
| Holt-Winters (additive, weekly seasonality) | 0.2310 | +2.44 |

**Verdict: seasonal naive wins** (Holt-Winters does not beat it - a 0.1% WAPE difference,
within noise). Per the acceptance rule (MASTER_DOC section 14), the baseline itself is the
reported recommendation. This is a legitimate, stated outcome, not a failure to find a better
model - see `notebooks/04_demand_forecast.ipynb` for the full backtest table and chart.

## Refit cadence

Refit (recompute the seasonal-naive reference week and re-run the walk-forward backtest)
**every 28 days**, immediately after each forecast horizon's actuals become available - the
same cadence as the forecast horizon itself, so the reference week never lags real demand by
more than one cycle.

## Investigation triggers

Both thresholds are derived from this backtest's own fold-level spread (mean + 1 standard
deviation across the 6 folds), not picked arbitrarily:

| Signal | Backtest mean | Backtest std | Investigate if... |
|---|---|---|---|
| Rolling WAPE | 0.231 | 0.110 | rolling WAPE > **0.34** |
| \|bias\| | 27.8 (mean absolute) | 40.0 | \|bias\| > **70 orders/day** |

If either trigger fires: (1) re-run the walk-forward backtest on the latest data to see if the
seasonal-naive-vs-Holt-Winters verdict has flipped: MASTER_DOC section 14's acceptance rule
applies fresh each time, not as a one-time decision; (2) check for a known event (promotional
spike, outage, marketplace policy change) before concluding the underlying demand pattern has
shifted; (3) if no model beats seasonal naive and the trigger persists across two consecutive
cycles, escalate to Ops as a capacity-planning risk rather than silently continuing to publish
a degraded forecast.

## Why no SARIMA / deployed monitoring dashboard

- **SARIMA** was in scope as an option for proper prediction intervals (MASTER_DOC section 14
  technique ladder, step 3), but the simplification escape hatch - Holt-Winters point forecasts
  plus empirical intervals from walk-forward residual quantiles - was used instead, since
  Holt-Winters didn't even beat the naive baseline; investing in SARIMA's residual-diagnostics
  tuning for a model that loses to the simplest baseline would be complexity without evidence.
- **A model-monitoring dashboard** is explicitly out of scope (MASTER_DOC section 4.3's rejected
  register): nothing is deployed, so there is nothing to monitor live. This document plus the
  backtest chart in the notebook achieves the legitimate goal (a documented plan for what to
  watch and when to act) without building unused infrastructure.

## Limitations (state plainly, per MASTER_DOC section 21)

- Only ~20 months of history and one observed annual cycle - seasonal patterns beyond a weekly
  cycle (e.g. year-over-year Black-Friday-style effects) are not modeled with any confidence.
  Black Friday 2017 (2017-11-24, ~6x normal volume) sits in every fold's training data but was
  never in a held-out test window (the earliest backtest fold starts 2018-03-08, 104 days
  after that spike) - so the backtest doesn't tell us how either model would handle a similar
  event landing inside a forecast horizon.
- If the marketplace enters a structurally different regime (new seller onboarding wave, a
  platform-level policy change, a macroeconomic shock) this forecast should not be trusted
  until the backtest is re-run against data from that new regime.
