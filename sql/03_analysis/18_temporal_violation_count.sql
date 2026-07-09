-- QUESTION: How many orders have impossible timestamp orderings in their delivery lifecycle?
SELECT
    COUNT(*) FILTER (
        WHERE order_delivered_carrier_date IS NOT NULL AND order_approved_at IS NOT NULL
        AND order_delivered_carrier_date < order_approved_at
    ) AS carrier_before_approved,
    COUNT(*) FILTER (
        WHERE order_delivered_customer_date IS NOT NULL AND order_delivered_carrier_date IS NOT NULL
        AND order_delivered_customer_date < order_delivered_carrier_date
    ) AS customer_before_carrier,
    COUNT(*) FILTER (
        WHERE order_status = 'canceled' AND order_delivered_customer_date IS NOT NULL
    ) AS canceled_with_delivery_date
FROM analytics.fact_orders;
