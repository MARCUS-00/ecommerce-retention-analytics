-- Feeds the Operations & Satisfaction page. Delivered orders only, with is_late and
-- delivery_days already derived in fact_orders, and review_score joined in (LEFT JOIN -
-- not every delivered order has a review) so the late-vs-review comparison needs no extra
-- relationships in the Power BI model (MASTER_DOC section 15).
-- order_date (DATE) is exposed for the same reason as vw_sales: Power BI's date-table
-- relationship needs a DATE-to-DATE match, not a match against a TIMESTAMP column.
DROP VIEW IF EXISTS analytics.vw_orders;

CREATE VIEW analytics.vw_orders AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_state,
    o.order_purchase_timestamp,
    o.order_purchase_timestamp::date AS order_date,
    o.delivery_days,
    o.is_late,
    o.order_estimated_delivery_date,
    o.order_delivered_customer_date,
    r.review_score
FROM analytics.fact_orders o
JOIN analytics.dim_customers c USING (customer_id)
LEFT JOIN analytics.order_reviews r USING (order_id)
WHERE o.order_status = 'delivered';
