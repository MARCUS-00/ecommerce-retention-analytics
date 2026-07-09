-- Grain: 1 row per zip prefix after dedup. Source has many rows per prefix (duplicate
-- lat/lng readings); decision: average lat/lng, take the most common city/state label.
DROP TABLE IF EXISTS analytics.geolocation CASCADE;

CREATE TABLE analytics.geolocation AS
SELECT
    geolocation_zip_code_prefix AS zip_code_prefix,
    AVG(geolocation_lat::numeric) AS avg_lat,
    AVG(geolocation_lng::numeric) AS avg_lng,
    MODE() WITHIN GROUP (ORDER BY geolocation_city) AS city,
    MODE() WITHIN GROUP (ORDER BY geolocation_state) AS state
FROM stg.geolocation
GROUP BY geolocation_zip_code_prefix;

ALTER TABLE analytics.geolocation ADD PRIMARY KEY (zip_code_prefix);
