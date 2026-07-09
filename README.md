# E-Commerce Revenue & Customer Retention Analytics

[![CI](https://github.com/MARCUS-00/ecommerce-retention-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/MARCUS-00/ecommerce-retention-analytics/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg?logo=python&logoColor=white)](requirements.txt)
[![PostgreSQL 16](https://img.shields.io/badge/postgresql-16-336791.svg?logo=postgresql&logoColor=white)](docker-compose.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-informational.svg)](LICENSE)

An end-to-end analytics build on the Olist Brazilian e-commerce dataset (~100K orders, 9
relational tables): a PostgreSQL staging-plus-star-schema warehouse, a validated and idempotent
Python ETL pipeline, 18 business-question SQL analyses, a statistically tested operational
insight, and a 28-day demand forecast with walk-forward validation. Headline finding: late
deliveries are associated with a materially and significantly lower review score (median 2/5
vs. 5/5 on-time, Mann-Whitney U p ≈ 0) - full results in `docs/findings.md`.

## Dashboard

Not built yet - this repository produces the feeding views, DAX measures, and a full build
specification (`dashboard/BUILD_SPEC.md`), never a stubbed `.pbix` (by design; see
`docs/MASTER_DOC.md` section 4.3). A screenshot/walkthrough link goes here once a human builds
the dashboard from that spec.

## Business problem

Olist is a Brazilian e-commerce marketplace connecting small sellers to customers. Leadership
has three questions ahead of annual planning:

- **Revenue (CFO):** what drives growth, and where is revenue concentrated (and therefore at
  risk)?
- **Retention (CMO):** what share of customers ever return, and which segments deserve
  targeted spend?
- **Operations (Head of Ops):** does delivery performance measurably affect satisfaction and
  repeat purchase, and is the effect statistically significant?

## Architecture & key decisions

```
Kaggle CSVs (data/raw, gitignored)
      | src/ingest.py - loads verbatim, no cleaning
      v
stg.* (raw mirror, all TEXT)
      | src/validate.py - INPUT checks (blocking + logged)
      | sql/02_transform/*.sql - typed, deduplicated, derived columns
      v
analytics.* (star schema) - facts, dims, typed reviews/payments
      | src/validate.py - OUTPUT checks: reconcile counts, orphan FKs, revenue tie-out
      +--> sql/03_analysis/ - 18 business queries
      +--> notebooks/01-03 - EDA, cohorts/RFM, statistical test
      +--> notebooks/04 - forecast -> analytics.forecast_28d
      +--> sql/04_dashboard_views/ -> Power BI (4 pages) -> executive memo
```

Full detail in `docs/architecture.md`. Three decisions worth knowing before reading any query:

- **The `customer_id` vs. `customer_unique_id` trap:** `customer_id` is unique per *order*, not
  per person; every retention/repeat/RFM calculation joins through `customer_unique_id`
  instead. Get this backwards and repeat-purchase rate reads as ~0%.
- **Revenue = item price + freight, delivered orders**, reconciled against payments: 303 of
  99,441 orders (0.30%) show a >R$0.01 items-vs-payments mismatch, fully explained by vouchers/
  installments/cancellations - not an ETL bug (item-level revenue ties out *exactly* to
  staging).
- **Two populations, never mixed:** revenue/retention/RFM use delivered orders only; the
  demand forecast uses all placed orders, because ops must plan capacity regardless of eventual
  order outcome.

## Key findings

Full detail with source paths in `docs/findings.md`. Summary:

1. Repeat-purchase rate is **3.0%** (2,801/93,358 customers) - this marketplace is
   acquisition-dependent, not retention-driven.
2. Late deliveries: median review score **2/5** (54.1% are 1-2★) vs. **5/5** on-time (9.2% are
   1-2★) - Mann-Whitney U, p ≈ 0.
3. **8.11%** of delivered orders (7,826/96,478) arrive late.
4. Top 5 of 74 categories generate **39.25%** of delivered revenue.
5. Items-vs-payments reconciliation: **0.30%** of orders mismatch, fully explained (not an ETL
   error).
6. RFM: "Champions" (repeat, recent buyers) are 1.29% of customers but 2.51% of revenue; the
   biggest addressable lever is the 38.71%-strong "Recent One-Time" segment.
7. Walk-forward backtest: the seasonal-naive baseline (**WAPE 0.2308**) was not beaten by
   Holt-Winters (0.2310) - the simple baseline is the recommendation.

## How to run

**Prerequisites:** Python 3.11+, Docker Desktop, a Kaggle account with
`~/.kaggle/kaggle.json` configured, and GNU Make.

- macOS/Linux: `make` is preinstalled or available via your package manager (`apt install
  make`, `brew install make`).
- **Windows:** `make` is not built in and does not ship with Git for Windows. Install it via
  [Chocolatey](https://chocolatey.org/) from an **elevated** (Run as Administrator) terminal:
  `choco install make -y`, or via [Scoop](https://scoop.sh/) from a normal terminal (no
  elevation needed): `scoop install make`. Verify with `make --version` before continuing.

```bash
make setup          # create .venv, install pinned requirements
cp .env.example .env  # then configure ~/.kaggle/kaggle.json for the Kaggle API
make db-up           # Postgres 16 in Docker
make pipeline        # ingest -> validate -> transform -> validate
```

Then `make test` (pytest), `make analysis` (the 18 SQL business-question queries, saved to
`sql/03_analysis/outputs/`), `make notebooks` (EDA, cohorts/RFM, stats test, forecast),
`make views` (Power BI feeding views), and `make excel` (the pivot summary workbook). Full
clean-room rebuild: `make clean && make db-up && make pipeline && pytest -q && make notebooks`.

Full step-by-step walkthrough (prerequisites, Kaggle setup, dashboard build, troubleshooting):
`docs/PLAYBOOK.md`.

## Repo map

```
sql/01_schema/          DDL: analytics schema + generated dim_date
sql/02_transform/       stg.* -> analytics.* (typed, deduped, derived)
sql/03_analysis/        18 business-question queries (+ outputs/ samples)
sql/04_dashboard_views/ Power BI feeding views
src/                    ingest, validate, transform, run_pipeline, run_analysis,
                        build_dashboard_views, build_excel_summary, utils
notebooks/              01 EDA, 02 cohorts/RFM, 03 statistical test, 04 forecast
tests/                  input/output data-quality suite + CI fixture generator
dashboard/              BUILD_SPEC.md, dax_measures.md, exec_summary.xlsx (no .pbix - see above)
docs/                   architecture, data dictionary, findings, monitoring policy,
                        PLAYBOOK.md (full run-through), MASTER_DOC.md (the governing spec),
                        BLUEPRINT.md (trimmed archive: ML-scope rationale + resume template)
```

## Data source & license

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
(Kaggle, credit: Olist) - not redistributed here; `src/ingest.py` downloads it at run time into
the gitignored `data/raw/`. See `LICENSE` for the dataset's separate license note and this
repo's MIT license for the code.

## Limitations

- Data covers 2016-2018 from one Brazilian marketplace; findings are observational, not causal
  (stated explicitly wherever a statistical test is involved - see `docs/findings.md` #2).
- Only ~20 months of history and one observed annual cycle inform the forecast; year-over-year
  seasonal effects (beyond the weekly cycle) aren't modeled with confidence
  (`docs/monitoring_policy.md`).
- The dashboard is a build specification, not a built artifact, as of this commit - see
  `dashboard/BUILD_SPEC.md`.
