# PROJECT_ARCHITECTURE.md

## N100 Financial Intelligence — Technical Architecture Document

**Audience:** Engineers onboarding to this codebase.
**Method:** Every claim in this document was verified directly against repository source code during this audit — including executing the test suite (`pytest tests/` → 53/53 passing) and running the ETL load scripts end-to-end (`create_db.py` → `load_companies.py` → confirmed `92 companies loaded.`). Where something could not be verified or does not exist, it is explicitly marked **"Not implemented in repository"** rather than assumed.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architectural Principles (as observed)](#2-architectural-principles-as-observed)
3. [Folder Structure Breakdown](#3-folder-structure-breakdown)
4. [Data Pipeline Architecture](#4-data-pipeline-architecture)
5. [Analytics Layer Architecture](#5-analytics-layer-architecture)
6. [Forecasting Layer Architecture](#6-forecasting-layer-architecture)
7. [Dashboard Layer Architecture](#7-dashboard-layer-architecture)
8. [Database Layer Architecture](#8-database-layer-architecture)
9. [Testing Architecture](#9-testing-architecture)
10. [Data Flow Diagrams](#10-data-flow-diagrams)
11. [Module Dependency Maps](#11-module-dependency-maps)
12. [Current System Capabilities](#12-current-system-capabilities)
13. [Scalability Assessment](#13-scalability-assessment)
14. [Recommended Future Improvements](#14-recommended-future-improvements)

---

## 1. System Overview

N100 Financial Intelligence is a **three-tier, file-driven analytics application**:

```
Excel files (data/raw/) ──▶ Python analytics modules (src/analytics/) ──▶ Streamlit UI (src/dashboard/)
                       ╲
                        ╲──▶ SQLite (db/nifty100.db)  [used by a minority of modules]
```

There is no live data feed, no message queue, no background job scheduler, and no API layer in the running system (`src/api/` does not exist, despite being referenced by the `Makefile`). The system is designed to be run as a **local, single-user Streamlit application** against a static snapshot of Nifty 100 financial data sourced from Bluestock Fintech.

**Key architectural fact that shapes everything else in this document:** the platform has **two parallel, independent data-access patterns** that coexist without a clear boundary:

1. **Excel-direct**: the majority of analytics and dashboard modules call `pandas.read_excel("data/raw/<file>.xlsx", header=1)` on every invocation, recomputing from the raw source each time.
2. **SQLite-backed**: a minority of modules (`top_companies.py`, `company_history.py`, their dashboard page equivalents, and `load_financial_ratios.py`) query `db/nifty100.db` instead.

These two patterns are **not unified or synchronized** — there is no caching layer, no single "repository" abstraction, and the SQLite database is not kept in sync with the Excel files beyond a one-time manual load. A new engineer should not assume that updating `db/nifty100.db` will be reflected in most of the dashboard, or vice versa.

---

## 2. Architectural Principles (as observed)

These are not principles asserted by project documentation — none of the original code contains an architecture decision record or design doc — but principles **inferable from consistent patterns in the code itself**:

- **Static methods for pure calculations.** `RatioEngine`, `CashFlowKPIs`, and `CAGRCalculator` are all implemented as classes with only `@staticmethod`s — they hold no state and are effectively namespaced function libraries. This makes them trivially unit-testable, which is reflected in the test suite (all 18 KPI-layer tests target exactly these three classes).
- **DataFrame-in, DataFrame-out for transformation functions.** Functions like `calculate_revenue_growth(df)`, `quality_score(df)`, `normalize_column_names(df)` all take a DataFrame and return a modified copy (`.copy()` is consistently used to avoid mutating the caller's frame). This is a clean, composable pattern that's followed with reasonable discipline throughout `src/analytics/`.
- **`sys.path.append` for cross-package imports.** Because `src/analytics/` and `src/dashboard/modules/` are siblings rather than nested packages with a shared root `__init__.py` strategy, most files that need to import across the boundary (e.g., a dashboard page importing an analytics engine) insert the project's `src/` directory onto `sys.path` at import time:
  ```python
  from pathlib import Path
  import sys
  sys.path.append(str(Path(__file__).resolve().parents[2]))
  from analytics.financial_health import FinancialHealthAnalyzer
  ```
  This pattern appears in `master_ranking.py`, `build_financial_ratios.py`, `build_capital_allocation.py`, `company_snapshot_page.py`, `financial_health_page.py`, `winner_dashboard_page.py`, `sector_analytics_page.py`, `valuation_dashboard_page.py`, `growth_dashboard_page.py`, `master_ranking_dashboard_page.py`, and `quality_dashboard_page.py` — 11 files use it consistently. Three files deviate from it (see Section 11).
- **Relative-path file I/O assumes execution from repository root.** Every `pd.read_excel("data/raw/...")` and `sqlite3.connect("db/nifty100.db")` call uses a path relative to the current working directory, not relative to the file itself (no `Path(__file__).parent` resolution for data paths). This was **confirmed by execution**: running `python src/etl/load_companies.py` from inside `src/etl/` raises `FileNotFoundError: data/raw/companies.xlsx`; running the identical command from the repository root succeeds and reports `92 companies loaded.`
- **Composable, layered scoring.** Quality Score → Financial Score → Master Score → Future Winner Score is a genuine layered design: each score is computed independently and then blended with fixed weights into the next tier up. This is the most architecturally coherent part of the codebase.

---

## 3. Folder Structure Breakdown

```
N100-Financial-Intelligence-main/
│
├── Makefile                        # 7 targets; 2 are non-functional (pipeline, api) — see Section 4 & 7
├── README.md                       # Original repo README described only "Sprint 1"; superseded by the regenerated README.md
├── requirements.txt                 # UTF-16-LE encoded, CRLF line endings, ~150 packages, missing scikit-learn
├── .gitignore                       # Ignores venv/, __pycache__/, db/*.db, output/*.csv, logs/*.log
│
├── db/
│   └── schema.sql                  # 2 CREATE TABLE statements (companies, profit_loss) + balance_sheet = 3 tables total
│                                     # (financial_ratios is created dynamically elsewhere — see Section 8)
│
├── data/
│   ├── raw/                        # 12 Excel files, all sourced from "Bluestock Fintech — Nifty 100"
│   │   ├── companies.xlsx           # header row 1; 92 rows; PK: id
│   │   ├── profitandloss.xlsx       # header row 1 (row 0 is a title banner); 1,263 rows; 100 unique company_id
│   │   ├── balancesheet.xlsx        # header row 1; 1,312 rows
│   │   ├── cashflow.xlsx            # header row 1; 1,187 rows
│   │   ├── sectors.xlsx             # header row 0 (no title banner); 92 rows; 10 broad_sector values
│   │   ├── stock_prices.xlsx        # header row 0; 5,520 rows; daily OHLC, 2020-01-01 to 2024-12-01
│   │   ├── financial_ratios.xlsx    # header row 0; 1,184 rows; PRE-SUPPLIED, distinct from the platform's own CSV output
│   │   ├── market_cap.xlsx          # header row 0; 552 rows; UNUSED — not read by any module
│   │   ├── analysis.xlsx            # header row 1; 20 rows; UNUSED
│   │   ├── documents.xlsx           # header row 1; 1,585 rows; UNUSED
│   │   ├── peer_groups.xlsx         # header row 0; UNUSED
│   │   └── prosandcons.xlsx         # header row 1; 16 rows; UNUSED
│   └── processed/
│       └── financial_ratios.csv    # 1,370 rows; output of build_financial_ratios.py; contains ≥1 duplicate composite key
│
├── src/
│   ├── __init__.py                  # present — makes src/ a regular package
│   ├── etl/
│   │   ├── __init__.py              # present
│   │   ├── loader.py                # load_excel() — generic Excel reader with header-row promotion
│   │   ├── normaliser.py            # normalize_column_names / normalize_ticker / normalize_year / normalize_text_columns
│   │   ├── validator.py             # check_nulls / check_duplicates / check_primary_key / check_composite_key
│   │   ├── balance_validator.py     # same validator functions, duplicated, specialized for balance sheet
│   │   ├── db_utils.py              # get_connection() — single source of the "db/nifty100.db" path string
│   │   ├── create_db.py             # executes db/schema.sql against a new SQLite file
│   │   ├── reset_db.py              # DELETEs all rows from all 3 schema tables
│   │   ├── load_companies.py        # Excel → companies table
│   │   ├── load_profit_loss.py      # Excel → profit_loss table
│   │   ├── load_balance_sheet.py    # Excel → balance_sheet table
│   │   ├── check_db.py              # lists table names
│   │   ├── check_companies.py       # SELECT COUNT(*) FROM companies
│   │   ├── check_profit_loss.py     # SELECT COUNT(*) FROM profit_loss
│   │   ├── check_balance_sheet.py   # SELECT COUNT(*) FROM balance_sheet
│   │   └── run_pipeline.py          # EMPTY FILE (0 bytes) — Not implemented in repository
│   │
│   ├── analytics/                   # NO __init__.py present (relies on Python 3 implicit namespace packages)
│   │   ├── ratios.py                # RatioEngine — 7 static methods
│   │   ├── cagr.py                  # CAGRCalculator — 1 static method with 6-way status flag
│   │   ├── cashflow_kpis.py         # CashFlowKPIs — 4 static methods
│   │   ├── growth.py                # YoY growth calculation + leaderboard + summary
│   │   ├── ranking.py                # top_revenue_growth / top_profit_growth helpers (operate on growth.py's output)
│   │   ├── quality.py                # normalize() + quality_score() + remove_extreme_growth()
│   │   ├── profitability.py          # operating_margin / net_profit_margin row-wise helpers (superseded by financial_health.py's vectorized version)
│   │   ├── financial_health.py       # FinancialHealthAnalyzer — vectorized np.where metrics + rule-based rating
│   │   ├── valuation.py              # ValuationAnalyzer — PE ratio + Under/Fair/Overvalued bucketing
│   │   ├── scoring_engine.py         # FinancialScoringEngine — 5-input weighted composite score
│   │   ├── scoring.py                # EMPTY FILE (0 bytes) — Not implemented in repository
│   │   ├── winner_analytics.py       # WinnerAnalytics — leaderboard/top/bottom wrapper around a pre-scored DataFrame
│   │   ├── master_ranking.py         # get_master_ranking() — orchestrates Quality + Financial + Valuation → Master Score
│   │   ├── company_compare.py        # 2-company comparison view over master_ranking() output
│   │   ├── company_history.py       # standalone script — hardcoded ticker "ABB", runs at import time
│   │   ├── analytics_report.py       # AnalyticsReport.company_snapshot() — single-company latest-year summary dict
│   │   ├── analytics_runner.py       # standalone script combining profitability+growth+health; uses bare imports (inconsistent with rest of repo)
│   │   ├── sector_analytics.py       # sector-level aggregation from sectors.xlsx
│   │   ├── top_companies.py          # standalone script — 3 SQL queries against companies table, runs at import time
│   │   ├── build_financial_ratios.py # merges P&L + BS + CF, computes 11 ratio/KPI columns, writes processed CSV
│   │   ├── build_financial_ratios.pybuild_financial_ratios.py  # EMPTY, malformed filename — stray artifact, recommend deletion
│   │   ├── build_capital_allocation.py # applies capital_allocation_pattern() across cashflow.xlsx, writes output/capital_allocation.csv
│   │   ├── build_ratio_edge_cases.py  # scans financial_ratios.csv for missing/extreme ratios, writes logs/ratio_edge_cases.log; runs at import time
│   │   ├── ratio_analytics.py        # RatioAnalytics — reads data/raw/financial_ratios.xlsx (the pre-supplied file, NOT the processed CSV)
│   │   ├── load_financial_ratios.py  # reads processed CSV → writes financial_ratios SQLite table (only script that creates this table)
│   │   ├── growth_prediction.py      # GrowthPredictor — rule-based growth score from latest 2 fiscal years (NOT ML)
│   │   ├── health_prediction.py      # HealthPredictor — rule-based health label from fixed thresholds (NOT ML)
│   │   ├── revenue_forecasting.py    # RevenueForecaster — sklearn LinearRegression per company (genuine ML)
│   │   ├── profit_forecasting.py     # ProfitForecaster — sklearn LinearRegression per company (genuine ML)
│   │   ├── eps_forecasting.py        # EPSForecaster — sklearn LinearRegression per company (genuine ML)
│   │   ├── future_winners.py         # FutureWinners — blends master_ranking() + growth_prediction() into future_winner_score
│   │   └── ai_insights.py            # AIInsights — maps future_winner_score to a templated Buy/Hold/Avoid recommendation (NOT ML/AI)
│   │
│   └── dashboard/                    # NO __init__.py present
│       ├── app.py                    # Streamlit entrypoint; sidebar router; 19 elif branches, 17 reachable
│       └── modules/                  # NO __init__.py present
│           ├── executive_command_center_page.py  # Home page
│           ├── top_companies_page.py
│           ├── company_history_page.py
│           ├── company_compare_page.py
│           ├── company_snapshot_page.py
│           ├── financial_health_page.py
│           ├── winner_dashboard_page.py
│           ├── sector_analytics_page.py
│           ├── valuation_dashboard_page.py
│           ├── growth_dashboard_page.py
│           ├── master_ranking_dashboard_page.py
│           ├── ratio_analytics_page.py            # ORPHANED — imported + branch exists, but no sidebar entry
│           ├── quality_dashboard_page.py           # ORPHANED — not imported, no branch, no sidebar entry
│           ├── revenue_forecasting_page.py
│           ├── profit_forecasting_page.py
│           ├── eps_forecasting_page.py
│           ├── health_prediction_page.py
│           ├── growth_prediction_page.py
│           ├── future_winners_page.py
│           ├── ai_insights_page.py
│           └── master_ranking.py                   # EMPTY FILE (0 bytes) — distinct stray file, not the dashboard page
│
└── tests/
    ├── __init__.py
    ├── etl/
    │   ├── __init__.py
    │   ├── test_normaliser.py        # 35 tests — all passing
    │   ├── test_loader.py            # EMPTY FILE — Not implemented in repository
    │   └── test_validator.py         # EMPTY FILE — Not implemented in repository
    └── kpi/                          # NO __init__.py present
        ├── test_cagr.py              # 5 tests — all passing
        ├── test_cashflow.py          # 6 tests — all passing
        └── test_ratios.py            # 7 tests — all passing
```

---

## 4. Data Pipeline Architecture

### 4.1 Intended pipeline (per the Makefile and naming conventions)

```
make load      →  python src/etl/loader.py        (demo script only — prints summaries, does not persist)
make validate  →  python src/etl/validator.py       (demo script only — prints null/duplicate counts, writes one CSV)
make pipeline  →  python src/etl/run_pipeline.py     (EMPTY — Not implemented in repository)
make dashboard →  streamlit run src/dashboard/app.py (works)
make api       →  uvicorn src.api.main:app --reload  (FAILS — src/api/ does not exist)
make test      →  pytest tests/                      (works — 53/53 passing, confirmed by execution)
```

`make load` and `make validate` are somewhat misleadingly named: `src/etl/loader.py`'s `__main__` block only loads `companies.xlsx` and `profitandloss.xlsx` into in-memory DataFrames and prints a summary — it does **not** write to SQLite. The actual SQLite-writing scripts are `load_companies.py`, `load_profit_loss.py`, and `load_balance_sheet.py`, none of which are exposed as Makefile targets.

### 4.2 Actual working pipeline (verified by execution during this audit)

```
Step 1:  python src/etl/create_db.py
         └─ Reads db/schema.sql, executes against a fresh db/nifty100.db
         └─ VERIFIED: "Database created successfully."

Step 2:  python src/etl/load_companies.py
         └─ load_excel("data/raw/companies.xlsx")     [loader.py: promotes row 0 to header, drops it]
         └─ normalize_column_names(df)                 [normaliser.py: lowercase, snake_case, % → percentage]
         └─ normalize_text_columns(df)                  [normaliser.py: strips whitespace, replaces newlines]
         └─ Subsets to 7 schema columns
         └─ df.to_sql("companies", conn, if_exists="append")
         └─ VERIFIED: "92 companies loaded."

Step 3:  python src/etl/load_profit_loss.py
         └─ load_excel("data/raw/profitandloss.xlsx")
         └─ normalize_column_names(df)
         └─ df.to_sql("profit_loss", conn, if_exists="append")    [NOTE: no column subsetting — all Excel columns land in the table]

Step 4:  python src/etl/load_balance_sheet.py
         └─ Same pattern as Step 3, targeting balance_sheet table
```

**Important distinction between `load_excel()`'s header handling and the analytics layer's header handling.** `loader.py`'s `load_excel()` always promotes **row 0** (`df.iloc[0]`) to be the new header — appropriate for files where `pandas.read_excel()`'s default header (row 0) is a title banner, not real column names. This matches all the ETL-consumed files. The analytics layer, however, calls `pd.read_excel(path, header=1)` directly in most places — functionally equivalent for these particular files (both approaches end up using row index 1 as the effective header), but implemented via two different mechanisms. A new file with a different banner-row convention would need to be handled differently depending on which code path consumes it.

### 4.3 Validation layer

`validator.py` and `balance_validator.py` provide four reusable checks:

| Function | Purpose |
|---|---|
| `check_nulls(df)` | Per-column null count |
| `check_duplicates(df)` | Full-row duplicate count |
| `check_primary_key(df, column)` | Duplicate count on a single column |
| `check_composite_key(df, columns)` | Duplicate count on a column combination |

Both files' `__main__` blocks **do not stop at the `if __name__` guard** — in `validator.py`, lines 56–116 (the bulk of the composite-key duplicate analysis and the `output/validation_failures.csv` write) execute unconditionally at module level, **outside** the `if __name__ == "__main__":` block that only wraps lines 36–54. This means `import validator` from anywhere will trigger file reads and a CSV write as a side effect. The same pattern (unconditional execution past an early `__main__` block) exists in `balance_validator.py`.

Validation is currently **diagnostic only** — there is no validate-then-reject gate in the load scripts. `load_companies.py`, `load_profit_loss.py`, and `load_balance_sheet.py` call `to_sql()` directly with no call to any `validator.py` function first. Validation and loading are two separate, disconnected workflows that happen to read the same source files.

### 4.4 Processed-data builders (analytics-adjacent, but logically part of the pipeline)

```
build_financial_ratios.py:
  pnl = read_excel(profitandloss.xlsx, header=1)
  bs  = read_excel(balancesheet.xlsx, header=1)
  cf  = read_excel(cashflow.xlsx, header=1)
  df  = pnl.merge(bs, on=[company_id, year], how=left)
           .merge(cf, on=[company_id, year], how=left)
  → applies RatioEngine + CashFlowKPIs row-wise via df.apply(axis=1)
  → writes data/processed/financial_ratios.csv  (1,370 rows)

build_capital_allocation.py:
  cf = read_excel(cashflow.xlsx, header=1)
  → applies CashFlowKPIs.capital_allocation_pattern() row-wise
  → writes output/capital_allocation.csv

build_ratio_edge_cases.py:
  df = read_csv(data/processed/financial_ratios.csv)
  → flags missing ROE/ROA/interest coverage, and Debt/Equity > 5
  → writes logs/ratio_edge_cases.log

load_financial_ratios.py:
  df = read_csv(data/processed/financial_ratios.csv)
  → df.to_sql("financial_ratios", conn, if_exists="replace")
```

**This chain has a hidden ordering dependency that is not enforced by any orchestration code:** `build_financial_ratios.py` must run before `build_ratio_edge_cases.py` and before `load_financial_ratios.py`, since both consume the CSV the first script produces. There is currently no `run_pipeline.py` implementation to enforce this order — a contributor must know to run them in sequence manually.

### 4.5 Row-count discrepancy worth flagging in this layer

`build_financial_ratios.py`'s three-way merge (`pnl.merge(bs).merge(cf)`) produces **1,370 rows** in the output CSV, despite the three source files having row counts of 1,263 (P&L), 1,312 (BS), and 1,187 (CF). A left join starting from 1,263 P&L rows growing to 1,370 output rows indicates a **fan-out**: at least one `(company_id, year)` key is non-unique in `balancesheet.xlsx` or `cashflow.xlsx`, causing some P&L rows to match more than one row on the right side of the merge. This is consistent with the observed duplicate composite key (`ABB`, `Mar 2014`) in the processed CSV described in Section 12.

---

## 5. Analytics Layer Architecture

### 5.1 Layering model

The analytics layer is best understood as four ascending tiers, each consuming the tier below:

```
TIER 0 — Raw metric calculators (pure functions/static methods, fully unit tested)
  RatioEngine · CAGRCalculator · CashFlowKPIs

TIER 1 — Per-row / per-company derived metrics (DataFrame transformations)
  growth.py · quality.py · financial_health.py · valuation.py · sector_analytics.py
  growth_prediction.py · health_prediction.py

TIER 2 — Composite scoring (blends Tier 1 outputs with fixed weights)
  scoring_engine.py (Financial Score) · quality.py's quality_score() (Quality Score)
  valuation.py's PE-derived Valuation Score

TIER 3 — Orchestration / ranking (combines Tier 2 scores across the company universe)
  master_ranking.py (Master Score = 0.40·Financial + 0.35·Quality + 0.25·Valuation)
  future_winners.py (Future Winner Score = 0.60·Master + 0.40·Growth)
  ai_insights.py (maps Future Winner Score → recommendation label)
```

This is a coherent design **in principle**. In practice, Tier 1 has duplication: `profitability.py`'s `operating_margin()`/`net_profit_margin()` row-wise functions compute the same thing as `financial_health.py`'s vectorized `np.where`-based equivalents, and only the latter is actually used by the dashboard (`financial_health_page.py`, `company_snapshot_page.py`). `profitability.py` is only consumed by the standalone `analytics_runner.py` script, which is itself not called from the dashboard or any Makefile target.

### 5.2 Engine-by-engine input/output contract

| Engine | Inputs | Output | Consumed by |
|---|---|---|---|
| `RatioEngine` | scalar financial figures (net_profit, sales, equity_capital, etc.) | scalar ratio or `None` | `build_financial_ratios.py` |
| `CAGRCalculator` | start_value, end_value, years | `(float or None, status_flag str)` | Not currently called by any dashboard page — available but unused in the UI |
| `CashFlowKPIs` | scalar cash flow figures | scalar/label | `build_financial_ratios.py`, `build_capital_allocation.py` |
| `growth.py` | full P&L DataFrame | DataFrame with `revenue_growth_pct`, `profit_growth_pct`, `growth_score` columns | `growth_dashboard_page.py`, `executive_command_center_page.py` (via `growth_prediction.py`, a separate but related module) |
| `quality.py` | full P&L DataFrame | DataFrame with `opm_score`, `eps_score`, `dividend_score`, `quality_score` | `master_ranking.py`, `quality_dashboard_page.py` (orphaned) |
| `financial_health.py` | full P&L DataFrame | DataFrame with margin/coverage/quality metrics + Risky/Average/Healthy rating | `financial_health_page.py`, `company_snapshot_page.py` |
| `valuation.py` (`ValuationAnalyzer`) | `stock_prices.xlsx` + `profitandloss.xlsx` | DataFrame with `pe_ratio`, `valuation_status` | `valuation_dashboard_page.py`, `master_ranking.py` |
| `sector_analytics.py` | `sectors.xlsx` | dict of summary/leaderboard/crosstab DataFrames | `sector_analytics_page.py` |
| `scoring_engine.py` (`FinancialScoringEngine`) | DataFrame with `market_cap`, `revenue`, `net_income`, `profit_margin`, `eps` columns | DataFrame + `financial_score` column | `master_ranking.py`, `winner_dashboard_page.py` |
| `master_ranking.py` | latest-year P&L + Quality + Financial + Valuation scores | ranked DataFrame with `master_score`, `rank` | `master_ranking_dashboard_page.py`, `company_compare.py`, `future_winners.py` |
| `growth_prediction.py` (`GrowthPredictor`) | full P&L DataFrame, last 2 years per company | ranked DataFrame with `growth_score`, `rank` | `growth_prediction_page.py`, `future_winners.py`, `executive_command_center_page.py` |
| `future_winners.py` (`FutureWinners`) | `master_ranking()` + `GrowthPredictor` output | ranked DataFrame with `future_winner_score`, `future_rank` | `future_winners_page.py`, `ai_insights.py`, `executive_command_center_page.py` |
| `ai_insights.py` (`AIInsights`) | single company's row from `FutureWinners` output | dict with `recommendation`, `insight` text | `ai_insights_page.py` |
| `health_prediction.py` (`HealthPredictor`) | single company's latest P&L row | dict with `health` label | `health_prediction_page.py` |
| `RevenueForecaster` / `ProfitForecaster` / `EPSForecaster` | single company's historical P&L rows (≥3 years) | dict with `next_year`, `predicted_<metric>` | corresponding `*_forecasting_page.py` |

### 5.3 Business value per engine (as actually delivered, not as aspirationally named)

- **RatioEngine / CashFlowKPIs**: genuine, auditable financial analysis — these are the most "real" parts of the analytics layer and are the only parts with meaningful unit test coverage.
- **CAGRCalculator**: a thoughtful piece of defensive design (the 6-way status flag) that is **currently not surfaced anywhere in the dashboard** — it exists and is tested, but a user of the running app cannot currently see a CAGR figure or its edge-case flag. This is a capability gap between "what the code can do" and "what the user can see."
- **Quality / Financial / Master / Future Winner Scores**: useful relative-ranking tools within this specific dataset, but all rely on fixed, hand-picked weights (e.g., 40/35/25, 60/40) with no documented derivation, backtesting, or sensitivity analysis. They should be understood as a **heuristic screening tool**, not a validated quantitative model.
- **AI Insights**: delivers a templated text recommendation derived entirely from the Future Winner Score's threshold bucket — it adds a thin presentation layer on top of an existing number, not new analytical content. See Section 6 for the distinction between this and the genuinely ML-based forecasters.

---

## 6. Forecasting Layer Architecture

There are exactly **three genuinely model-based components** in this repository, and they are architecturally identical:

```python
class <X>Forecaster:
    def __init__(self):
        self.df = pd.read_excel("data/raw/profitandloss.xlsx", header=1)

    def clean_data(self):
        df = self.df.copy()
        df["year_num"] = df["year"].astype(str).str.extract(r"(\d{4})")
        df = df.dropna(subset=["year_num"])
        df["year_num"] = df["year_num"].astype(int)
        return df

    def predict_company_<metric>(self, company_id):
        df = self.clean_data()
        company = df[df["company_id"] == company_id].sort_values("year_num")
        X = company[["year_num"]]
        y = company["<sales|net_profit|eps>"]
        if len(company) < 3:
            return None
        model = LinearRegression()
        model.fit(X, y)
        next_year = int(company["year_num"].max() + 1)
        prediction = float(model.predict(pd.DataFrame({"year_num": [next_year]}))[0])
        return {"company_id": ..., "next_year": next_year, "predicted_<metric>": round(prediction, 2)}
```

`year_num` extraction via regex (`str.extract(r"(\d{4})")`) is necessary because the raw `year` column contains mixed formats (`"Mar 2014"`, `"Dec 2012"`, `"TTM"`). Rows where the regex fails to match a 4-digit year — notably the `"TTM"` (trailing twelve months) rows — are dropped via `dropna(subset=["year_num"])`. This means **the most recent trailing-twelve-month figures are excluded from every forecast's training data**, even though they are arguably the most current and relevant data point available. This is a meaningful modeling choice that isn't documented or flagged anywhere in the code.

**Model characteristics:**
- Algorithm: ordinary least squares linear regression (`sklearn.linear_model.LinearRegression`), one independent feature (`year_num`).
- Trained **per company, per metric, on every page load** — there is no model persistence (no pickling, no cached fitted models). Each Streamlit interaction refits from scratch.
- Minimum data requirement: 3 historical (non-TTM) fiscal years. Recently-listed companies or those with sparse history return `None` and the dashboard shows "Not enough historical data."
- No evaluation: no R², MAE, RMSE, residual analysis, or backtest is computed anywhere in the codebase. There is currently no programmatic way to know if a given company's forecast is reliable.
- No regularization, no polynomial/log features, no seasonality — a straight line through historical annual figures.

**Two rule-based modules are deliberately distinguished here from the above, despite similar naming:**

- `HealthPredictor.get_latest_company_data()` computes a weighted sum (`revenue*0.4 + profit*0.4 + eps*0.2`) and buckets it against three hardcoded thresholds (5000, 2000, 500) with no normalization for company size — a company with revenue in the tens of thousands will trivially score "Excellent" regardless of profitability ratios, while a small but highly profitable company could score "Weak." This is a known scale-sensitivity limitation of the current formula.
- `GrowthPredictor.get_growth_ranking()` computes growth percentages directly from the latest two fiscal years' P&L figures (`(latest - previous) / max(previous, 1)`), with no fitting step at all.

Neither involves training, a model object, or `scikit-learn`. They are correctly described as **rule-based heuristics**, and the README and this document deliberately avoid calling them "predictive models" or "ML" to keep user expectations accurate.

---

## 7. Dashboard Layer Architecture

### 7.1 Routing mechanism

`src/dashboard/app.py` is a single-file, **linear `if/elif` chain keyed on a sidebar `st.selectbox` value** — there is no Streamlit multipage-app folder structure (`pages/`) in use, despite Streamlit supporting that pattern natively. Each branch either inlines its own `st.dataframe`/`px.bar` calls directly in `app.py`, or (more commonly in the later sections of the file) delegates entirely to a `get_*_dashboard()` function imported from `modules/`.

**Verified branch-to-sidebar mapping** (by direct inspection of `app.py`):

```
Sidebar selectbox options (as literally listed in code, in order):
  Home, Top Companies, Company History, Company Comparison, Financial Health,
  Company Snapshot, Winner Dashboard, Sector Analytics, Valuation Dashboard,
  Growth Dashboard, Master Ranking, Revenue Forecasting, Profit Forecasting,
  EPS Forecasting, Health Prediction, Growth Prediction, Future Winners,
  AI Insights, Home          ← "Home" duplicated; "Ratio Analytics" absent

elif branches defined in code (in order):
  Home, Top Companies, Company History, Company Comparison, Financial Health,
  Company Snapshot, Winner Dashboard, Sector Analytics, Valuation Dashboard,
  Growth Dashboard, Master Ranking, Ratio Analytics ← UNREACHABLE,
  Revenue Forecasting, Profit Forecasting, EPS Forecasting, Health Prediction,
  Growth Prediction, Future Winners, AI Insights
```

The mismatch means: selecting the second "Home" entry in the dropdown re-renders the same Home page (harmless but confusing UX); there is no way to reach the "Ratio Analytics" branch through the UI at all, since its string never appears in the `selectbox` options list.

`quality_dashboard_page.py` is a complete, working module (`get_quality_dashboard()` returns summary/top/bottom DataFrames cleanly) that is simply **never imported into `app.py`** — not in the import block, not in the sidebar list, not in any `elif`. It is fully orphaned, one level more disconnected than Ratio Analytics.

### 7.2 Page-to-engine dependency pattern

Dashboard pages follow one of two patterns:

**Pattern A — Page does its own data loading + light orchestration** (e.g., `winner_dashboard_page.py`, `quality_dashboard_page.py`):
```python
df = pd.read_excel("data/raw/profitandloss.xlsx", header=1)
# inline renames / derived columns (e.g., market_cap = revenue * 10)
engine = SomeEngine()
result = engine.calculate_scores(df)
return result
```

**Pattern B — Page delegates entirely to an analytics class** (e.g., `future_winners_page.py`, `growth_prediction_page.py`, the three forecasting pages):
```python
model = SomeAnalyticsClass()
df = model.some_method()
# render directly
```

Pattern A duplicates the `market_cap = revenue * 10` substitution and the `sales→revenue / net_profit→net_income / opm_percentage→profit_margin` column renaming **independently in at least three places** (`master_ranking.py`, `winner_dashboard_page.py`, and implicitly wherever `FinancialScoringEngine` is invoked) rather than centralizing it in one shared data-preparation function. A change to this renaming convention currently requires updating multiple files in lockstep.

### 7.3 Visualization stack

All charts use `plotly.express` (`px.bar`, `px.line`), rendered via `st.plotly_chart(fig, use_container_width=True)`. There is no caching (`st.cache_data` / `st.cache_resource` is not used anywhere in the codebase), meaning every Excel read, every score computation, and every model fit re-executes on every page interaction and every sidebar switch. For a 100-company, multi-year dataset of this size this is not yet a performance problem in practice, but it is an architectural gap relevant to the [Scalability Assessment](#13-scalability-assessment).

---

## 8. Database Layer Architecture

### 8.1 Schema as defined vs. schema as actually populated

`db/schema.sql` defines exactly three tables: `companies`, `profit_loss`, `balance_sheet`. A fourth table, `financial_ratios`, is created **only if** `src/analytics/load_financial_ratios.py` is run — via `pandas.DataFrame.to_sql(..., if_exists="replace")`, which lets pandas infer the schema from the DataFrame's dtypes rather than from any DDL. This means `financial_ratios`'s schema is **not documented in `schema.sql`** and would change shape automatically if `build_financial_ratios.py`'s output columns ever change — there is no migration or schema versioning for this table.

### 8.2 Foreign key enforcement

Both `profit_loss` and `balance_sheet` declare `FOREIGN KEY(company_id) REFERENCES companies(id)` in `schema.sql`. **SQLite does not enforce foreign keys by default** — enforcement requires `PRAGMA foreign_keys = ON` to be set on each connection, and no file in this repository (`db_utils.py`, any `load_*.py`, or `create_db.py`) sets this pragma. The constraint is therefore documentation-only in the current implementation.

This is not a hypothetical concern: the audit confirmed 8 `company_id` values present in `profitandloss.xlsx` (`ULTRACEMCO`, `UNIONBANK`, `UNITDSPR`, `VBL`, `VEDL`, `WIPRO`, `ZOMATO`, `ZYDUSLIFE`) with **no corresponding row** in `companies.xlsx`. Because the foreign key is unenforced, `load_profit_loss.py` will load these rows into `profit_loss` without error. Any query that `JOIN`s `profit_loss` to `companies` (the pattern used by `top_companies_page.py` and similar) will silently exclude these 8 companies' financial history.

### 8.3 Which modules actually use SQLite

Of ~30 analytics and ~20 dashboard files, only these touch `db/nifty100.db`:

| File | Operation |
|---|---|
| `etl/create_db.py` | DDL execution |
| `etl/load_companies.py`, `load_profit_loss.py`, `load_balance_sheet.py` | `INSERT` via `to_sql(if_exists="append")` |
| `etl/reset_db.py` | `DELETE FROM` all 3 tables |
| `etl/check_db.py`, `check_companies.py`, `check_profit_loss.py`, `check_balance_sheet.py` | read-only verification queries |
| `analytics/top_companies.py` | 3 `SELECT ... ORDER BY ... LIMIT 10` queries |
| `analytics/company_history.py` | 1 hardcoded-ticker `SELECT` |
| `analytics/load_financial_ratios.py` | `to_sql(if_exists="replace")` — the only writer of `financial_ratios` |
| `dashboard/modules/top_companies_page.py` | mirrors `top_companies.py`'s ROE query |
| `dashboard/modules/company_history_page.py` | mirrors `company_history.py`'s pattern, parameterized by UI selection |

Every other analytics engine and every other dashboard page reads from `data/raw/*.xlsx` directly via `pandas.read_excel()`, bypassing SQLite entirely. **The database is a secondary, partially-used data path, not the system of record it might appear to be from the schema design alone.**

### 8.4 Connection management

`db_utils.get_connection()` opens a new `sqlite3.connect("db/nifty100.db")` on every call with no pooling, no context manager usage at the call sites (callers manually call `.commit()` and `.close()`), and no error handling around connection failures. For a single-user local Streamlit app this is adequate; it would not scale to concurrent multi-user access without changes (see Section 13).

---

## 9. Testing Architecture

### 9.1 Coverage map (verified by running `pytest tests/ -v`)

```
53 passed in 0.75s
```

| Module Under Test | Test File | Test Count | Status |
|---|---|---|---|
| `etl/normaliser.py` (`normalize_ticker`, `normalize_year`) | `tests/etl/test_normaliser.py` | 35 | ✅ All passing |
| `analytics/cagr.py` (`CAGRCalculator`) | `tests/kpi/test_cagr.py` | 5 | ✅ All passing |
| `analytics/cashflow_kpis.py` (`CashFlowKPIs`) | `tests/kpi/test_cashflow.py` | 6 | ✅ All passing |
| `analytics/ratios.py` (`RatioEngine`) | `tests/kpi/test_ratios.py` | 7 | ✅ All passing |
| `etl/loader.py` | `tests/etl/test_loader.py` | 0 | ❌ Not implemented in repository (file exists, is empty) |
| `etl/validator.py` | `tests/etl/test_validator.py` | 0 | ❌ Not implemented in repository (file exists, is empty) |
| `etl/balance_validator.py` | — | 0 | ❌ Not implemented in repository (no test file exists at all) |
| `etl/load_companies.py`, `load_profit_loss.py`, `load_balance_sheet.py` | — | 0 | ❌ Not implemented in repository |
| `analytics/growth.py`, `quality.py`, `financial_health.py`, `valuation.py`, `sector_analytics.py` | — | 0 | ❌ Not implemented in repository |
| `analytics/scoring_engine.py`, `master_ranking.py`, `future_winners.py`, `ai_insights.py` | — | 0 | ❌ Not implemented in repository |
| `analytics/revenue_forecasting.py`, `profit_forecasting.py`, `eps_forecasting.py` | — | 0 | ❌ Not implemented in repository |
| Any `dashboard/` module | — | 0 | ❌ Not implemented in repository |

**Effective test coverage is concentrated entirely in the lowest, most stateless layer** (normalization helpers and Tier-0 static calculators from Section 5.1). This is a reasonable place to start a test suite, but it means the parts of the system most likely to silently produce wrong numbers under data changes — the merges in `build_financial_ratios.py`, the scoring weight blends, the forecaster's TTM-row-dropping behavior — currently have zero automated regression protection.

### 9.2 Test design patterns observed

- All tests are plain `pytest` functions using bare `assert` statements — no `pytest.fixture`, no parametrization (`@pytest.mark.parametrize`), no mocking. This keeps the suite simple to read but means each edge case is a fully separate, hand-written function (visible in `test_normaliser.py`'s 35 nearly-parallel test functions for `normalize_ticker`/`normalize_year`).
- Two distinct `sys.path` manipulation strategies coexist:
  - `test_normaliser.py` imports via `from src.etl.normaliser import ...` — relying on `pytest`'s rootdir-based import mode and the `src/__init__.py` + `src/etl/__init__.py` package structure, with no manual `sys.path` edit.
  - `test_cagr.py`, `test_cashflow.py`, `test_ratios.py` instead manually prepend `src/` to `sys.path` and import via `from analytics.cagr import ...` (treating `analytics` as a top-level package, since `src/analytics/` has no `__init__.py`).

  Both approaches work today (confirmed: 53/53 pass when run via plain `pytest tests/` from the repo root), but they reflect two different mental models of the package structure and would behave differently if the test runner's working directory or `rootdir` assumptions changed.

### 9.3 What "KPI validation," "analytics validation," and "data quality validation" actually mean in this repository

Mapping the audit prompt's requested categories onto what was actually found:

- **KPI validation**: present and solid — `test_ratios.py` and `test_cashflow.py` directly assert formula correctness and edge-case behavior (zero sales, negative equity, debt-free companies) against `RatioEngine` and `CashFlowKPIs`.
- **Analytics validation**: largely **not implemented in repository** — no test exercises `growth.py`, `quality.py`, `financial_health.py`, `scoring_engine.py`, or `master_ranking.py`'s actual blending logic and weights.
- **Data quality validation**: implemented as **diagnostic scripts, not as tests** — `validator.py`, `balance_validator.py`, and `build_ratio_edge_cases.py` perform null/duplicate/edge-case checks against live data and produce log/CSV output for human review, but none of this is wrapped in `pytest` assertions or run automatically as part of `make test`.

---

## 10. Data Flow Diagrams

### 10.1 End-to-end flow (as actually implemented, not aspirational)

```
┌──────────────────────────────────────────────────────────────────────────┐
│  data/raw/*.xlsx  (12 files, Bluestock Fintech — Nifty 100 export)        │
└───────────┬────────────────────────────────────────────┬───────────────────┘
            │                                            │
   (path A: SQLite-backed,                    (path B: Excel-direct,
    minority of modules)                       majority of modules)
            │                                            │
            ▼                                            ▼
┌───────────────────────────┐          ┌──────────────────────────────────────┐
│ src/etl/create_db.py       │          │ pandas.read_excel(..., header=1)      │
│ src/etl/load_companies.py  │          │ called independently inside:           │
│ src/etl/load_profit_loss.py│          │  growth.py, quality.py,                │
│ src/etl/load_balance_sheet │          │  financial_health.py, valuation.py,    │
│       ↓                    │          │  master_ranking.py, scoring_engine.py  │
│ db/nifty100.db              │          │  (via callers), growth_prediction.py,  │
│  - companies (92 rows)      │          │  health_prediction.py,                 │
│  - profit_loss (1,263 rows) │          │  revenue/profit/eps_forecasting.py,    │
│  - balance_sheet (1,312)    │          │  every *_page.py except                │
│       ↓                    │          │  top_companies_page / company_history  │
│ used by:                    │          └──────────────────┬───────────────────────┘
│  top_companies(_page).py    │                             │
│  company_history(_page).py  │                             ▼
└───────────┬──────────────────┘          ┌──────────────────────────────────────┐
            │                              │  Tier 0/1 calculators & transforms     │
            │                              │  → Tier 2 composite scores             │
            │                              │  → Tier 3 Master / Future Winner Rank   │
            │                              └──────────────────┬───────────────────────┘
            │                                                 │
            ▼                                                 ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                  src/dashboard/app.py (Streamlit sidebar router)          │
│   17 reachable pages render st.dataframe / px.bar / px.line / st.metric    │
└──────────────────────────────────────────────────────────────────────────┘

Separately, an offline/batch branch:

data/raw/{profitandloss,balancesheet,cashflow}.xlsx
        │
        ▼  build_financial_ratios.py (3-way merge + RatioEngine + CashFlowKPIs)
data/processed/financial_ratios.csv  (1,370 rows)
        │
        ├──▶ build_ratio_edge_cases.py ──▶ logs/ratio_edge_cases.log
        │
        └──▶ load_financial_ratios.py ──▶ db/nifty100.db: financial_ratios table
                                            (NOT currently read back by any
                                             dashboard page — see Section 12)

data/raw/cashflow.xlsx
        │
        ▼  build_capital_allocation.py (CashFlowKPIs.capital_allocation_pattern)
output/capital_allocation.csv  (NOT currently read by any dashboard page)
```

### 10.2 Single-page data flow example — "Future Winners" (representative of the most architecturally complete chain)

```
data/raw/profitandloss.xlsx
        │
        ├──▶ master_ranking.get_master_ranking()
        │       ├─ quality.quality_score()                    → quality_score
        │       ├─ rename columns (sales→revenue, etc.)
        │       ├─ market_cap = revenue * 10  [synthetic proxy]
        │       ├─ scoring_engine.FinancialScoringEngine()      → financial_score
        │       └─ valuation.ValuationAnalyzer() [+ stock_prices.xlsx] → valuation_score
        │             └─ master_score = 0.40·financial + 0.35·quality + 0.25·valuation
        │
        ├──▶ growth_prediction.GrowthPredictor().get_growth_ranking() → growth_score
        │
        └──▶ future_winners.FutureWinners().get_future_winners()
                 future_winner_score = 0.60·master_score + 0.40·growth_score
                       │
                       ├──▶ future_winners_page.py  (leaderboard + bar chart)
                       ├──▶ ai_insights.py → ai_insights_page.py (templated recommendation)
                       └──▶ executive_command_center_page.py (Home page summary)
```

This single page touches **5 raw Excel reads** (`profitandloss.xlsx` is independently re-read inside `master_ranking.py` and again inside `growth_prediction.py`, plus `stock_prices.xlsx` inside `valuation.py`), with no shared caching — see Section 13.

---

## 11. Module Dependency Maps

### 11.1 Import-style consistency map

| File | Import strategy for cross-package analytics imports |
|---|---|
| `master_ranking.py`, `build_financial_ratios.py`, `build_capital_allocation.py` | `sys.path.append(parents[1])` then `from analytics.X import Y` |
| `company_snapshot_page.py`, `financial_health_page.py`, `winner_dashboard_page.py`, `sector_analytics_page.py`, `valuation_dashboard_page.py`, `growth_dashboard_page.py`, `master_ranking_dashboard_page.py`, `quality_dashboard_page.py` | `sys.path.append(parents[2])` then `from analytics.X import Y` |
| `app.py` | `sys.path.append(parent.parent)` (after some imports have already executed — see 11.2) then `from analytics.X import Y` |
| `company_compare_page.py`, `ratio_analytics_page.py`, `future_winners_page.py`, `growth_prediction_page.py`, `ai_insights_page.py`, `revenue_forecasting_page.py`, `profit_forecasting_page.py`, `eps_forecasting_page.py`, `health_prediction_page.py`, `executive_command_center_page.py` | `from analytics.X import Y` with **no explicit `sys.path.append`** in the file itself — relies on `app.py` (or Streamlit's own working-directory behavior) having already put the right path on `sys.path` before these modules are imported |
| `analytics_runner.py` (standalone script) | Bare `from profitability import X` — **inconsistent**; only resolves if `analytics/` itself is the working directory or on `sys.path`, unlike every other file in the layer |

### 11.2 A subtlety in `app.py`'s own import order

`app.py` imports `from modules.master_ranking_dashboard_page import get_master_dashboard` and `from modules.ratio_analytics_page import get_ratio_dashboard` **before** its own `sys.path.append(str(Path(__file__).resolve().parent.parent))` call. This works in practice only because Streamlit's execution model adds the script's own directory (`src/dashboard/`) to `sys.path` automatically, which is sufficient for the `modules.*` imports (siblings of `app.py`) but would not be sufficient for any `analytics.*` import attempted before the explicit `sys.path.append` line. The ordering is fragile rather than incorrect — it works today because of where each import happens to sit relative to the one `sys.path.append` call, not because of a deliberate, documented import order policy.

### 11.3 Dependency graph — who depends on whom (Tier 3 → Tier 0)

```
ai_insights_page.py
  └─ ai_insights.AIInsights
       └─ future_winners.FutureWinners
            ├─ master_ranking.get_master_ranking
            │    ├─ quality.quality_score
            │    ├─ scoring_engine.FinancialScoringEngine
            │    └─ valuation.ValuationAnalyzer
            └─ growth_prediction.GrowthPredictor

future_winners_page.py
  └─ future_winners.FutureWinners   (same subtree as above)

executive_command_center_page.py
  ├─ future_winners.FutureWinners   (same subtree as above)
  └─ growth_prediction.GrowthPredictor

company_compare_page.py
  └─ company_compare.get_company_comparison
       └─ master_ranking.get_master_ranking

winner_dashboard_page.py
  ├─ scoring_engine.FinancialScoringEngine
  └─ winner_analytics.WinnerAnalytics

quality_dashboard_page.py  [ORPHANED — not reachable from app.py]
  └─ quality.{quality_summary, top_quality_companies, bottom_quality_companies}

ratio_analytics_page.py  [ORPHANED — unreachable elif branch]
  └─ ratio_analytics.RatioAnalytics
       └─ reads data/raw/financial_ratios.xlsx directly (NOT build_financial_ratios.py's output)
```

`master_ranking.py` is the single most depended-upon module in the entire analytics layer — it is a transitive dependency of `company_compare_page.py`, `future_winners_page.py`, `ai_insights_page.py`, and `executive_command_center_page.py`. A bug or schema change in `master_ranking.get_master_ranking()` has the widest blast radius in the codebase.

---

## 12. Current System Capabilities

**What works end-to-end today, verified by direct execution during this audit:**

- Building a fresh SQLite database and loading Companies (92 rows confirmed), Profit & Loss, and Balance Sheet data from Excel, run from the repository root.
- Running the full 53-test suite cleanly with `pytest tests/`.
- Launching the Streamlit dashboard and navigating to 17 of 19 implemented pages.
- Computing all seven `RatioEngine` ratios and four `CashFlowKPIs` metrics correctly against known inputs (test-verified).
- Producing a per-company next-year forecast for Revenue, Profit, or EPS via `LinearRegression`, for any company with ≥3 non-TTM historical years.
- Producing a blended Master Score and Future Winner ranking across the available company universe, surfaced on the Home page and three dedicated dashboard pages.

**What exists in code but is not currently reachable or connected:**

- Ratio Analytics dashboard page (missing sidebar entry).
- Quality Dashboard page (not imported into `app.py` at all).
- The `financial_ratios` SQLite table (populated only by a manual script run, not read back by any dashboard page once created).
- `output/capital_allocation.csv` (built by a standalone script, never visualized).
- `CAGRCalculator`'s edge-case-flagged growth rates (tested and correct, but not surfaced in any dashboard view — the dashboard's "growth" figures all come from `growth.py`'s simple YoY `pct_change()`, not CAGR).

**What is described by naming or by the original Sprint 1 README but is not implemented in repository:**

- A unified `run_pipeline.py` orchestration script — file exists, is empty.
- A FastAPI-based API layer — referenced by the `Makefile`, no `src/api/` directory exists.
- Any test coverage for the ETL loader/validator layer beyond normalization helpers.
- Any forecast accuracy or confidence metric for the three `LinearRegression` forecasters.

---

## 13. Scalability Assessment

This system was built and currently performs adequately for its actual scale: **~100 companies, single-digit-years of annual financial history, single local user.** The following constraints would become relevant at meaningfully larger scale or under different usage patterns:

**Compute / latency**
- No caching anywhere (`st.cache_data` unused). Every sidebar navigation re-reads the relevant Excel file(s) from disk and recomputes every derived score from scratch. At ~1,000-1,500 rows per source file this is fast; it would not remain fast if the universe grew from 100 to, say, 5,000 companies or if history grew from ~12 years to several decades, since several operations (e.g., `master_ranking.py`'s per-row `.apply(axis=1)` calls in `build_financial_ratios.py`) are not vectorized.
- The three forecasters refit a fresh `LinearRegression` per company on every page interaction rather than training once and persisting. This is currently invisible to the user because fitting a single-feature OLS model on a handful of points is near-instantaneous, but it does not amortize.

**Data architecture**
- Excel as the source-of-truth format does not scale gracefully to frequent updates or multi-user write access — there's no locking, versioning, or audit trail. A move to a proper warehouse table (or at minimum, treating SQLite consistently as the system of record instead of a partially-used side path) would be a prerequisite for any real-time or frequently-refreshed deployment.
- The dual Excel-direct / SQLite-backed access pattern (Section 8.3) means that scaling or hardening the database layer alone would only address a minority of the system's actual data access — most modules would need to be migrated to read from SQLite (or another store) to benefit.

**Concurrency**
- `sqlite3.connect()` calls with no pooling and no WAL-mode configuration are adequate for one local user but would contend under concurrent multi-user access, which SQLite is not architected for at any significant scale.
- Streamlit's own single-process model means concurrent users of a shared deployment would all share CPU for these uncached recomputations.

**Operational**
- No logging framework (only ad hoc `print()` statements and one hand-rolled log file from `build_ratio_edge_cases.py`). Diagnosing a production issue would currently require re-running scripts manually rather than reading structured logs.
- No configuration management — all paths (`"data/raw/..."`, `"db/nifty100.db"`) are hardcoded string literals repeated across dozens of files rather than centralized in a config module or environment variable. Changing the database location or data directory today requires a multi-file find-and-replace.
- No containerization (`Dockerfile` absent) or CI/CD configuration (no `.github/workflows/`) found anywhere in the repository.

None of these are urgent given the system's current, real-world scale — they are listed because "scalability assessment" was explicitly requested, and a fair assessment is that this is appropriately built for a single-user local analytics tool, not yet for a multi-user or large-universe deployment.

---

## 14. Recommended Future Improvements

In addition to the prioritized roadmap in `README.md`, from a purely architectural standpoint:

1. **Pick one data access pattern and migrate to it consistently.** Either commit to SQLite as the system of record (and update every Excel-direct module to read from it) or commit to Excel-direct + an in-memory cache (and stop maintaining the partially-populated database). The current half-and-half state is the single largest source of confusion for a new contributor.
2. **Introduce a shared data-preparation function** for the `sales→revenue`/`net_profit→net_income`/`market_cap = revenue*10` renaming pattern that's currently duplicated across `master_ranking.py` and `winner_dashboard_page.py`.
3. **Add `st.cache_data` decorators** to the Excel-loading functions used by dashboard pages — a low-effort change with an immediate, noticeable responsiveness improvement.
4. **Centralize path configuration** (`data/raw/`, `db/nifty100.db`, `output/`, `logs/`) into a single `config.py` or `.env`-driven settings module, removing the ~30+ duplicated hardcoded path strings currently scattered through the codebase.
5. **Add a thin `src/api/` FastAPI layer** if the Makefile's `api` target is meant to be real, or remove the target plus the `fastapi`/`uvicorn`/`starlette` dependencies if it's not — the current half-state (dependency installed, target defined, no implementation) is pure technical debt either way.
6. **Promote `CAGRCalculator` into the UI.** It's the most defensively-engineered piece of the analytics layer (explicit edge-case flags) and is currently invisible to end users.
7. **Add a model-evaluation step to the forecasting layer** — even a simple leave-one-year-out backtest reported alongside each forecast would materially improve the trustworthiness of the Revenue/Profit/EPS Forecasting pages.

---

*This document reflects the repository state at the time of audit. It should be re-verified against source after any significant refactor, particularly any change to `app.py`'s sidebar list, `db/schema.sql`, or the `run_pipeline.py` implementation status.*
