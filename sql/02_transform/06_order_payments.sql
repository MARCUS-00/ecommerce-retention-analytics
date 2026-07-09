-- Grain: 1 row per payment record. Multiple rows per order are legitimate
-- (installments, mixed payment methods, vouchers) - no dedup here.
DROP TABLE IF EXISTS analytics.order_payments CASCADE;

CREATE TABLE analytics.order_payments AS
SELECT
    order_id,
    payment_sequential::int AS payment_sequential,
    payment_type,
    payment_installments::int AS payment_installments,
    payment_value::numeric AS payment_value
FROM stg.order_payments;

ALTER TABLE analytics.order_payments ADD PRIMARY KEY (order_id, payment_sequential);
ALTER TABLE analytics.order_payments ADD FOREIGN KEY (order_id) REFERENCES analytics.fact_orders(order_id);
