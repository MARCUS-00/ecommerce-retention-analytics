ifeq ($(OS),Windows_NT)
	VENV_PY := .venv/Scripts/python.exe
else
	VENV_PY := .venv/bin/python
endif

.PHONY: setup db-up db-down fixtures pipeline analysis views excel test notebooks clean

setup:
	python -m venv .venv
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -r requirements.txt

db-up:
	docker compose up -d --wait

db-down:
	docker compose down

fixtures:
	$(VENV_PY) tests/fixtures/generate_fixtures.py data/raw

pipeline:
	$(VENV_PY) -m src.run_pipeline

analysis:
	$(VENV_PY) -m src.run_analysis

views:
	$(VENV_PY) -m src.build_dashboard_views

excel:
	$(VENV_PY) -m src.build_excel_summary

test:
	$(VENV_PY) -m pytest -q

notebooks:
	$(VENV_PY) -m jupyter nbconvert --to notebook --execute --inplace notebooks/01_eda.ipynb
	$(VENV_PY) -m jupyter nbconvert --to notebook --execute --inplace notebooks/02_retention_rfm.ipynb
	$(VENV_PY) -m jupyter nbconvert --to notebook --execute --inplace notebooks/03_delivery_reviews.ipynb
	$(VENV_PY) -m jupyter nbconvert --to notebook --execute --inplace notebooks/04_demand_forecast.ipynb

clean:
	docker compose down -v
	rm -rf .pytest_cache
	find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +
