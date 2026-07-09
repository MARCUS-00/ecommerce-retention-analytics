-- Grain: 1 row per ORDER after dedup. Source can hold multiple reviews per order
-- (confirmed in Phase 2 validation: 547 orders, 789 repeated review_id values) - rule:
-- keep the latest by review_answer_timestamp, per MASTER_DOC section 8.
DROP TABLE IF EXISTS analytics.order_reviews CASCADE;

CREATE TABLE analytics.order_reviews AS
SELECT DISTINCT ON (order_id)
    review_id,
    order_id,
    review_score::int AS review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date::timestamp AS review_creation_date,
    review_answer_timestamp::timestamp AS review_answer_timestamp
FROM stg.order_reviews
ORDER BY order_id, review_answer_timestamp::timestamp DESC, review_id;

ALTER TABLE analytics.order_reviews ADD PRIMARY KEY (order_id);
ALTER TABLE analytics.order_reviews ADD FOREIGN KEY (order_id) REFERENCES analytics.fact_orders(order_id);
