"""Generate small, synthetic, schema-faithful CSVs for CI (MASTER_DOC section 19).

Never copies real rows. Deliberately plants three defects so the validation suite is
demonstrably exercised in CI, not just trivially green on clean data:
  - one duplicate review (order O-0001 gets two review rows)
  - one payment mismatch (order O-0002's payment total != its item total)
  - one temporal violation (order O-0003 delivered before it was shipped)
All three are "logged" anomaly categories (MASTER_DOC section 10), never blocking - referential
integrity, PK uniqueness, and domain values stay clean so CI's pytest run is genuinely green.
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

N_CUSTOMERS = 100
N_SELLERS = 15
N_PRODUCTS = 25
N_ORDERS = 100

CATEGORIES_PT = ["cama_mesa_banho", "beleza_saude", "esporte_lazer", "moveis_decoracao", "informatica_acessorios"]
CATEGORIES_EN = ["bed_bath_table", "health_beauty", "sports_leisure", "furniture_decor", "computers_accessories"]
STATES = ["SP", "RJ", "MG", "RS", "PR"]
BASE_DATE = datetime(2017, 6, 1)


def _ts(offset_days: float) -> str:
    return (BASE_DATE + timedelta(days=offset_days)).strftime("%Y-%m-%d %H:%M:%S")


def generate(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    customers = pd.DataFrame({
        "customer_id": [f"C-{i:04d}" for i in range(N_CUSTOMERS)],
        "customer_unique_id": [f"U-{i % 90:04d}" for i in range(N_CUSTOMERS)],  # a few repeat persons
        "customer_zip_code_prefix": [10000 + i for i in range(N_CUSTOMERS)],
        "customer_city": ["sao paulo"] * N_CUSTOMERS,
        "customer_state": [random.choice(STATES) for _ in range(N_CUSTOMERS)],
    })
    customers.to_csv(output_dir / "olist_customers_dataset.csv", index=False)

    geolocation = pd.DataFrame({
        "geolocation_zip_code_prefix": [10000 + (i % 50) for i in range(80)],  # duplicate prefixes, like real source
        "geolocation_lat": [-23.5 + random.uniform(-0.1, 0.1) for _ in range(80)],
        "geolocation_lng": [-46.6 + random.uniform(-0.1, 0.1) for _ in range(80)],
        "geolocation_city": ["sao paulo"] * 80,
        "geolocation_state": ["SP"] * 80,
    })
    geolocation.to_csv(output_dir / "olist_geolocation_dataset.csv", index=False)

    sellers = pd.DataFrame({
        "seller_id": [f"S-{i:04d}" for i in range(N_SELLERS)],
        "seller_zip_code_prefix": [20000 + i for i in range(N_SELLERS)],
        "seller_city": ["rio de janeiro"] * N_SELLERS,
        "seller_state": ["RJ"] * N_SELLERS,
    })
    sellers.to_csv(output_dir / "olist_sellers_dataset.csv", index=False)

    products = pd.DataFrame({
        "product_id": [f"P-{i:04d}" for i in range(N_PRODUCTS)],
        "product_category_name": [CATEGORIES_PT[i % len(CATEGORIES_PT)] for i in range(N_PRODUCTS)],
        "product_name_lenght": [40 + i for i in range(N_PRODUCTS)],
        "product_description_lenght": [200 + i for i in range(N_PRODUCTS)],
        "product_photos_qty": [1 + i % 5 for i in range(N_PRODUCTS)],
        "product_weight_g": [500 + i * 10 for i in range(N_PRODUCTS)],
        "product_length_cm": [20 + i for i in range(N_PRODUCTS)],
        "product_height_cm": [10 + i for i in range(N_PRODUCTS)],
        "product_width_cm": [15 + i for i in range(N_PRODUCTS)],
    })
    products.to_csv(output_dir / "olist_products_dataset.csv", index=False)

    category_translation = pd.DataFrame({
        "product_category_name": CATEGORIES_PT,
        "product_category_name_english": CATEGORIES_EN,
    })
    category_translation.to_csv(output_dir / "product_category_name_translation.csv", index=False)

    order_ids = [f"O-{i:04d}" for i in range(N_ORDERS)]
    statuses = ["delivered"] * 90 + ["shipped"] * 5 + ["canceled"] * 5
    orders_rows = []
    for i, order_id in enumerate(order_ids):
        purchase_offset = i * 0.5
        status = statuses[i]
        approved_at = _ts(purchase_offset + 0.5)
        carrier_date = _ts(purchase_offset + 2)
        customer_date = _ts(purchase_offset + 8) if status == "delivered" else None
        estimated_date = _ts(purchase_offset + 12)

        if order_id == "O-0003":
            # planted temporal violation: delivered before it was even shipped
            customer_date = _ts(purchase_offset + 1)

        if order_id == "O-0004":
            # null approved_at (mirrors real orders abandoned before payment capture)
            approved_at = None

        orders_rows.append({
            "order_id": order_id,
            "customer_id": f"C-{i:04d}",
            "order_status": status,
            "order_purchase_timestamp": _ts(purchase_offset),
            "order_approved_at": approved_at,
            "order_delivered_carrier_date": carrier_date if status != "canceled" else None,
            "order_delivered_customer_date": customer_date,
            "order_estimated_delivery_date": estimated_date,
        })
    orders = pd.DataFrame(orders_rows)
    orders.to_csv(output_dir / "olist_orders_dataset.csv", index=False)

    items_rows = []
    for i, order_id in enumerate(order_ids):
        items_rows.append({
            "order_id": order_id,
            "order_item_id": 1,
            "product_id": f"P-{i % N_PRODUCTS:04d}",
            "seller_id": f"S-{i % N_SELLERS:04d}",
            "shipping_limit_date": _ts(i * 0.5 + 3),
            "price": round(50 + i * 1.5, 2),
            "freight_value": round(10 + i * 0.2, 2),
        })
    order_items = pd.DataFrame(items_rows)
    order_items.to_csv(output_dir / "olist_order_items_dataset.csv", index=False)

    payments_rows = []
    for i, order_id in enumerate(order_ids):
        item_total = round(50 + i * 1.5, 2) + round(10 + i * 0.2, 2)
        payment_value = item_total
        if order_id == "O-0002":
            payment_value = round(item_total - 25.00, 2)  # planted payment mismatch
        payments_rows.append({
            "order_id": order_id,
            "payment_sequential": 1,
            "payment_type": "credit_card",
            "payment_installments": 1 + i % 4,
            "payment_value": payment_value,
        })
    order_payments = pd.DataFrame(payments_rows)
    order_payments.to_csv(output_dir / "olist_order_payments_dataset.csv", index=False)

    reviews_rows = []
    for i, order_id in enumerate(order_ids):
        if statuses[i] != "delivered":
            continue
        reviews_rows.append({
            "review_id": f"R-{i:04d}",
            "order_id": order_id,
            "review_score": 1 + (i % 5),
            # most reviews skip the optional title/message fields, like the real source
            # (title null unless i%5==0 -> 80% null; message null unless i%3==0 -> 67% null)
            "review_comment_title": "great" if i % 5 == 0 else None,
            "review_comment_message": "good product" if i % 3 == 0 else None,
            "review_creation_date": _ts(i * 0.5 + 9),
            "review_answer_timestamp": _ts(i * 0.5 + 10),
        })
    # planted duplicate review: order O-0001 gets a second, later review
    reviews_rows.append({
        "review_id": "R-9999",
        "order_id": "O-0001",
        "review_score": 5,
        "review_comment_title": "update",
        "review_comment_message": "changed my mind, great after all",
        "review_creation_date": _ts(50),
        "review_answer_timestamp": _ts(51),
    })
    order_reviews = pd.DataFrame(reviews_rows)
    order_reviews.to_csv(output_dir / "olist_order_reviews_dataset.csv", index=False)


if __name__ == "__main__":
    import sys

    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw")
    generate(dest)
    print(f"Wrote fixture CSVs to {dest}")
