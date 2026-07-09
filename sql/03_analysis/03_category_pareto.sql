-- QUESTION: What share of revenue do the top product categories generate (Pareto concentration)?
WITH category_revenue AS (
    SELECT
        COALESCE(p.product_category_name_english, 'unknown') AS category,
        SUM(oi.price + oi.freight_value) AS revenue
    FROM analytics.fact_orders o
    JOIN analytics.fact_order_items oi USING (order_id)
    JOIN analytics.dim_products p USING (product_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1
)
SELECT
    category,
    revenue,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 2) AS revenue_share_pct,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC) / SUM(revenue) OVER (), 2) AS cumulative_share_pct
FROM category_revenue
ORDER BY revenue DESC;
