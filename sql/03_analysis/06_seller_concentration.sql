-- QUESTION: How concentrated is GMV among top sellers (top-10 share of total)?
WITH seller_revenue AS (
    SELECT
        oi.seller_id,
        SUM(oi.price + oi.freight_value) AS revenue
    FROM analytics.fact_orders o
    JOIN analytics.fact_order_items oi USING (order_id)
    WHERE o.order_status = 'delivered'
    GROUP BY oi.seller_id
),
ranked AS (
    SELECT
        seller_id,
        revenue,
        ROW_NUMBER() OVER (ORDER BY revenue DESC) AS revenue_rank
    FROM seller_revenue
)
SELECT
    seller_id,
    revenue,
    revenue_rank,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue_rank) / SUM(revenue) OVER (), 2) AS cumulative_share_pct
FROM ranked
ORDER BY revenue_rank
LIMIT 10;
