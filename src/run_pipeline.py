"""Single entry point: ingest -> validate(input) -> transform -> validate(output).
Fails loudly (non-zero exit) at the first blocking failure, per MASTER_DOC section 9.
"""

import sys
from pathlib import Path

from src.ingest import download_dataset, load_staging
from src.transform import run_sql_dir
from src.utils import get_engine, get_logger
from src.validate import run_input_checks, run_output_checks

logger = get_logger(__name__)


def main() -> int:
    engine = get_engine()
    raw_dir = Path("data/raw")

    download_dataset(raw_dir)
    load_staging(engine, raw_dir)

    input_report = run_input_checks(engine)
    if not input_report.passed:
        logger.error("Input validation failed - aborting before transform")
        return 1

    run_sql_dir(engine, Path("sql/01_schema"))
    run_sql_dir(engine, Path("sql/02_transform"))

    output_report = run_output_checks(engine)
    if not output_report.passed:
        logger.error("Output validation failed")
        return 1

    logger.info("Pipeline complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
