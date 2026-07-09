-- English category joined from the translation table; falls back to the Portuguese
-- name when no translation exists (a handful of categories are untranslated in source).
DROP TABLE IF EXISTS analytics.dim_products CASCADE;

CREATE TABLE analytics.dim_products AS
SELECT
    p.product_id,
    COALESCE(t.product_category_name_english, p.product_category_name) AS product_category_name_english,
    p.product_category_name AS product_category_name_pt,
    p.product_name_lenght::int AS product_name_length,
    p.product_description_lenght::int AS product_description_length,
    p.product_photos_qty::int AS product_photos_qty,
    p.product_weight_g::numeric AS product_weight_g,
    p.product_length_cm::numeric AS product_length_cm,
    p.product_height_cm::numeric AS product_height_cm,
    p.product_width_cm::numeric AS product_width_cm
FROM stg.products p
LEFT JOIN stg.product_category_translation t USING (product_category_name);

ALTER TABLE analytics.dim_products ADD PRIMARY KEY (product_id);
