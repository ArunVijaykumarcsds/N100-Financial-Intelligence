# Sprint 2 Review — N100 Financial Intelligence

**Prepared from a full repository audit.** This review evaluates Sprint 2 against the codebase as it actually exists today — every "Completed" claim below was checked against source files, and several were verified by direct execution (running the ETL scripts and the full test suite). Where a deliverable is partially built or not built, this document says so plainly rather than rounding up.

---

## Sprint Goal

Sprint 1 (per the repository's original README) delivered the **data foundation**: a validated SQLite database built from 12 source Excel files, with ETL loaders, validators, a normaliser, and 35+ unit tests.

Building on that foundation, **Sprint 2's implicit goal — inferred from the volume and nature of code added — was to deliver the analytics, scoring, forecasting, and presentation layers**: turning the raw, loaded financial data into ratios, KPIs, composite rankings, simple predictive models, and a usable multi-page Streamlit dashboard that an end user could actually navigate.

No formal sprint planning document, ticket tracker export, or burndown chart exists in the repository, so this goal statement is reconstructed from evidence (file creation patterns, the breadth of `src/analytics/` and `src/dashboard/`, and the Makefile's `dashboard` target) rather than quoted from a planning artifact.

---

## Completed Deliverables

The following were verified as working, either by direct code review confirming correct logic and complete wiring, or by direct execution:

- **Financial ratio calculation engine** (`RatioEngine` in `ratios.py`) — 7 ratios (net profit margin, operating margin, ROE, ROCE, ROA, debt-to-equity, interest coverage, asset turnover), each with explicit divide-by-zero / invalid-input handling. **Unit tested — 7 tests, all passing.**
- **Cash flow KPI engine** (`CashFlowKPIs` in `cashflow_kpis.py`) — free cash flow, CFO quality classification, capex intensity classification, FCF conversion, and a 7-pattern capital allocation classifier. **Unit tested — 6 tests, all passing.**
- **CAGR calculator with edge-case flagging** (`CAGRCalculator` in `cagr.py`) — 6-way status flag (OK/ZERO_BASE/DECLINE_TO_LOSS/TURNAROUND/BOTH_NEGATIVE/INVALID) instead of a silently misleading number. **Unit tested — 5 tests, all passing.**
- **Growth analytics** (`growth.py`, `ranking.py`) — YoY revenue/profit growth via `pct_change()`, `inf`-to-`NaN` cleanup, blended growth score, and top/bottom leaderboards. Wired into the **Growth Dashboard** page.
- **Quality scoring** (`quality.py`) — normalized 0–100 composite of Operating Margin, EPS, and Dividend Payout (40/40/20 weighting). Feeds into Master Ranking.
- **Financial health analyzer** (`financial_health.py`) — vectorized margin/coverage/earnings-quality metrics with a 0–4 point Risky/Average/Healthy rating. Wired into **Financial Health** and **Company Snapshot** pages.
- **Valuation analyzer** (`valuation.py`) — PE ratio computation joining latest stock price to latest EPS, with Undervalued/Fairly Valued/Overvalued bucketing. Wired into the **Valuation Dashboard** page.
- **Sector analytics** (`sector_analytics.py`) — sector-level company counts, index weight aggregation, and market-cap-category crosstab from `sectors.xlsx`. Wired into the **Sector Analytics** page.
- **Composite scoring system**: Financial Score (`scoring_engine.py`) → Quality Score → Valuation Score → **Master Score** (`master_ranking.py`, weighted 40/35/25) → **Future Winner Score** (`future_winners.py`, weighted 60/40 against a separate growth score). This four-tier scoring chain is the most architecturally complete piece of work delivered this sprint and is correctly wired end-to-end.
- **Three linear regression forecasters** (`RevenueForecaster`, `ProfitForecaster`, `EPSForecaster`) using `scikit-learn`'s `LinearRegression`, fit per company on `year_num` vs. the target metric, with a ≥3-year minimum data guard. All three are wired into dedicated dashboard pages with chart visualization.
- **Rule-based health and growth heuristics** (`HealthPredictor`, `GrowthPredictor`) — simple weighted-threshold classifiers, correctly distinguished in this review (and in `PROJECT_ARCHITECTURE.md`) from the genuinely model-based forecasters above.
- **AI Insights recommendation generator** (`ai_insights.py`) — maps a company's Future Winner Score to a Strong Buy/Buy/Hold/Avoid label with templated explanatory text.
- **17-page Streamlit dashboard** (`src/dashboard/app.py` + `modules/`) — confirmed reachable via the sidebar: Home, Top Companies, Company History, Company Comparison, Financial Health, Company Snapshot, Winner Dashboard, Sector Analytics, Valuation Dashboard, Growth Dashboard, Master Ranking, Revenue/Profit/EPS Forecasting, Health Prediction, Growth Prediction, Future Winners, AI Insights.
- **Executive Command Center home page** — a genuine synthesis view pulling top Future Winner, top Growth company, two leaderboards, two bar charts, and a generated recommendation feed onto one landing page.

---

## Analytics Engines Implemented

| Engine | Status | Notes |
|---|---|---|
| Ratio Engine | ✅ Complete, tested | 7 ratios, all with edge-case returns |
| Cash Flow KPI Engine | ✅ Complete, tested | Includes the capital allocation pattern classifier |
| CAGR Engine | ✅ Complete, tested | **Not yet surfaced in any dashboard page** — built and correct, but invisible to end users this sprint |
| Growth Engine | ✅ Complete | Wired into UI; `remove_extreme_growth()` guard exists but is not called from the main growth pipeline |
| Quality Engine | ✅ Complete | Feeds Master Ranking; standalone Quality Dashboard page exists but is **not connected to the app** (see Challenges Encountered) |
| Financial Health Engine | ✅ Complete | Wired into two pages |
| Valuation Engine | ✅ Complete | Fixed PE thresholds, not sector-adjusted |
| Scoring Engine (Financial Score) | ✅ Complete | Market Cap input is a `revenue * 10` proxy, not real market cap data (see Edge Case Handling) |
| Master Ranking Engine | ✅ Complete | Most depended-upon module in the analytics layer |
| Future Winners Engine | ✅ Complete | Blends Master Score + Growth Score |
| AI Insights Engine | ✅ Complete, scope-limited | Template-based recommendation, not a trained model — labeled accurately as such in this sprint's documentation |
| Sector Analytics Engine | ✅ Complete | Uses a dedicated raw file rather than re-deriving from P&L |

---

## Forecasting Modules Implemented

| Module | Status | Notes |
|---|---|---|
| Revenue Forecasting | ✅ Complete | `sklearn.linear_model.LinearRegression`, per-company, ≥3-year minimum |
| Profit Forecasting | ✅ Complete | Same architecture as above |
| EPS Forecasting | ✅ Complete | Same architecture as above |
| Health Prediction | ✅ Complete (rule-based, by design) | Not a trained model — flagged accurately rather than oversold |
| Growth Prediction | ✅ Complete (rule-based, by design) | Latest-2-years formula, no fitting step |

**Partial / not done within forecasting scope:**
- No accuracy metric (R², MAE, etc.) is computed for any forecaster — this was not delivered this sprint and there is currently no way to assess forecast reliability from within the app.
- `scikit-learn` was used as a new dependency this sprint but was **not added to `requirements.txt`** — an environment-setup gap that will affect anyone cloning the repo fresh.
- TTM (trailing-twelve-month) rows are silently dropped from every forecaster's training data as a side effect of the year-extraction regex, which was not a documented or apparently deliberate design decision.

---

## Database Deliverables

- `db/schema.sql` carried over from Sprint 1 — unchanged this sprint (still 3 tables: `companies`, `profit_loss`, `balance_sheet`).
- **New this sprint**: `load_financial_ratios.py`, which creates a 4th table, `financial_ratios`, by writing the processed CSV into SQLite via `to_sql(if_exists="replace")`. This is a genuine new deliverable, but it is **disconnected from the rest of the pipeline** — it must be run manually, is not part of any Makefile target, and its output table is not read back by any analytics or dashboard module once created. As currently built, it's a write-only destination.
- No schema migration tooling, versioning, or `ALTER TABLE` support was added — the dynamically-created `financial_ratios` table's structure is implicitly defined by whatever columns `build_financial_ratios.py` happens to output.

---

## KPI Deliverables

This sprint delivered the full KPI computation chain end to end for the financial-ratio family:

```
profitandloss.xlsx + balancesheet.xlsx + cashflow.xlsx
   → build_financial_ratios.py (3-way merge + 11 derived columns)
   → data/processed/financial_ratios.csv  (1,370 rows, confirmed by direct inspection)
```

The 11 derived KPI columns are: `net_profit_margin_pct`, `operating_profit_margin_pct`, `return_on_equity_pct`, `return_on_assets_pct`, `debt_to_equity`, `interest_coverage`, `asset_turnover`, `free_cash_flow`, `cfo_quality_score`, `capex_intensity`, `fcf_conversion`.

A second, separate KPI deliverable — `build_capital_allocation.py` → `output/capital_allocation.csv` — classifies each company-year's cash flow sign pattern into one of 7 capital allocation behaviors. This was completed but, like the `financial_ratios` SQLite table, is **not yet visualized in any dashboard page**.

A third diagnostic deliverable, `build_ratio_edge_cases.py`, scans the processed CSV for missing ROE/ROA/interest-coverage values and excessive debt-to-equity (>5), logging findings to `logs/ratio_edge_cases.log`. This is a genuinely useful data-quality artifact, but it runs entirely at module-import time with no `__main__` guard, which is a code-quality issue to clean up rather than a functional gap.

---

## Testing Deliverables

Verified by executing `pytest tests/` from the repository root during this review:

```
53 passed in 0.75s
```

New this sprint (KPI-layer tests, which did not exist in the Sprint 1 deliverable list):

- `tests/kpi/test_cagr.py` — 5 tests
- `tests/kpi/test_cashflow.py` — 6 tests
- `tests/kpi/test_ratios.py` — 7 tests

The Sprint 1-era `tests/etl/test_normaliser.py` (35 tests) continues to pass unchanged.

**Not delivered this sprint, and still gaps as of this review:**
- `tests/etl/test_loader.py` and `tests/etl/test_validator.py` exist as files but are **empty** — zero tests for `loader.py`'s `load_excel()` or any function in `validator.py`.
- No tests exist for any of: `growth.py`, `quality.py`, `financial_health.py`, `valuation.py`, `sector_analytics.py`, `scoring_engine.py`, `master_ranking.py`, `future_winners.py`, `ai_insights.py`, `health_prediction.py`, `growth_prediction.py`, the three forecasters, or any dashboard page.
- This means the entire **scoring and ranking chain** — arguably the analytical core of the platform — currently has no regression protection. A change to a weighting constant (e.g., the 40/35/25 Master Score blend) would not be caught by any automated test today.

---

## Capital Allocation Deliverables

`build_capital_allocation.py` and the underlying `CashFlowKPIs.capital_allocation_pattern()` method were completed this sprint:

- Classifies each company-year into one of: Reinvestor, Liquidating Assets, Distress Signal, Growth Funded By Debt, Cash Accumulator, Pre-Revenue, Mixed, or Unknown — based on the sign combination of operating/investing/financing cash flow activities.
- Verified logic: the lookup table covers 7 of the 8 possible sign combinations explicitly; the 8th falls through to "Unknown" by design (the `dict.get()` default), not by omission/bug.
- Output (`output/capital_allocation.csv`) is generated correctly but **has no corresponding dashboard page** — this is a completed backend deliverable without a completed frontend counterpart, and should be tracked as a carry-over item into the next sprint rather than marked fully done.

---

## Edge Case Handling

Sprint 2 shows clear, deliberate edge-case engineering in the lower layers of the analytics stack:

- `RatioEngine`: every division returns `None` rather than raising or propagating `inf`/`NaN` silently (zero sales, non-positive equity, zero interest, zero total assets all handled).
- `CAGRCalculator`: 6 distinct edge cases identified and flagged rather than collapsed into a single "can't compute" case — this is the single most carefully designed piece of edge-case handling in the repository.
- `CashFlowKPIs.cfo_quality_score()` and `capex_intensity()`: graceful `None` returns on zero-denominator inputs, with classification thresholds clearly documented in the code.
- `quality.py`'s `normalize()`: explicitly handles the degenerate case where `min_val == max_val` across a series (returns a flat 50 instead of dividing by zero).

**Edge cases that were not handled or were handled inconsistently, found during this review:**

- `HealthPredictor`'s weighted health score has no scale normalization — it directly compares raw revenue/profit/EPS figures against fixed thresholds (5000/2000/500) with no adjustment for company size, so the classification is not comparable across companies of very different scale. This is a design limitation, not a bug, but it was not flagged or documented anywhere in the original code.
- The forecasting layer's `< 3 years` guard returns `None` cleanly, and the corresponding dashboard pages handle that `None` gracefully with a `st.warning()` message — this part was done correctly and consistently across all three forecasters.
- `master_ranking.py`'s `market_cap = revenue * 10` substitution is not an edge case handler but a **placeholder for missing real data** that was not labeled as such anywhere in the original code or comments — a real `market_cap.xlsx` file exists in `data/raw/` with genuine market cap figures and was not integrated this sprint.
- The `build_financial_ratios.py` merge produces 1,370 output rows from a 1,263-row P&L input — indicating an unhandled one-to-many join fan-out from a non-unique `(company_id, year)` key somewhere in the balance sheet or cash flow source data. This was not caught, flagged, or deduplicated during this sprint.

---

## Streamlit Dashboard Deliverables

17 working, sidebar-reachable pages were delivered this sprint (full list and per-page description in `README.md` → Dashboard Modules). This represents the majority of the planned page set.

**Two pages were built but not successfully connected to the running application — confirmed by direct inspection of `app.py`:**

- **Ratio Analytics** — the page module (`ratio_analytics_page.py`) is correctly implemented and is even imported into `app.py`, and a full `elif page == "Ratio Analytics":` branch exists with proper metric/chart rendering code. However, the string `"Ratio Analytics"` does not appear in the sidebar `st.selectbox` options list, so a user can never select it. This is the closest possible miss — one missing string in one list.
- **Quality Dashboard** — the page module (`quality_dashboard_page.py`) is correctly implemented and self-contained, but is not imported into `app.py` at all, has no `elif` branch, and has no sidebar entry. It is fully built but entirely disconnected.

Both are one small integration step away from being shipped — this is recorded explicitly so the fix is correctly scoped as "wire up an already-built page" rather than "build a new page" in sprint planning going forward.

A minor cosmetic bug was also found: the sidebar `selectbox` options list contains `"Home"` twice (once at the start, once at the end of the list) — harmless (it just re-renders the same page) but worth a one-line cleanup.

---

## Challenges Encountered

Inferred from the patterns left in the code itself (there is no sprint retrospective document in the repository to quote from directly):

- **Coordinating two parallel data-access strategies.** The team appears to have started with a SQLite-first design (per Sprint 1's schema and loaders) but the majority of Sprint 2's new analytics and dashboard code reads Excel files directly instead. This likely reflects a pragmatic shortcut under time pressure — Excel-direct avoids needing to re-run ETL after every data tweak — but it leaves the codebase with two co-existing patterns rather than one, which is now documented as a key piece of technical debt in `PROJECT_ARCHITECTURE.md`.
- **Sidebar list maintenance falling out of sync with implementation.** Two pages (Ratio Analytics, Quality Dashboard) were fully or mostly built but did not make it into the sidebar list — a common failure mode when a UI's navigation list is maintained as a separate, manually-edited array rather than being derived automatically from the set of registered pages.
- **Missing a real market capitalization data source at integration time**, leading to the `revenue * 10` placeholder being used in the scoring engine — despite `market_cap.xlsx` (552 rows of real data) already being present in `data/raw/` from the start. This suggests the integration of that specific file was either deprioritized or simply missed during this sprint.
- **Dependency tracking gap** — `scikit-learn` was adopted mid-sprint for the forecasting work but never added to `requirements.txt`, which would have caused a `ModuleNotFoundError` for anyone setting up the project fresh from the committed dependency list.
- **Copy-paste duplication under time pressure** — visible in `build_capital_allocation.py`'s duplicated import block and `revenue_forecasting.py`'s duplicated model-fitting code block, both consistent with code being assembled by extending an existing file rather than refactoring a shared base.

---

## Technical Decisions

Decisions inferable from the consistent patterns in the delivered code:

- **Static methods for pure financial calculations** (`RatioEngine`, `CashFlowKPIs`, `CAGRCalculator`) — a deliberate choice that paid off directly in testability; these are exactly the three modules with meaningful unit test coverage this sprint.
- **Per-company linear regression rather than a single global model** for forecasting — appropriate given how different companies' growth trajectories are, though it does mean 100 independent single-feature models with no shared learning across companies.
- **Fixed-weight composite scoring** (Quality 40/40/20, Financial Score 20/25/25/15/15, Master Score 40/35/25, Future Winner 60/40) rather than any data-driven or optimized weighting — a reasonable, explainable starting point for a first-pass screener, with the explicit tradeoff that none of these weights have been validated against actual subsequent company performance.
- **`sys.path.append` for cross-package imports** rather than restructuring `src/analytics/` and `src/dashboard/` into a properly installable package (no `setup.py`/`pyproject.toml` exists) — a pragmatic choice for a project at this stage, with the cost being the inconsistency documented in `PROJECT_ARCHITECTURE.md` Section 11.
- **Diagnostic scripts over automated test assertions for data quality** (`validator.py`, `build_ratio_edge_cases.py`) — these produce human-readable logs/CSVs for manual review rather than `pytest`-enforced gates, which was likely the faster path to a usable output this sprint but defers the cost of catching regressions automatically to a future sprint.

---

## Sprint Metrics

Quantified directly from the repository:

| Metric | Value |
|---|---|
| Analytics modules added (`src/analytics/*.py`, excluding 2 empty stray files) | 28 |
| Dashboard page modules added (`src/dashboard/modules/*.py`, excluding 1 empty stray file) | 19 |
| Dashboard pages reachable in the running app | 17 / 19 |
| New unit tests added this sprint (KPI layer) | 18 |
| Total unit tests passing (full suite) | 53 / 53 |
| Lines of analytics code (`wc -l src/analytics/*.py`) | 2,367 |
| Lines of dashboard code (`wc -l src/dashboard/**/*.py`) | ~1,310 (modules + app.py) |
| Raw data files available | 12 |
| Raw data files actually consumed by any code path | 8 / 12 |
| Composite scoring tiers implemented (Quality/Financial/Valuation → Master → Future Winner) | 4 |
| Genuine ML-based forecasting models | 3 (Revenue, Profit, EPS — all `LinearRegression`) |
| Rule-based (non-ML) "prediction" modules | 2 (Health Prediction, Growth Prediction) |
| New SQLite tables added this sprint | 1 (`financial_ratios`, dynamically created, not pipeline-integrated) |
| Empty/stray files found in `src/` | 3 (`scoring.py`, `dashboard/modules/master_ranking.py`, `build_financial_ratios.pybuild_financial_ratios.py`) |
| Empty test files found | 2 (`test_loader.py`, `test_validator.py`) |

---

## Remaining Gaps

Carried forward, in the order they should likely be picked up:

1. **Wire up Ratio Analytics and Quality Dashboard** into `app.py`'s sidebar and routing — both are already built; this is pure integration work, not new development.
2. **Pin `scikit-learn`** in `requirements.txt` so the forecasting pages work on a fresh install.
3. **Replace the `revenue * 10` market cap proxy** with real data from the already-present `market_cap.xlsx`.
4. **Implement `run_pipeline.py`** so there is one command that takes the project from raw Excel to a fully loaded database and processed CSVs, rather than requiring a contributor to know and run 5+ scripts in the right order manually.
5. **Add test coverage** for the scoring/ranking chain (`scoring_engine.py`, `master_ranking.py`, `future_winners.py`) and for `loader.py`/`validator.py`, both currently at zero.
6. **Investigate the `build_financial_ratios.py` merge fan-out** (1,263 → 1,370 rows) and deduplicate the resulting CSV.
7. **Surface the `financial_ratios` SQLite table, `capital_allocation.csv`, and `CAGRCalculator`'s edge-case flags** in the dashboard — three completed backend deliverables with no frontend yet.
8. **Decide on the API layer** — either build `src/api/` to match the Makefile's `api` target or remove the target and its unused dependencies.
9. **Reconcile the 8 orphaned company IDs** in `profitandloss.xlsx` that have no matching row in `companies.xlsx`.
10. Clean up the small but real code-quality items: duplicate `"Home"` sidebar entry, duplicated import block in `build_capital_allocation.py`, duplicated model-fit block in `revenue_forecasting.py`, the empty stray files, and the inconsistent `sys.path` strategies between `analytics_runner.py` and the rest of the analytics layer.

---

## Readiness Assessment

**Is this sprint's output ready for end users?** Conditionally yes, for its core, reachable feature set:

- A user can today install dependencies (with the one documented `scikit-learn` fix), build the database, and run `streamlit run src/dashboard/app.py` to get a working 17-page financial screening dashboard over real Nifty 100 data, with correct, tested ratio and cash-flow-quality calculations underneath.
- The platform is **not** ready to be positioned as having "AI-powered" or "predictive" capabilities beyond the three linear regression forecasters — the "AI Insights," "Health Prediction," and "Growth Prediction" naming should be paired with accurate scope-setting (rule-based heuristics, not trained models) in any user-facing materials, to avoid setting expectations the current implementation doesn't meet.
- The platform is **not** ready for multi-user or production deployment without the architectural work flagged in `PROJECT_ARCHITECTURE.md` Section 13 (no caching, no connection pooling, no config centralization, no CI/CD).
- Data integrity gaps (orphaned company IDs, the CSV row-count fan-out, the unused real market-cap data) should be resolved before any of the ranking outputs (Master Ranking, Future Winners) are used to make real investment decisions — these are currently best understood as a heuristic screening demo over real data, not a production-grade quantitative research tool.

---

## Sprint Outcome

**Sprint 2 substantially achieved its inferred goal.** The team delivered a complete, internally consistent four-tier scoring system (Ratio/KPI → Quality/Financial/Valuation → Master Score → Future Winner Score), three working ML-based forecasters, and a 17-page functional Streamlit dashboard — all verified working by direct execution during this audit, not just by reading code.

The shortfall against a fully "done" sprint is concentrated in three places: (1) two dashboard pages built but not connected to the navigation, (2) a testing gap that leaves the entire scoring/ranking layer without regression protection even though the lower-level KPI calculators are well tested, and (3) several data-integration loose ends (the unused real market-cap file, the orphaned company IDs, the CSV merge fan-out) that don't break anything visibly today but represent latent correctness risk in the platform's core ranking outputs.

None of these gaps are large rewrites — each is scoped concretely in [Remaining Gaps](#remaining-gaps) above — which makes them a reasonable and achievable starting backlog for Sprint 3 rather than a sign that Sprint 2 underdelivered.
