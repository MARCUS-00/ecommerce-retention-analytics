# Portfolio Blueprint: E-Commerce Revenue & Customer Retention Analytics (archive extract)

**Status: superseded.** `docs/MASTER_DOC.md` is the current, locked spec and covers everything
this document originally did — business problem, architecture, tech stack, SQL queries, KPI
contract, dashboard plan, and roadmap — in refined, final form. This file originally ran ~630
lines; it has been trimmed to the two sections that were never absorbed into MASTER_DOC because
they aren't build spec, they're reasoning and templates: the ML-scope evaluation (why demand
forecasting was approved and churn/NLP/deep-learning were rejected) and the resume-bullet
template. Section numbers below are kept as originally written for citation continuity.

---

## 15. Resume-ready project description

**E-Commerce Revenue & Customer Retention Analytics** — PostgreSQL · Python · SQL · Power BI · [GitHub link]

- Built an end-to-end analytics pipeline on a ~100K-order Brazilian e-commerce dataset: designed a PostgreSQL star schema (9 raw tables → staging → modeled facts/dims), Python ETL with automated data-quality checks, and a 4-page Power BI executive dashboard.
- Authored 20+ analytical SQL queries (CTEs, window functions) for cohort retention, RFM segmentation, and Pareto analysis; identified that [N] categories drive [X]% of revenue and a repeat-purchase rate of [Y]%, and reconciled item-level vs payment-level revenue ([Z]% mismatch documented).
- Quantified delivery's impact on satisfaction: late deliveries ([X]% of orders) showed significantly lower review scores (Mann–Whitney U, p < 0.05; median [a] vs [b]); delivered recommendations in a 1-page executive memo.

Replace every bracket with your actual computed result (they're already sitting in
`docs/findings.md` — never invent one). If a bullet's number isn't yours, delete the bullet.

## 16. Skills demonstrated (JD-keyword mapping)

SQL (joins, CTEs, window functions, indexing) · data modeling (star schema, staging layers) · Python (pandas, SQLAlchemy, scipy) · statistics (hypothesis testing, distributions, cohort analysis) · Power BI + DAX · Excel (pivot summary deliverable) · ETL & data quality · Git/GitHub (+ optional CI) · business communication (memo, README, KPIs) · documentation.

---

## 20. Verdict and decision framework (ML scope evaluation)

**Decision: keep the Olist project. Add one meaningful ML module (demand forecasting) and one optional low-cost module (K-Means segmentation benchmarked against rule-based RFM). Reject everything else.** No project switch — reasoning in the conversation log; short version: alternatives with "native" ML (SaaS churn, telco churn, credit default) fail on synthetic-data circularity, cliché datasets, or data-science drift.

Every candidate ML feature was tested against seven criteria (real business problem · industry-common · analyst-scope · fresher-achievable on public data · reasonable timeframe · interview-defensible · doesn't read as incomplete DS). Results:

| Candidate feature | Verdict | Deciding reason |
|---|---|---|
| Short-horizon demand forecasting | **Approved (Module A)** | The canonical analyst-ML task in retail; strengthens the ops story; classical methods are fully explainable |
| K-Means segments vs rule-based RFM | **Approved, optional (Module B)** | Cheap, industry-real, and the *comparison* framing avoids the cliché |
| Churn prediction model | **Rejected** | Marketplace data has no churn construct (~one-time buyers dominate); a "churn model" here is a misapplied concept — instant interview kill |
| Repeat-purchase propensity classifier | **Rejected** | Severely imbalanced target + weak at-purchase features → misleading metrics; the *inferential* question (what drives repeat purchase) is already answered by the stats work |
| Review sentiment NLP | **Rejected** | Reviews are Portuguese, and a labeled 1–5 score already exists — modeling sentiment adds zero decision value |
| Deep learning (any) | **Rejected** | Nothing in this data justifies it; a red flag on an analyst resume |
| LLM "chat with your data" bot | **Rejected for v1** | Engineering demo, not analysis; DA interviewers can't evaluate it and it dilutes the analyst story. Demonstrate AI literacy verbally (how you use AI tools *with verification*) instead. Fine as a separate later experiment |

**Three rules that keep the ML analyst-grade (state them in the README):**
1. **Baseline first.** Every model is compared against a naive baseline; if it doesn't beat the baseline, that gets reported, not hidden.
2. **The model serves an insight.** Each module ends in a memo recommendation, not a model artifact. No deployment claims.
3. **Resume label:** "predictive analytics" / "forecasting" / "segmentation" — never "machine learning engineering."

(Module A shipped exactly as decided here: `notebooks/04_demand_forecast.ipynb`,
`docs/monitoring_policy.md`. Module B was never built — the core scope filled the available
time, and Module B was explicitly conditional on that per MASTER_DOC's optional ladder.)
