"""Build the Power BI feeding views (sql/04_dashboard_views/*.sql) against analytics.*.
Separate from the core pipeline (src/run_pipeline.py) since views are a BI-layer concern,
not required for data-quality gates - reuses transform.py's run_sql_dir unchanged.
"""

from pathlib import Path

from src.transform import run_sql_dir
from src.utils import get_engine, get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    engine = get_engine()
    run_sql_dir(engine, Path("sql/04_dashboard_views"))
    logger.info("Dashboard views built")
