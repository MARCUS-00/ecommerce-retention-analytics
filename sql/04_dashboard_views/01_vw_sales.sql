-- Feeds the Executive Overview and Sales Deep-Dive pages. Delivered item lines only,
-- with line_revenue precomputed so Power BI's DAX stays a simple SUM (MASTER_DOC section 15).
-- order_date (DATE) is exposed alongside order_purchase_timestamp because Power BI's
-- date-table relationship needs a DATE-to-DATE match - relating to a TIMESTAMP column
-- with a time component silently fails to join any rows.
DROP VIEW IF EXISTS analytics.vw_sales;

CREATE VIEW analytics.vw_sales AS
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    p.product_category_name_english,
    c.customer_state,
    c.customer_unique_id,
    o.order_purchase_timestamp,
    o.order_purchase_timestamp::date AS order_date,
    (oi.price + oi.freight_value) AS line_revenue
FROM analytics.fact_order_items oi
JOIN analytics.fact_orders o USING (order_id)
JOIN analytics.dim_products p USING (product_id)
JOIN analytics.dim_customers c USING (customer_id)
WHERE o.order_status = 'delivered';
