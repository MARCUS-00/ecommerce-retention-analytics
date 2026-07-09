"""Build the one Excel pivot deliverable (MASTER_DOC section 4.1/15): a processed extract
from analytics.vw_sales, plus pivot-table summaries computed from it (category x month
revenue, state summary) - the same result a fresher would get importing the extract into
Excel and building a PivotTable by hand, computed here via pandas.pivot_table instead.
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.utils import get_engine, get_logger

logger = get_logger(__name__)

OUTPUT_PATH = Path("dashboard/exec_summary.xlsx")


def build_summary(engine) -> None:
    extract = pd.read_sql(
        text("""
            SELECT
                order_id, product_category_name_english AS category, customer_state AS state,
                order_date, line_revenue
            FROM analytics.vw_sales
        """),
        engine,
        parse_dates=["order_date"],
    )
    extract["month"] = extract["order_date"].dt.to_period("M").astype(str)
    # pivot_table drops NaN index values by default - fill so uncategorized-product
    # revenue (610 products with no source category) isn't silently excluded from the total,
    # matching the COALESCE(..., 'unknown') convention used in sql/03_analysis/03_category_pareto.sql
    extract["category"] = extract["category"].fillna("unknown")

    category_month_pivot = pd.pivot_table(
        extract, index="category", columns="month", values="line_revenue",
        aggfunc="sum", fill_value=0, margins=True, margins_name="Total",
    ).round(2)

    state_pivot = pd.pivot_table(
        extract, index="state", values=["line_revenue", "order_id"],
        aggfunc={"line_revenue": "sum", "order_id": pd.Series.nunique},
    ).rename(columns={"line_revenue": "revenue", "order_id": "orders"}).round(2)
    state_pivot = state_pivot.sort_values("revenue", ascending=False)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUTPUT_PATH, engine="openpyxl") as writer:
        extract.head(5000).to_excel(writer, sheet_name="Raw Extract", index=False)
        category_month_pivot.to_excel(writer, sheet_name="Category x Month Pivot")
        state_pivot.to_excel(writer, sheet_name="State Pivot")

    logger.info(
        "Wrote %s: %d extract rows (sheet capped at 5000), %d categories x %d months, %d states",
        OUTPUT_PATH, len(extract), category_month_pivot.shape[0] - 1,
        category_month_pivot.shape[1] - 1, state_pivot.shape[0],
    )


if __name__ == "__main__":
    build_summary(get_engine())
