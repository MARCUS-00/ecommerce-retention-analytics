-- QUESTION: Which orders' item totals don't match their payment totals, and by how much?
WITH item_totals AS (
    SELECT order_id, SUM(price + freight_value) AS item_total
    FROM analytics.fact_order_items
    GROUP BY order_id
),
payment_totals AS (
    SELECT order_id, SUM(payment_value) AS payment_total
    FROM analytics.order_payments
    GROUP BY order_id
)
SELECT
    o.order_id,
    i.item_total,
    p.payment_total,
    ROUND(p.payment_total - i.item_total, 2) AS diff
FROM analytics.fact_orders o
JOIN item_totals i USING (order_id)
JOIN payment_totals p USING (order_id)
WHERE ABS(p.payment_total - i.item_total) > 0.01
ORDER BY ABS(p.payment_total - i.item_total) DESC, o.order_id;
