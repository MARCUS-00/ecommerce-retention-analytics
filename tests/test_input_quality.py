"""Input-layer (staging) data-quality tests. Run locally against a live Postgres now;
Phase 7 CI points get_engine() at a fixture-loaded service Postgres instead - no test
code changes needed, since the connection is entirely .env-driven.
"""

import pytest

from src.utils import get_engine
from src.validate import run_input_checks


@pytest.fixture(scope="module")
def engine():
    return get_engine()


@pytest.fixture(scope="module")
def report(engine):
    return run_input_checks(engine)


def _failures(report, check_name):
    return [r for r in report.blocking_failures if r.check == check_name]


def test_all_staging_tables_populated(report):
    failures = _failures(report, "row_count")
    assert not failures, f"empty staging tables: {failures}"


def test_primary_keys_unique(report):
    failures = _failures(report, "pk_uniqueness")
    assert not failures, f"duplicate primary keys: {failures}"


def test_referential_integrity_clean(report):
    failures = _failures(report, "referential_integrity")
    assert not failures, f"orphan foreign keys: {failures}"


def test_domain_values_valid(report):
    failures = _failures(report, "domain")
    assert not failures, f"domain violations: {failures}"


def test_no_blocking_failures(report):
    assert report.passed, f"blocking failures: {report.blocking_failures}"


def test_anomaly_log_has_at_least_five_entries(report):
    assert len(report.logged_anomalies) >= 5, (
        f"expected >= 5 logged anomalies (MASTER_DOC 16 Phase 2 gate), "
        f"got {len(report.logged_anomalies)}"
    )
