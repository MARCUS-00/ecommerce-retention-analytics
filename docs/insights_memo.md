# Olist Marketplace: Revenue, Retention and Delivery

**Executive Insights Memo**

**To:** Leadership: CFO, CMO, Head of Operations  
**From:** Manoj Kumar  
**Re:** Annual planning: what the order data says, and what to do next  
**Data:** Olist public marketplace dataset (Kaggle), 2016-2018; 99,441 orders, 96,478 delivered  

## Business problem

Leadership asked three questions before annual planning: where revenue comes from, whether customers come back, and whether delivery performance measurably affects satisfaction. This memo answers them from the project's validated pipeline. Every figure is reproducible from the repository (source paths in docs/findings.md).

## Key findings

| Finding | Evidence | What it means |
|---|---|---|
| **Customers rarely return** | Only 3.0% of customers (2,801 of 93,358) placed a second delivered order. | Growth depends on winning new customers. The near-empty retention curve is itself the finding. |
| **Late delivery goes with much lower reviews** | 8.11% of delivered orders (7,826 of 96,478) arrived late. Late orders: median review 2 of 5, 54.07% rated 1-2 stars. On-time orders: median 5 of 5, 9.22% rated 1-2 stars. Mann-Whitney U, p < 0.001. | Delivery reliability is a lever on satisfaction. This is an association, not proof that lateness causes the low scores. |
| **Lateness is uneven** | Late rate peaked at 21.36% in March 2018 (months with 500+ deliveries). By state it ranges from 2.88% (RO) to 23.93% (AL). | Late rates vary widely by period and region, so effort can be targeted. |
| **Revenue leans on a few categories** | The top 5 of 74 categories earn 39.25% of delivered revenue (health_beauty 9.16%, watches_gifts 8.20%, bed_bath_table 7.95%, sports_leisure 7.25%, computers_accessories 6.70%). The top 10 sellers earn 12.93%. | Category concentration is both a strength and a risk. Seller concentration is modest. |
| **The growth pool is recent one-time buyers** | 97% of customers buy once or twice. "Recent One-Time" buyers are 38.71% of customers and 38.51% of revenue; "Champions" are 1.29% of customers and 2.51% of revenue. | The reachable pool for repeat purchase is the recent one-time group, not the tiny repeat-buyer base. |
| **A simple forecast is good enough** | In a 6-fold, 28-day backtest, seasonal-naive (WAPE 0.2308) tied Holt-Winters (0.2310). Forecast for 2018-08-23 to 2018-09-19: 6,660 orders. | Plan capacity on the simple, auditable baseline. Summed daily bounds (3,585-9,943) are not a 28-day interval; the six backtest totals missed by -2,363 to +731 orders. |

## Recommendations

1. **Test, then scale, a second-purchase offer.** Pilot it on recent one-time buyers with a hold-out group, and judge it on repeat rate against that hold-out before any wider rollout.
2. **Make on-time delivery a tracked KPI.** Report the late rate by state and by month, start with the worst regions (for example AL and MA) and the peak-demand months, and review the sellers and carriers behind them.
3. **Check the cause before investing.** Compare late and on-time orders while controlling for distance, seller and freight cost. Lateness may be partly a proxy for those factors.
4. **Watch the top categories.** Monitor stock and delivery performance in the five lead categories, since a shock there moves a large share of revenue.
5. **Use the forecast as a planning baseline, not a commitment.** Plan for a wide range of daily demand, refit every 28 days, and investigate if rolling WAPE exceeds 0.34 or bias exceeds 70 orders per day (docs/monitoring_policy.md).

## Limitations

- Findings are observational. They show association, not cause, and no experiment was run.
- The data is one marketplace, 2016-2018. About 20 months of history means one annual cycle, and Black Friday 2017 was never in a held-out backtest window.
- The dataset has no costs or margins, so this memo makes no profit or financial-impact estimate.
- The retention figure counts repeat orders on this marketplace only, and the forecast is a method demonstration on frozen data.
