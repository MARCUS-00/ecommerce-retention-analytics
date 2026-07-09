-- QUESTION: How does each customer score on recency, frequency, and monetary value (RFM)?
-- Frequency is bucketed 1 / 2 / 3+ rather than NTILE(5): most customers buy exactly once, so a
-- frequency quintile would be tie-dominated and NTILE would split identical values arbitrarily.
WITH rfm AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp)::date AS last_order,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price + oi.freight_value) AS monetary
    FROM analytics.fact_orders o
    JOIN analytics.dim_customers c USING (customer_id)
    JOIN analytics.fact_order_items oi USING (order_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    customer_unique_id,
    NTILE(5) OVER (ORDER BY last_order) AS r_score,
    CASE WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 2 ELSE 3 END AS f_bucket,
    NTILE(5) OVER (ORDER BY monetary) AS m_score
FROM rfm;
