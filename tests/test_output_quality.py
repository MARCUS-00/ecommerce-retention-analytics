"""Output-layer (analytics) data-quality tests: row reconciliation, orphan FKs, revenue
tie-out. Run locally against a live Postgres now; Phase 7 CI points get_engine() at a
fixture-loaded service Postgres instead - no test code changes needed.
"""

import pytest

from src.utils import get_engine
from src.validate import run_output_checks


@pytest.fixture(scope="module")
def engine():
    return get_engine()


@pytest.fixture(scope="module")
def report(engine):
    return run_output_checks(engine)


def _failures(report, check_name):
    return [r for r in report.blocking_failures if r.check == check_name]


def test_row_reconciliation(report):
    failures = _failures(report, "row_reconciliation")
    assert not failures, f"row count mismatch vs staging: {failures}"


def test_no_orphan_foreign_keys(report):
    failures = _failures(report, "referential_integrity")
    assert not failures, f"orphan foreign keys: {failures}"


def test_revenue_ties_out_to_staging(report):
    failures = _failures(report, "revenue_tie_out")
    assert not failures, f"revenue mismatch: {failures}"


def test_no_blocking_failures(report):
    assert report.passed, f"blocking failures: {report.blocking_failures}"
