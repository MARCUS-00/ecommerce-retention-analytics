-- QUESTION: What share of customers ever place more than one delivered order?
WITH orders_per_customer AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS delivered_orders
    FROM analytics.fact_orders o
    JOIN analytics.dim_customers c USING (customer_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE delivered_orders >= 2) AS repeat_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE delivered_orders >= 2) / COUNT(*), 2) AS repeat_pct
FROM orders_per_customer;
