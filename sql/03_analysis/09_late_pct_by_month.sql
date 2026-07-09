-- QUESTION: How has the late-delivery rate trended month over month?
SELECT
    date_trunc('month', order_purchase_timestamp)::date AS month,
    COUNT(*) AS delivered_orders,
    COUNT(*) FILTER (WHERE is_late) AS late_orders,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_late) / COUNT(*), 2) AS late_pct
FROM analytics.fact_orders
WHERE order_status = 'delivered'
GROUP BY 1
ORDER BY 1;
