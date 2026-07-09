-- QUESTION: What does the distribution of delivery time (purchase to customer receipt) look like?
SELECT
    delivery_days,
    COUNT(*) AS orders
FROM analytics.fact_orders
WHERE order_status = 'delivered'
  AND delivery_days IS NOT NULL
GROUP BY delivery_days
ORDER BY delivery_days;
