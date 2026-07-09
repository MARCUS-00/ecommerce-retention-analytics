-- QUESTION: How many customers and how much revenue fall into each RFM segment (r_score x f_bucket)?
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
),
scored AS (
    SELECT
        customer_unique_id,
        NTILE(5) OVER (ORDER BY last_order) AS r_score,
        CASE WHEN frequency = 1 THEN 1 WHEN frequency = 2 THEN 2 ELSE 3 END AS f_bucket,
        monetary
    FROM rfm
)
SELECT
    r_score,
    f_bucket,
    COUNT(*) AS customers,
    ROUND(SUM(monetary), 2) AS segment_revenue,
    ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 2) AS revenue_share_pct
FROM scored
GROUP BY r_score, f_bucket
ORDER BY r_score DESC, f_bucket DESC;
