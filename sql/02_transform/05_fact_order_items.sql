DROP TABLE IF EXISTS analytics.fact_order_items CASCADE;

CREATE TABLE analytics.fact_order_items AS
SELECT
    order_id,
    order_item_id::int AS order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::timestamp AS shipping_limit_date,
    price::numeric AS price,
    freight_value::numeric AS freight_value
FROM stg.order_items;

ALTER TABLE analytics.fact_order_items ADD PRIMARY KEY (order_id, order_item_id);
ALTER TABLE analytics.fact_order_items ADD FOREIGN KEY (order_id) REFERENCES analytics.fact_orders(order_id);
ALTER TABLE analytics.fact_order_items ADD FOREIGN KEY (product_id) REFERENCES analytics.dim_products(product_id);
ALTER TABLE analytics.fact_order_items ADD FOREIGN KEY (seller_id) REFERENCES analytics.dim_sellers(seller_id);
CREATE INDEX idx_fact_order_items_order_id ON analytics.fact_order_items(order_id);
CREATE INDEX idx_fact_order_items_product_id ON analytics.fact_order_items(product_id);
