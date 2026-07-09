-- delivery_days/is_late are NULL for orders never delivered (no delivered_customer_date) -
-- deliberately not coerced to a false "on time", since the comparison genuinely doesn't apply.
DROP TABLE IF EXISTS analytics.fact_orders CASCADE;

CREATE TABLE analytics.fact_orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::timestamp AS order_purchase_timestamp,
    order_approved_at::timestamp AS order_approved_at,
    order_delivered_carrier_date::timestamp AS order_delivered_carrier_date,
    order_delivered_customer_date::timestamp AS order_delivered_customer_date,
    order_estimated_delivery_date::timestamp AS order_estimated_delivery_date,
    EXTRACT(DAY FROM (order_delivered_customer_date::timestamp - order_purchase_timestamp::timestamp))::int AS delivery_days,
    (order_delivered_customer_date::timestamp > order_estimated_delivery_date::timestamp) AS is_late
FROM stg.orders;

ALTER TABLE analytics.fact_orders ADD PRIMARY KEY (order_id);
ALTER TABLE analytics.fact_orders ADD FOREIGN KEY (customer_id) REFERENCES analytics.dim_customers(customer_id);
CREATE INDEX idx_fact_orders_purchase_ts ON analytics.fact_orders(order_purchase_timestamp);
