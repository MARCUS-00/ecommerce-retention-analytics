-- QUESTION: Which customer states have the highest late-delivery rates?
SELECT
    c.customer_state AS state,
    COUNT(*) AS delivered_orders,
    COUNT(*) FILTER (WHERE o.is_late) AS late_orders,
    ROUND(100.0 * COUNT(*) FILTER (WHERE o.is_late) / COUNT(*), 2) AS late_pct
FROM analytics.fact_orders o
JOIN analytics.dim_customers c USING (customer_id)
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
HAVING COUNT(*) >= 30
ORDER BY late_pct DESC;
