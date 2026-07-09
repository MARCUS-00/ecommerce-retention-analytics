-- QUESTION: How has average order value (AOV) trended month over month?
WITH monthly_orders AS (
    SELECT
        date_trunc('month', o.order_purchase_timestamp)::date AS month,
        o.order_id,
        SUM(oi.price + oi.freight_value) AS order_revenue
    FROM analytics.fact_orders o
    JOIN analytics.fact_order_items oi USING (order_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1, 2
)
SELECT
    month,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(order_revenue) / COUNT(DISTINCT order_id), 2) AS aov
FROM monthly_orders
GROUP BY 1
ORDER BY 1;
