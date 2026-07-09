DROP TABLE IF EXISTS analytics.dim_sellers CASCADE;

CREATE TABLE analytics.dim_sellers AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM stg.sellers;

ALTER TABLE analytics.dim_sellers ADD PRIMARY KEY (seller_id);
