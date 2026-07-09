-- Grain: 1 row per customer_id (ORDER-scoped). customer_unique_id is the PERSON key -
-- all retention/repeat/RFM math joins through it, never through customer_id.
DROP TABLE IF EXISTS analytics.dim_customers CASCADE;

CREATE TABLE analytics.dim_customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM stg.customers;

ALTER TABLE analytics.dim_customers ADD PRIMARY KEY (customer_id);
