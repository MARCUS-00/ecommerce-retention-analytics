-- QUESTION: What does monthly cohort retention look like (person-level, delivered orders)?
WITH first_purchase AS (
    SELECT
        c.customer_unique_id,
        MIN(date_trunc('month', o.order_purchase_timestamp)) AS cohort_month
    FROM analytics.fact_orders o
    JOIN analytics.dim_customers c USING (customer_id)
    WHERE o.order_status = 'delivered'
    GROUP BY 1
),
activity AS (
    SELECT DISTINCT
        c.customer_unique_id,
        date_trunc('month', o.order_purchase_timestamp) AS activity_month
    FROM analytics.fact_orders o
    JOIN analytics.dim_customers c USING (customer_id)
    WHERE o.order_status = 'delivered'
)
SELECT
    f.cohort_month::date AS cohort,
    (EXTRACT(YEAR FROM age(a.activity_month, f.cohort_month)) * 12
        + EXTRACT(MONTH FROM age(a.activity_month, f.cohort_month)))::int AS month_offset,
    COUNT(DISTINCT a.customer_unique_id) AS active_customers
FROM first_purchase f
JOIN activity a USING (customer_unique_id)
GROUP BY 1, 2
ORDER BY 1, 2;
