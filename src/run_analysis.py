"""Execute every saved query in sql/03_analysis and write a trimmed result sample to
sql/03_analysis/outputs/ for traceability (MASTER_DOC section 11).
"""

from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, text

from src.utils import get_engine, get_logger

logger = get_logger(__name__)

SAMPLE_ROWS = 200


def run_all_queries(
    engine: Engine,
    sql_dir: Path = Path("sql/03_analysis"),
    output_dir: Path = Path("sql/03_analysis/outputs"),
) -> dict[str, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for sql_file in sorted(sql_dir.glob("*.sql")):
        df = pd.read_sql(text(sql_file.read_text()), engine)
        results[sql_file.stem] = df
        df.head(SAMPLE_ROWS).to_csv(output_dir / f"{sql_file.stem}.csv", index=False)
        note = "" if len(df) <= SAMPLE_ROWS else f" (saved first {SAMPLE_ROWS})"
        logger.info("%s: %d rows%s", sql_file.stem, len(df), note)
    return results


if __name__ == "__main__":
    engine = get_engine()
    run_all_queries(engine)
    logger.info("Analysis layer run complete")
