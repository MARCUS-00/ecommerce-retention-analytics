-- QUESTION: What is monthly revenue, and how fast is it growing or shrinking month over month?
WITH monthly AS (
    SELECT
        date_trunc('month', o.order_purchase_timestamp)::date AS month,
        SUM(oi.price + oi.freight_value) AS revenue
    FROM analytics.fact_orders o
    JOIN analytics.fact_order_items oi USING (order_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    month,
    revenue,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 1) AS mom_growth_pct
FROM monthly
ORDER BY month;
