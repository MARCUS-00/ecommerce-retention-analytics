-- QUESTION: Where is revenue concentrated geographically, by customer state?
WITH state_revenue AS (
    SELECT
        c.customer_state AS state,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.price + oi.freight_value) AS revenue
    FROM analytics.fact_orders o
    JOIN analytics.fact_order_items oi USING (order_id)
    JOIN analytics.dim_customers c USING (customer_id)
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_state
)
SELECT
    state,
    orders,
    revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS revenue_share_pct
FROM state_revenue
ORDER BY revenue DESC;
