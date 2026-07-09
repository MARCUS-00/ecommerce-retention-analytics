-- Feeds the Customers & Retention page. Person grain (customer_unique_id, not the
-- order-scoped customer_id - MASTER_DOC section 8's trap) with is_repeat precomputed so
-- DAX stays a simple DISTINCTCOUNT (MASTER_DOC section 15).
DROP VIEW IF EXISTS analytics.vw_customers;

CREATE VIEW analytics.vw_customers AS
SELECT
    c.customer_unique_id,
    COUNT(DISTINCT o.order_id) AS delivered_orders,
    SUM(oi.price + oi.freight_value) AS lifetime_revenue,
    MIN(o.order_purchase_timestamp) AS first_order,
    MAX(o.order_purchase_timestamp) AS last_order,
    (COUNT(DISTINCT o.order_id) >= 2) AS is_repeat
FROM analytics.fact_orders o
JOIN analytics.dim_customers c USING (customer_id)
JOIN analytics.fact_order_items oi USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id;
