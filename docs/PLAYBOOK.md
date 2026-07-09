# Playbook: Run This Project End to End

A single, verified walkthrough from an empty machine to a working dashboard. Every command
and every expected output below was actually run against this repository, not assumed. For
the *why* behind any decision, see `docs/architecture.md`; for column-level detail, see
`docs/data_dictionary.md`. This playbook only covers *how*.

**Time budget:** ~10-15 min setup (steps 0-3) + ~5-10 min pipeline (step 4) + ~5-15 min tests
and notebooks (steps 5-6) + 30-60 min for the Power BI build if you do it (step 8, manual,
optional). **Disk/network:** ~1GB free disk (Postgres image + data + `.venv`), ~50MB Kaggle
download, ~500MB if you also install Power BI Desktop.

## 0. Prerequisites

| Tool | Why | Check |
|---|---|---|
| Python 3.11+ (3.12 used to build this repo) | runs the ETL, tests, notebooks | `python --version` |
| Docker Desktop | runs Postgres 16 in a container - no local Postgres install needed | Desktop app shows "Engine running" |
| Git | clone the repo | `git --version` |
| GNU Make | runs every project command via short targets (`make pipeline`, etc.) | `make --version` |
| A free Kaggle account | the pipeline downloads the dataset from Kaggle at run time | kaggle.com |
| Power BI Desktop (Windows only, optional) | only needed to build the dashboard (step 8) | Microsoft Store |

**Installing `make` on Windows** (not bundled with Windows or Git for Windows):
- [Scoop](https://scoop.sh/) (no elevated terminal needed):
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
  scoop install make
  ```
- Or [Chocolatey](https://chocolatey.org/) from an **elevated** (Run as Administrator) terminal:
  `choco install make -y`
- Verify: `make --version` should print `GNU Make 4.x`.

macOS/Linux: `make` is preinstalled or one line away (`apt install make`, `brew install make`).

## 1. Clone and configure

```bash
git clone https://github.com/MARCUS-00/ecommerce-retention-analytics.git
cd ecommerce-retention-analytics
cp .env.example .env
```

`.env` holds local-only Postgres credentials (gitignored, never committed). The defaults in
`.env.example` work as-is for a fresh setup - edit only if you want different values:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=olist
DB_USER=analyst
DB_PASSWORD=changeme
```

**Set this before the first `make db-up`, not after** - these values seed the Postgres
container on its first boot (via `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB` in
`docker-compose.yml`). Changing `.env` after the container's data volume already exists does
**not** change the running database's actual password - see the troubleshooting table if you
hit this.

## 2. Kaggle credentials

The pipeline downloads the dataset via the Kaggle API, not a manual download.

1. kaggle.com -> sign up (free) -> profile picture -> **Settings** -> **API** -> **Create New
   Token**. This downloads `kaggle.json`.
2. Place it where the Kaggle CLI expects it:
   - Windows (PowerShell): `mkdir "$env:USERPROFILE\.kaggle"` then copy `kaggle.json` there.
   - macOS/Linux: `mkdir -p ~/.kaggle && cp ~/Downloads/kaggle.json ~/.kaggle/`
3. Never commit `kaggle.json` anywhere - it's a credential, not project data.

## 3. Install and start

```bash
make setup    # creates .venv, installs pinned requirements.txt - 1-3 min first run
make db-up    # starts Postgres 16 in Docker (docker compose up -d --wait)
```

Docker Desktop must already be running before `make db-up` (open it from the Start
menu/Applications, wait for "Engine running"). Confirm the database is healthy:

```bash
docker compose ps
```

Expect a row named `olist_postgres` with status `Up ... (healthy)`. (Note the underscore -
`olist_postgres`, not a hyphen - that's the literal container name in `docker-compose.yml`.)

**Activating the venv directly** (only needed if you want to run `python`, `jupyter`, or a
one-off script by hand instead of through `make` - every `make` target already calls
`.venv`'s Python directly and doesn't need this):
```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

## 4. Run the pipeline

```bash
make pipeline
```

This runs `ingest -> validate(input) -> transform -> validate(output)` end to end: downloads
the ~50MB dataset from Kaggle (skipped automatically if `data/raw/` already has all 9 CSVs),
loads it verbatim into `stg.*`, runs blocking + logged data-quality checks, builds the
`analytics.*` star schema, then re-validates the output. Takes 3-8 minutes on a first run.

Expect the log to end with:
```
Input validation: PASSED (0 blocking failures, 9 logged anomalies)
...
Output validation: PASSED (0 blocking failures, 1 logged anomalies)
Pipeline complete
```

If it doesn't end with `Pipeline complete`, stop here and check the Troubleshooting table -
nothing downstream is trustworthy until this passes.

Optionally, regenerate the SQL analysis-layer outputs (the 18 business-question queries'
trimmed result samples already committed under `sql/03_analysis/outputs/`):

```bash
make analysis
```

## 5. Verify

```bash
make test
```

Expect `10 passed`. These are data-quality assertions against the live database (row counts,
primary keys, referential integrity, revenue tie-out) - not mocked, run against exactly what
`make pipeline` just built.

## 6. Run the analysis notebooks

```bash
make notebooks
```

Executes all 4 notebooks top to bottom and saves outputs in place (`nbconvert --execute
--inplace`). Takes 3-10 minutes. Open any `.ipynb` in VS Code or Jupyter afterward to see the
charts and numbers. Cross-check these against `docs/findings.md` to confirm you're looking at
real data, not a stale/partial run:

| Notebook | Sanity-check number |
|---|---|
| `02_retention_rfm.ipynb` | repeat-purchase rate ≈ 3.0% |
| `03_delivery_reviews.ipynb` | late orders: median review 2/5; on-time: median 5/5 |
| `04_demand_forecast.ipynb` | 28-day forecast ≈ 6,660 orders (interval ≈ 3,585-9,943) |

`04_demand_forecast.ipynb` also writes `analytics.forecast_28d` - required before the
dashboard's forecast band will show anything.

## 7. Build the dashboard-feeding layer

```bash
make views    # analytics.vw_sales / vw_orders / vw_customers / vw_daily_orders
make excel    # dashboard/exec_summary.xlsx - pivot-table summary for non-technical readers
```

## 8. Build the Power BI dashboard (Windows, optional, human task)

Full detail in `dashboard/BUILD_SPEC.md` and the DAX formulas in `dashboard/dax_measures.md` -
this section is the short version with the two mistakes worth avoiding called out explicitly.

1. **Connect**: Home -> Get data -> More -> Database -> PostgreSQL database -> Connect.
   Server `localhost:5432`, Database `olist`, mode **Import**. Credentials: Database auth,
   the `DB_USER`/`DB_PASSWORD` from your `.env`.
2. **Import exactly these 6 objects** (Navigator, under `olist -> analytics`): `vw_sales`,
   `vw_orders`, `vw_customers`, `vw_daily_orders`, `forecast_28d`, `dim_date`. Do not import
   `stg.*` or the raw `fact_*`/`dim_*` tables directly - the views already bake in the correct
   delivered-vs-all-placed population filter.
3. **Relationships** (Model view): drag `dim_date[date]` to `vw_sales[order_date]`,
   `vw_orders[order_date]`, `vw_daily_orders[order_date]`, `forecast_28d[date]` - all
   one-to-many. **Use `order_date` (DATE), never `order_purchase_timestamp` (TIMESTAMP)** -
   relating a date table to a timestamp column silently matches zero rows and every chart
   goes blank. Then mark `dim_date` as the model's Date Table (Table Tools -> Mark as Date
   Table -> `date` column) - required for the MoM measure.
4. **DAX measures**: copy every formula from `dashboard/dax_measures.md` as-is (right-click
   the named table -> New measure). After creating them, sanity-check: `Total Revenue` ≈
   R$15,419,773.75, `Late Delivery %` ≈ 8.1%, `Repeat Cust %` ≈ 3.0%. If these are far off,
   the relationships in step 3 are probably wrong.
5. **Monthly trend charts** (revenue trend, AOV trend, late-% trend - Pages 1/2/4): put
   `dim_date[date]` on the X-axis, not a bare month number. Power BI's date hierarchy lets
   you drill to the Month level while still separating 2017 from 2018 - a chart binned on
   the standalone `month` integer column merges Jan 2017 and Jan 2018 into one bucket and
   silently produces a meaningless "growth" trend.
6. **Build the 4 pages** per `dashboard/BUILD_SPEC.md` section 3, one page per stakeholder
   question. Apply one consistent theme (View -> Themes) across all 4. (This playbook doesn't
   restate every visual from `BUILD_SPEC.md` page-by-page - it's the source of truth for that
   level of detail, this section is just the two mistakes worth avoiding.)
7. Save as `dashboard/ecommerce_analytics.pbix`. If you hit an SSL-negotiation error while
   connecting (uncommon on a fresh setup - this project's Postgres already runs with `md5`
   auth for broad BI-tool compatibility, see `docker-compose.yml`), Advanced options -> SSL
   Mode -> disable is safe for this local-only database.
8. Screenshot each page (`mkdir -p dashboard/screenshots` first) and embed at least the
   revenue overview in the README's Dashboard section - replaces more about the project for a
   reader in 5 seconds than any amount of prose.

## 9. Write the insights memo (human-authored, do not automate)

`docs/findings.md` has 7 machine-computed findings with exact numbers and source paths.
`docs/insights_memo.md` translates 5-7 of them into business language plus your own
recommendations, in your own words - by design, this file is never AI-written (a hiring
manager will ask you to explain any sentence in it). Use `docs/findings.md` as your source of
truth for every number; never round differently than it does.

## 10. Publish (repo owner only)

```bash
git add dashboard/ecommerce_analytics.pbix dashboard/screenshots/ docs/insights_memo.md README.md
git commit -m "feat: add dashboard, screenshots, and insights memo"
git push origin main
```

This only applies if you're pushing to **your own** GitHub repo with your own credentials. If
you're someone else running this playbook just to verify the project works (a recruiter, a
reviewer, a second machine you don't have push access to), stop after step 9 - do not attempt
to push to the original author's repository.

Pushing to `main` triggers `.github/workflows/ci.yml` (the badge at the top of the README) -
it re-runs the pipeline and test suite against synthetic fixtures in a clean GitHub-hosted
Postgres, independent of anything on your machine. Check the Actions tab after pushing; a red
badge means something doesn't reproduce outside your local environment and is worth
investigating before treating the build as done.

## Inspecting the database directly

Useful when troubleshooting - connect with `psql` (bundled with the Postgres Docker image, no
separate install needed) or any GUI client (DBeaver, pgAdmin, Power BI's own preview):

```bash
docker exec olist_postgres psql -U analyst -d olist -c "SELECT COUNT(*) FROM analytics.fact_orders;"
```

Expect `99441`. If this fails or returns something else, the problem is in the database
itself, not in whatever tool you were trying to use on top of it (Power BI, a notebook, etc.)
- narrows down where to keep looking.

## Daily quick-reference (after the first full setup)

```bash
cd ecommerce-retention-analytics
make db-up     # Docker Desktop must already be open
```

| Command | Does |
|---|---|
| `make setup` | install Python deps (first time only) |
| `make db-up` / `make db-down` | start / stop the Postgres container |
| `make pipeline` | full ingest -> validate -> transform -> validate |
| `make test` | 10 data-quality tests |
| `make analysis` | run the 18 SQL business-question queries, save samples to `sql/03_analysis/outputs/` |
| `make notebooks` | execute all 4 analysis notebooks |
| `make views` / `make excel` | rebuild the Power BI feeding views / Excel summary |
| `make clean` | destroys the DB volume + caches - full reset, use deliberately |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `failed to connect to the docker API` | Docker Desktop isn't running | Open Docker Desktop, wait for "Engine running", retry |
| `make db-up` hangs or the container never becomes healthy, port 5432 already allocated | another Postgres (local install or a different container) is already using port 5432 | Stop the other Postgres, or change `DB_PORT` in `.env` to e.g. `5433` and re-run `make db-up` (the container's *internal* port stays 5432; only the host-side mapping changes) |
| `Input validation: FAILED (N blocking failures ...)` and the pipeline stops before building `analytics.*` | a raw CSV doesn't match this repo's expected shape - wrong/corrupted download, or a different dataset version than this repo was built against | Read the blocking failures printed just above that line (each names the table/check); delete `data/raw/` and re-run `make pipeline` to force a clean re-download before assuming the data itself is bad |
| `make: command not found` | `make` not installed / new terminal hasn't picked up PATH | Re-run section 0's install, or open a fresh terminal |
| Kaggle `401 Unauthorized` | expired/missing `kaggle.json` | kaggle.com -> Settings -> API -> Expire Token -> Create New Token, redo step 2 |
| `DependentObjectsStillExist` on `make pipeline` | ran `make views` against an older schema, then re-ran the pipeline | Already fixed in this repo (`sql/02_transform/*.sql` uses `DROP ... CASCADE`) - if you see this, you're on an old commit; `git pull` |
| Power BI "couldn't authenticate" with correct-looking credentials | `.env`'s `DB_PASSWORD` was changed *after* the Postgres container's data volume was already created - the running database still has the old password | Either revert `.env` to match what the DB actually has, or reset the DB to pick up the new value: `docker compose down -v && make db-up && make pipeline` (destroys and rebuilds the DB from scratch) |
| Charts blank / all-zero in Power BI | Date relationships built against `order_purchase_timestamp` instead of `order_date` | Model view -> delete the `dim_date` relationships -> rebuild using `order_date` (see step 8.3) |
| Notebooks fail with `ModuleNotFoundError: No module named 'src'` | ran `jupyter`/`pytest` directly instead of via `make`, from the wrong working directory | Run `make notebooks` / `make test`, or manually always launch via `python -m ...` from the repo root |
| `make pipeline` succeeds but row counts look tiny (~100 rows) | pipeline ran against CI's synthetic fixtures, not the real Kaggle download | Delete `data/raw/`, re-run `make pipeline` so it downloads the real dataset |
