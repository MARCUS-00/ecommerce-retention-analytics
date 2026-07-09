"""Download the Olist dataset from Kaggle and load its 9 CSVs verbatim into stg.*.

No cleaning or typing happens here - staging is a raw TEXT mirror of the source CSVs.
Typing and transformation happen in sql/02_transform (Phase 3).
"""

import subprocess
import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, text

from src.utils import get_engine, get_logger

logger = get_logger(__name__)

KAGGLE_DATASET = "olistbr/brazilian-ecommerce"

# Source CSV (without .csv) -> staging table name.
CSV_TO_TABLE = {
    "olist_customers_dataset": "customers",
    "olist_geolocation_dataset": "geolocation",
    "olist_order_items_dataset": "order_items",
    "olist_order_payments_dataset": "order_payments",
    "olist_order_reviews_dataset": "order_reviews",
    "olist_orders_dataset": "orders",
    "olist_products_dataset": "products",
    "olist_sellers_dataset": "sellers",
    "product_category_name_translation": "product_category_translation",
}


def download_dataset(dest: Path) -> None:
    """Download and unzip the Kaggle dataset into dest, skipping if already present."""
    expected_files = [f"{csv_name}.csv" for csv_name in CSV_TO_TABLE]
    if dest.exists() and all((dest / f).exists() for f in expected_files):
        logger.info("All %d source CSVs already present in %s, skipping download", len(expected_files), dest)
        return

    dest.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "kaggle", "datasets", "download",
        "-d", KAGGLE_DATASET, "-p", str(dest), "--unzip",
    ]
    logger.info("Downloading %s to %s", KAGGLE_DATASET, dest)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("Kaggle download failed (exit %d): %s", result.returncode, result.stderr.strip())
        raise RuntimeError(
            f"Kaggle download of {KAGGLE_DATASET} failed - verify the dataset slug and "
            f"~/.kaggle/kaggle.json credentials manually; do not guess a mirror."
        )
    logger.info("Download complete")


def load_staging(engine: Engine, raw_dir: Path) -> dict[str, int]:
    """Load each source CSV verbatim (all TEXT) into stg.<table>. Returns row counts loaded."""
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS stg"))

    counts: dict[str, int] = {}
    for csv_name, table_name in CSV_TO_TABLE.items():
        csv_path = raw_dir / f"{csv_name}.csv"
        df = pd.read_csv(csv_path, dtype=str)
        df.to_sql(table_name, engine, schema="stg", if_exists="replace", index=False, chunksize=10_000)
        counts[table_name] = len(df)
        logger.info("Loaded stg.%s: %d rows (from %s)", table_name, len(df), csv_path.name)
    return counts


if __name__ == "__main__":
    raw_dir = Path("data/raw")
    download_dataset(raw_dir)
    engine = get_engine()
    row_counts = load_staging(engine, raw_dir)
    logger.info("Ingest complete. Row counts: %s", row_counts)
