-- QUESTION: How many orders had more than one review in the source data, before dedup?
SELECT
    COUNT(*) AS orders_with_multiple_reviews
FROM (
    SELECT order_id
    FROM stg.order_reviews
    GROUP BY order_id
    HAVING COUNT(*) > 1
) duplicated;
