"""Build the analytics star schema by executing sql/01_schema then sql/02_transform,
in filename order, one transaction per file (DROP IF EXISTS + CREATE AS pattern - idempotent).
"""

from pathlib import Path

from sqlalchemy import Engine, text

from src.utils import get_engine, get_logger

logger = get_logger(__name__)


def _strip_line_comments(sql_text: str) -> str:
    """Drop '-- ...' line comments before statement-splitting, so a semicolon inside a
    comment's prose can't be mistaken for a statement terminator."""
    lines = (line.split("--", 1)[0] for line in sql_text.splitlines())
    return "\n".join(lines)


def run_sql_dir(engine: Engine, path: Path) -> None:
    """Execute every *.sql file in path, in filename order, one transaction per file.

    The splitter below is a plain string split on ';' after stripping '--' comments - it
    does not understand string literals or dollar-quoted ($$ ... $$) function bodies. Safe
    for every file currently under sql/, all of which are simple DDL/DML with no semicolons
    or '--' inside literals; would silently misbehave if a future file needs either. Reach
    for a real SQL-aware splitter (e.g. sqlparse) before adding one.
    """
    for sql_file in sorted(path.glob("*.sql")):
        cleaned = _strip_line_comments(sql_file.read_text())
        statements = [s.strip() for s in cleaned.split(";") if s.strip()]
        with engine.begin() as conn:
            for statement in statements:
                conn.execute(text(statement))
        logger.info("Executed %s (%d statements)", sql_file.name, len(statements))


if __name__ == "__main__":
    engine = get_engine()
    run_sql_dir(engine, Path("sql/01_schema"))
    run_sql_dir(engine, Path("sql/02_transform"))
    logger.info("Transform complete")
