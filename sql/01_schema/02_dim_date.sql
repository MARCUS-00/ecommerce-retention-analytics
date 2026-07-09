-- Generated calendar table, not derived from stg.*. Range covers the full observed
-- purchase/delivery/estimated-delivery window (2016-09 to 2018-11) with margin.
DROP TABLE IF EXISTS analytics.dim_date CASCADE;

CREATE TABLE analytics.dim_date AS
SELECT
    d::date AS date,
    EXTRACT(YEAR FROM d)::int AS year,
    EXTRACT(MONTH FROM d)::int AS month,
    TRIM(TO_CHAR(d, 'Day')) AS weekday,
    EXTRACT(ISODOW FROM d) IN (6, 7) AS is_weekend
FROM generate_series('2016-01-01'::date, '2018-12-31'::date, '1 day'::interval) AS d;

ALTER TABLE analytics.dim_date ADD PRIMARY KEY (date);
