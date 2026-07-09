-- QUESTION: How do orders distribute across the status funnel (all placed orders, not just delivered)?
SELECT
    order_status,
    COUNT(*) AS orders,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct
FROM analytics.fact_orders
GROUP BY order_status
ORDER BY orders DESC;
