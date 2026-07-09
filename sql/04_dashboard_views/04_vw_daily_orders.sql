-- Feeds the forecast band on the Operations page. ALL placed orders, not just delivered -
-- ops must plan capacity for every order regardless of eventual status (MASTER_DOC section 15).
DROP VIEW IF EXISTS analytics.vw_daily_orders;

CREATE VIEW analytics.vw_daily_orders AS
SELECT
    order_purchase_timestamp::date AS order_date,
    COUNT(*) AS orders
FROM analytics.fact_orders
GROUP BY 1;
