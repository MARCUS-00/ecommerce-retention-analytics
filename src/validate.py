"""Input-layer (staging) data-quality checks, per MASTER_DOC section 10.1.

Blocking checks fail the pipeline (non-zero exit, CI red). Logged checks record real
anomalies in the source data - never silently dropped or fixed - for the anomaly log
(MASTER_DOC section 10.2 format: date | table | check | count | decision).
"""

import sys
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable

from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError

from src.utils import get_engine, get_logger

logger = get_logger(__name__)

STAGING_TABLES = [
    "customers", "geolocation", "order_items", "order_payments",
    "order_reviews", "orders", "products", "sellers", "product_category_translation",
]

# PK columns expected unique per table's documented grain (MASTER_DOC section 8).
PRIMARY_KEYS = {
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "customers": ["customer_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
}

# (child table, child FK column(s), parent table, parent key column(s)).
FOREIGN_KEYS = [
    ("order_items", "order_id", "orders", "order_id"),
    ("order_items", "product_id", "products", "product_id"),
    ("order_items", "seller_id", "sellers", "seller_id"),
    ("orders", "customer_id", "customers", "customer_id"),
    ("order_payments", "order_id", "orders", "order_id"),
    ("order_reviews", "order_id", "orders", "order_id"),
]

# (table, column, null-rate threshold as a fraction, decision if breached).
NULL_POLICY = [
    ("orders", "order_approved_at", 0.0005,
     "small number of orders never received an approval timestamp (likely abandoned before "
     "payment capture); kept null as a verbatim staging mirror, no fix applied"),
    ("orders", "order_delivered_customer_date", 0.01,
     "expected: matches the count of orders whose order_status is not yet 'delivered' "
     "(shipped/canceled/unavailable/invoiced/processing/created/approved)"),
    ("order_reviews", "review_comment_title", 0.50,
     "expected: review title is an optional field, most customers skip it"),
    ("order_reviews", "review_comment_message", 0.50,
     "expected: review comment is an optional field, most customers leave no written comment"),
]


@dataclass
class CheckResult:
    check: str
    table: str
    detail: str
    count: int
    severity: str  # "blocking" or "logged"


@dataclass
class Report:
    passed: bool = True
    blocking_failures: list[CheckResult] = field(default_factory=list)
    logged_anomalies: list[CheckResult] = field(default_factory=list)

    def add(self, result: CheckResult) -> None:
        if result.count == 0:
            return
        if result.severity == "blocking":
            self.blocking_failures.append(result)
            self.passed = False
        else:
            self.logged_anomalies.append(result)


def _scalar(conn, query: str) -> int | Decimal | None:
    return conn.execute(text(query)).scalar()


def _run_check_group(conn, report: Report, check_name: str, fn: Callable) -> None:
    """Run one check-group function; a cast/syntax error against a malformed staging
    value (staging is verbatim TEXT - not guaranteed clean) becomes an attributed
    blocking failure instead of an opaque crash that kills every other check too."""
    try:
        fn(conn, report)
    except DBAPIError as exc:
        conn.rollback()
        report.add(CheckResult(
            check_name, "unknown",
            f"check raised a database error, likely a malformed staging value - {exc.orig}",
            1, "blocking",
        ))


def _check_row_counts(conn, report: Report) -> None:
    for table in STAGING_TABLES:
        n = _scalar(conn, f"SELECT COUNT(*) FROM stg.{table}")
        report.add(CheckResult(
            "row_count", table, f"stg.{table} has {n} rows", 0 if n > 0 else 1, "blocking",
        ))


def _check_primary_keys(conn, report: Report) -> None:
    for table, cols in PRIMARY_KEYS.items():
        col_list = ", ".join(cols)
        n = _scalar(conn, f"""
            SELECT COUNT(*) FROM (
                SELECT {col_list} FROM stg.{table} GROUP BY {col_list} HAVING COUNT(*) > 1
            ) dupes
        """)
        report.add(CheckResult(
            "pk_uniqueness", table, f"duplicate ({col_list}) values in stg.{table}", n, "blocking",
        ))


def _check_referential_integrity(conn, report: Report) -> None:
    for child, child_col, parent, parent_col in FOREIGN_KEYS:
        n = _scalar(conn, f"""
            SELECT COUNT(*) FROM stg.{child} c
            LEFT JOIN stg.{parent} p ON c.{child_col} = p.{parent_col}
            WHERE p.{parent_col} IS NULL
        """)
        report.add(CheckResult(
            "referential_integrity", child,
            f"{child}.{child_col} values missing from {parent}.{parent_col}", n, "blocking",
        ))


def _check_domain_values(conn, report: Report) -> None:
    checks = [
        ("order_reviews", "review_score::int NOT BETWEEN 1 AND 5"),
        ("order_items", "price::numeric < 0"),
        ("order_items", "freight_value::numeric < 0"),
        ("order_payments", "payment_value::numeric < 0"),
    ]
    for table, condition in checks:
        n = _scalar(conn, f"SELECT COUNT(*) FROM stg.{table} WHERE {condition}")
        report.add(CheckResult("domain", table, f"{table}: {condition}", n, "blocking"))


def _check_temporal_sanity(conn, report: Report) -> None:
    temporal_checks = [
        ("orders", "order_delivered_carrier_date < order_approved_at",
         "order_delivered_carrier_date IS NOT NULL AND order_approved_at IS NOT NULL "
         "AND order_delivered_carrier_date::timestamp < order_approved_at::timestamp"),
        ("orders", "order_delivered_customer_date < order_delivered_carrier_date",
         "order_delivered_customer_date IS NOT NULL AND order_delivered_carrier_date IS NOT NULL "
         "AND order_delivered_customer_date::timestamp < order_delivered_carrier_date::timestamp"),
        ("orders", "canceled order with a non-null delivered_customer_date",
         "order_status = 'canceled' AND order_delivered_customer_date IS NOT NULL"),
    ]
    for table, detail, condition in temporal_checks:
        n = _scalar(conn, f"SELECT COUNT(*) FROM stg.{table} WHERE {condition}")
        report.add(CheckResult("temporal_sanity", table, detail, n, "logged"))


def _check_null_policy(conn, report: Report) -> None:
    for table, column, threshold, decision in NULL_POLICY:
        total = _scalar(conn, f"SELECT COUNT(*) FROM stg.{table}")
        nulls = _scalar(conn, f"SELECT COUNT(*) FROM stg.{table} WHERE {column} IS NULL")
        rate = nulls / total if total else 0.0
        if rate > threshold:
            report.add(CheckResult(
                "null_policy", table,
                f"{column}: {nulls}/{total} ({rate:.2%}) null, exceeds {threshold:.2%} "
                f"threshold - {decision}",
                nulls, "logged",
            ))


def _check_review_duplicates(conn, report: Report) -> None:
    dup_review_ids = _scalar(conn, """
        SELECT COUNT(*) FROM (
            SELECT review_id FROM stg.order_reviews GROUP BY review_id HAVING COUNT(*) > 1
        ) x
    """)
    report.add(CheckResult(
        "review_duplicates", "order_reviews",
        "review_id values repeated across rows - not a reliable dedup key on its own",
        dup_review_ids, "logged",
    ))

    multi_review_orders = _scalar(conn, """
        SELECT COUNT(*) FROM (
            SELECT order_id FROM stg.order_reviews GROUP BY order_id HAVING COUNT(*) > 1
        ) x
    """)
    report.add(CheckResult(
        "review_duplicates", "order_reviews",
        "orders with more than one review - Phase 3 transform keeps latest by "
        "review_answer_timestamp (MASTER_DOC section 8)",
        multi_review_orders, "logged",
    ))


def run_input_checks(engine: Engine) -> Report:
    report = Report()
    with engine.connect() as conn:
        _run_check_group(conn, report, "row_count", _check_row_counts)
        _run_check_group(conn, report, "pk_uniqueness", _check_primary_keys)
        _run_check_group(conn, report, "referential_integrity", _check_referential_integrity)
        _run_check_group(conn, report, "domain", _check_domain_values)
        _run_check_group(conn, report, "temporal_sanity", _check_temporal_sanity)
        _run_check_group(conn, report, "null_policy", _check_null_policy)
        _run_check_group(conn, report, "review_duplicates", _check_review_duplicates)

    _log_report(report, "Input validation")
    return report


# --- Output layer (analytics), MASTER_DOC section 10.2 ---

# (analytics table, staging-equivalent count query) - dedup rules mean some don't map 1:1.
ROW_RECONCILIATION = [
    ("dim_customers", "SELECT COUNT(*) FROM stg.customers"),
    ("dim_products", "SELECT COUNT(*) FROM stg.products"),
    ("dim_sellers", "SELECT COUNT(*) FROM stg.sellers"),
    ("fact_orders", "SELECT COUNT(*) FROM stg.orders"),
    ("fact_order_items", "SELECT COUNT(*) FROM stg.order_items"),
    ("order_payments", "SELECT COUNT(*) FROM stg.order_payments"),
    ("order_reviews", "SELECT COUNT(DISTINCT order_id) FROM stg.order_reviews"),
    ("geolocation", "SELECT COUNT(DISTINCT geolocation_zip_code_prefix) FROM stg.geolocation"),
]

# (child table, child FK column, parent table, parent key column) in analytics.*.
OUTPUT_FOREIGN_KEYS = [
    ("fact_orders", "customer_id", "dim_customers", "customer_id"),
    ("fact_order_items", "order_id", "fact_orders", "order_id"),
    ("fact_order_items", "product_id", "dim_products", "product_id"),
    ("fact_order_items", "seller_id", "dim_sellers", "seller_id"),
    ("order_payments", "order_id", "fact_orders", "order_id"),
    ("order_reviews", "order_id", "fact_orders", "order_id"),
]


def _check_row_reconciliation(conn, report: Report) -> None:
    for table, stg_query in ROW_RECONCILIATION:
        analytics_count = _scalar(conn, f"SELECT COUNT(*) FROM analytics.{table}")
        stg_count = _scalar(conn, stg_query)
        report.add(CheckResult(
            "row_reconciliation", table,
            f"analytics.{table} has {analytics_count} rows, expected {stg_count} from staging",
            0 if analytics_count == stg_count else 1, "blocking",
        ))


def _check_output_referential_integrity(conn, report: Report) -> None:
    for child, child_col, parent, parent_col in OUTPUT_FOREIGN_KEYS:
        n = _scalar(conn, f"""
            SELECT COUNT(*) FROM analytics.{child} c
            LEFT JOIN analytics.{parent} p ON c.{child_col} = p.{parent_col}
            WHERE p.{parent_col} IS NULL
        """)
        report.add(CheckResult(
            "referential_integrity", child,
            f"{child}.{child_col} values missing from {parent}.{parent_col}", n, "blocking",
        ))


def _check_revenue_tie_out(conn, report: Report) -> None:
    analytics_total = _scalar(conn, "SELECT ROUND(SUM(price + freight_value), 2) FROM analytics.fact_order_items")
    stg_total = _scalar(conn, "SELECT ROUND(SUM(price::numeric + freight_value::numeric), 2) FROM stg.order_items")
    report.add(CheckResult(
        "revenue_tie_out", "fact_order_items",
        f"analytics total item revenue {analytics_total} vs staging total {stg_total}",
        0 if analytics_total == stg_total else 1, "blocking",
    ))

    mismatch_count = _scalar(conn, """
        WITH item_totals AS (
            SELECT order_id, SUM(price + freight_value) AS item_total
            FROM analytics.fact_order_items GROUP BY order_id
        ),
        payment_totals AS (
            SELECT order_id, SUM(payment_value) AS payment_total
            FROM analytics.order_payments GROUP BY order_id
        )
        SELECT COUNT(*) FROM analytics.fact_orders o
        JOIN item_totals i USING (order_id)
        JOIN payment_totals p USING (order_id)
        WHERE ABS(p.payment_total - i.item_total) > 0.01
    """)
    report.add(CheckResult(
        "revenue_tie_out", "fact_order_items",
        "orders where item total and payment total differ by more than 0.01 "
        "(vouchers/installments/cancellations - quantified for query D, not a data error)",
        mismatch_count, "logged",
    ))


def run_output_checks(engine: Engine) -> Report:
    report = Report()
    with engine.connect() as conn:
        _run_check_group(conn, report, "row_reconciliation", _check_row_reconciliation)
        _run_check_group(conn, report, "referential_integrity", _check_output_referential_integrity)
        _run_check_group(conn, report, "revenue_tie_out", _check_revenue_tie_out)

    _log_report(report, "Output validation")
    return report


def _log_report(report: Report, label: str) -> None:
    for result in report.blocking_failures:
        logger.error("BLOCKING [%s] %s: %s (count=%d)", result.check, result.table, result.detail, result.count)
    for result in report.logged_anomalies:
        logger.warning("LOGGED [%s] %s: %s (count=%d)", result.check, result.table, result.detail, result.count)
    logger.info(
        "%s: %s (%d blocking failures, %d logged anomalies)",
        label, "PASSED" if report.passed else "FAILED",
        len(report.blocking_failures), len(report.logged_anomalies),
    )


if __name__ == "__main__":
    engine = get_engine()
    input_report = run_input_checks(engine)
    output_report = run_output_checks(engine)
    sys.exit(0 if (input_report.passed and output_report.passed) else 1)
