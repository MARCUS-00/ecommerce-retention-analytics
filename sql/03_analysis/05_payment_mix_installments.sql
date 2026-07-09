-- QUESTION: What payment methods do customers use, and how much do they rely on installments?
SELECT
    payment_type,
    COUNT(*) AS payment_records,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS share_pct,
    ROUND(AVG(payment_installments), 2) AS avg_installments,
    SUM(payment_value) AS total_payment_value
FROM analytics.order_payments
GROUP BY payment_type
ORDER BY payment_records DESC;
