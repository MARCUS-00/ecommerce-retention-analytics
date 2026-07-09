-- QUESTION: Do late deliveries receive lower review scores than on-time deliveries?
SELECT
    o.is_late,
    COUNT(*) AS reviewed_orders,
    ROUND(AVG(r.review_score), 2) AS avg_review_score,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY r.review_score) AS median_review_score,
    ROUND(100.0 * COUNT(*) FILTER (WHERE r.review_score <= 2) / COUNT(*), 2) AS pct_1_2_star
FROM analytics.fact_orders o
JOIN analytics.order_reviews r USING (order_id)
WHERE o.order_status = 'delivered'
  AND o.is_late IS NOT NULL
GROUP BY o.is_late
ORDER BY o.is_late;
