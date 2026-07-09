"""Shared helpers: database engine and logger factory, used by every pipeline module."""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

load_dotenv()


def get_engine() -> Engine:
    """Build a SQLAlchemy engine from .env-configured Postgres credentials."""
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    name = os.environ["DB_NAME"]
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}")


def get_logger(name: str) -> logging.Logger:
    """Return a module-level logger with consistent formatting across the pipeline."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
