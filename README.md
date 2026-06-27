# N100 Financial Intelligence Platform

> A Python + Streamlit analytics platform that turns raw Nifty 100 financial statements into ratios, rankings, growth forecasts, and a multi-page investor dashboard.

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.58-FF4B4B.svg)](https://streamlit.io/)
[![Tests](https://img.shields.io/badge/tests-53%20passing-brightgreen.svg)](#running-tests)
[![License](https://img.shields.io/badge/license-Unspecified-lightgrey.svg)](#license)

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [Analytics Engines](#analytics-engines)
- [Machine Learning Components](#machine-learning-components)
- [Dashboard Modules](#dashboard-modules)
- [Database Overview](#database-overview)
- [Repository Structure](#repository-structure)
- [Installation Guide](#installation-guide)
- [Local Development Setup](#local-development-setup)
- [Running the ETL Pipeline](#running-the-etl-pipeline)
- [Running the Analytics Layer](#running-the-analytics-layer)
- [Running Streamlit](#running-streamlit)
- [Running Tests](#running-tests)
- [Known Issues & Technical Debt](#known-issues--technical-debt)
- [Screenshots](#screenshots)
- [Future Roadmap](#future-roadmap)
- [Contribution Guide](#contribution-guide)
- [License](#license)

---

## Executive Summary

**N100 Financial Intelligence** is a data analytics platform built around the **Nifty 100** (India's top 100 listed companies by market capitalization). It ingests raw financial statement data sourced from **Bluestock Fintech** — profit & loss, balance sheet, cash flow, sector classification, and stock price Excel exports — and turns it into:

- A validated **SQLite** database of company fundamentals
- A library of **financial ratio, cash-flow-quality, growth, valuation, and composite scoring engines**
- Three **linear-regression-based forecasting models** (Revenue, Profit, EPS)
- A **17-page Streamlit dashboard** for exploring company history, comparisons, rankings, sector breakdowns, and forward-looking "Future Winners" recommendations

This document is generated from a full, line-by-line audit of the repository as it currently exists. Every claim below was checked against source code, and the unit test suite (53 tests) was executed to confirm pass/fail status rather than assumed. Where a feature is described in code comments or naming but not actually wired up or implemented, that gap is called out explicitly rather than glossed over — see [Known Issues & Technical Debt](#known-issues--technical-debt).

---

## Project Overview

### The Problem

Retail investors and analysts who want to screen the Nifty 100 for fundamentally strong companies are usually stuck choosing between:

1. Manually downloading and reconciling financial statements company-by-company, or
2. Paying for a commercial terminal (Bloomberg, Capital IQ, Screener.in premium, etc.)

There's a gap for a **self-hosted, transparent, code-first** screening tool where every ratio and score is computed from a formula you can read in the source, not a black box.

### What This Platform Does

N100 Financial Intelligence loads twelve raw Excel exports covering Nifty 100 company fundamentals, normalizes and validates them, and computes a layered set of financial metrics:

| Layer | Output |
|---|---|
| **Ratios** | Net margin, operating margin, ROE, ROA, ROCE, debt/equity, interest coverage, asset turnover |
| **Cash Flow Quality** | Free cash flow, CFO quality classification, capex intensity, FCF conversion, capital allocation pattern |
| **Growth** | YoY revenue/profit growth, CAGR with edge-case flagging (zero base, turnaround, decline-to-loss) |
| **Composite Scoring** | A weighted "Financial Score," a "Quality Score," a "Valuation Score," and a "Master Score" that blends all three |
| **Forecasting** | Per-company linear regression forecasts for next-year Revenue, Net Profit, and EPS |
| **Rule-Based Recommendations** | "Future Winner" ranking and a Strong Buy / Buy / Hold / Avoid label generator |

### End-User Workflow

1. A user opens the Streamlit app and lands on the **Executive Command Center** (Home), seeing the top "Future Winner" and top "Growth" company at a glance.
2. They drill into **Company History** or **Company Snapshot** to see one company's multi-year trend.
3. They use **Company Comparison** to put two tickers side by side on the composite scores.
4. They browse **Master Ranking**, **Winner Dashboard**, **Sector Analytics**, or **Valuation Dashboard** to screen the universe.
5. They check **Revenue/Profit/EPS Forecasting** for a simple trend-line projection on a specific company.
6. They read the **AI Insights** or **Future Winners** page for a templated buy/hold/avoid recommendation.

### Value Proposition

- **Transparent**: every score is a documented, auditable formula in `src/analytics/`, not a proprietary black box.
- **Self-hosted**: runs entirely on local Excel files + SQLite; no external API dependency for the core analytics.
- **Composable**: each analytics engine is a small, independently testable Python module that can be reused outside the dashboard (e.g., in a notebook or batch job).

---

## Key Features

- ✅ **ETL pipeline** that loads Companies, Profit & Loss, and Balance Sheet data into SQLite with column normalization and duplicate/null validation utilities
- ✅ **Ratio Engine** covering 7 core profitability/leverage/efficiency ratios with documented edge-case handling (e.g., zero sales, negative equity)
- ✅ **Cash Flow KPI Engine** that classifies CFO quality ("High Quality" / "Moderate" / "Accrual Risk") and capital allocation behavior ("Reinvestor," "Distress Signal," "Cash Accumulator," etc.) from the sign pattern of CFO/CFI/CFF
- ✅ **CAGR Calculator** with explicit flags for non-standard cases (zero base, turnaround, both-negative, decline-to-loss) instead of silently returning misleading numbers
- ✅ **Composite scoring system** — Financial Score, Quality Score, Valuation Score → blended into a single Master Score and ranking table
- ✅ **Three linear regression forecasters** (Revenue, Profit, EPS) built on `scikit-learn`'s `LinearRegression`, fit per-company on historical year-over-year values
- ✅ **17 working Streamlit dashboard pages** spanning company drill-down, sector analytics, valuation screening, growth screening, and forecast visualization
- ✅ **53 passing unit tests** covering the normalization and KPI calculation layers
- ⚠️ **"AI Insights" page** — a rule-based recommendation generator (score thresholds → Strong Buy/Buy/Hold/Avoid label), not a trained machine learning or LLM-based system. See [Machine Learning Components](#machine-learning-components) for the accurate scope.

---

## Architecture Overview

The system is organized into four layers, all driven from flat Excel files rather than a live data feed:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES (data/raw/)                     │
│   12 Excel files from Bluestock Fintech — Nifty 100 dataset          │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          ETL LAYER (src/etl/)                        │
│  loader.py → normaliser.py → validator.py → load_*.py → SQLite       │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ANALYTICS LAYER (src/analytics/)                  │
│  Ratios · Cash Flow KPIs · CAGR · Growth · Quality · Valuation ·      │
│  Scoring Engine · Master Ranking · Forecasting · AI Insights          │
└───────────────────────────────┬───────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  DASHBOARD LAYER (src/dashboard/)                     │
│           Streamlit multi-page app — 17 reachable pages               │
└─────────────────────────────────────────────────────────────────────┘
```

**A note on the data path that matters in practice:** most of the analytics and dashboard modules read directly from `data/raw/profitandloss.xlsx` (via `pandas.read_excel`) rather than from the SQLite database. SQLite is populated and used by a smaller subset of modules (`top_companies.py`, `company_history.py`, the `Top Companies`/`Company History` dashboard pages, and `load_financial_ratios.py`). This is documented in detail in **`PROJECT_ARCHITECTURE.md`**, including which specific files use which data path.

For the full deep-dive — module dependency maps, exact data flow per dashboard page, scalability assessment, and a complete list of disconnected/dead code paths — see **[`PROJECT_ARCHITECTURE.md`](./PROJECT_ARCHITECTURE.md)**.

---

## Analytics Engines

All engines live under `src/analytics/`. Below is what each one actually does, verified against source.

### RatioEngine (`ratios.py`)

Static-method calculator for: net profit margin, operating profit margin, ROE, ROCE, ROA, debt-to-equity, interest coverage, asset turnover. Every method returns `None` on a divide-by-zero or invalid-input condition (e.g., zero sales, non-positive equity) instead of raising or returning `inf`/`NaN` silently. Covered by `tests/kpi/test_ratios.py` (7 tests).

### CAGRCalculator (`cagr.py`)

Computes compound annual growth rate between a start and end value over N years, but — unusually for a screener tool — it **returns an explicit status flag** alongside the number: `OK`, `ZERO_BASE`, `DECLINE_TO_LOSS`, `TURNAROUND`, `BOTH_NEGATIVE`, or `INVALID`. This prevents the common screener bug of reporting a meaningless CAGR when a company moved from profit to loss or vice versa. Covered by `tests/kpi/test_cagr.py` (5 tests).

### CashFlowKPIs (`cashflow_kpis.py`)

- `free_cash_flow` — CFO + CFI
- `cfo_quality_score` — classifies CFO/Net Profit ratio into High Quality (>1), Moderate (0.5–1), or Accrual Risk (<0.5)
- `capex_intensity` — classifies |CFI|/Sales into Asset Light (<3%), Moderate (3–8%), or Capital Intensive (>8%)
- `fcf_conversion` — FCF / Operating Profit, as a percentage
- `capital_allocation_pattern` — maps the sign combination of (CFO, CFI, CFF) to a human-readable label such as "Reinvestor," "Distress Signal," "Growth Funded By Debt," or "Cash Accumulator," using a fixed lookup table of the 7 sign combinations the code explicitly handles (the 8th combination falls through to "Unknown")

Covered by `tests/kpi/test_cashflow.py` (6 tests).

### Growth Engine (`growth.py`, `ranking.py`)

Computes year-over-year revenue and profit growth per company via `groupby().pct_change()`, replaces `inf` results with `NaN`, and builds a "growth score" (50% revenue growth + 50% profit growth) used for leaderboard ranking. `quality.py`'s `remove_extreme_growth()` is available to null out growth figures above 1000% (a guard against base-effect distortion) but **is not called from the main `growth.py` pipeline** — it's only invoked from `analytics_runner.py`, a standalone script not wired into the dashboard.

### Quality Engine (`quality.py`)

Normalizes Operating Margin, EPS, and Dividend Payout to a 0–100 scale and blends them (40% / 40% / 20%) into a single Quality Score, with leaderboard helpers for top/bottom 10. This score feeds into the Master Ranking engine.

### Financial Scoring Engine (`scoring_engine.py`)

Normalizes five inputs (Market Cap, Revenue, Net Income, Profit Margin, EPS) to 0–100 and combines them with fixed weights (20/25/25/15/15) into a "Financial Score." **Market Cap here is not the company's real market capitalization** — every caller of this engine substitutes `revenue * 10` as a market cap proxy. A real `market_cap.xlsx` file with `market_cap_crore` exists in `data/raw/` but is not read by any code path. See [Known Issues](#known-issues--technical-debt).

### Master Ranking Engine (`master_ranking.py`)

Combines Financial Score (40%), Quality Score (35%), and a Valuation Score (25%, derived as `100 / PE ratio`) into a single `master_score`, then ranks all companies by it. This is the backbone of the Master Ranking, Winner Dashboard, Company Comparison, and Future Winners pages.

### Valuation Analyzer (`valuation.py`)

Joins the latest close price (`stock_prices.xlsx`) with the latest EPS (`profitandloss.xlsx`) to compute a PE ratio, then buckets companies into Undervalued (PE < 15), Fairly Valued (15–30), or Overvalued (PE > 30) — fixed thresholds, not sector-adjusted.

### Sector Analytics (`sector_analytics.py`)

Reads `sectors.xlsx` directly (a file populated with real sector classification and index-weight data) and produces sector-level aggregates: company count, total/average index weight, and a market-cap-category crosstab. This is one of the few modules using a dedicated, purpose-built raw file rather than re-deriving from P&L data.

### Future Winners Engine (`future_winners.py`)

Blends the Master Score (60%) with a separate Growth Score from `growth_prediction.py` (40%) into a `future_winner_score`, then ranks. Powers both the **Future Winners** page and the **Executive Command Center** home page.

### AI Insights Engine (`ai_insights.py`)

Takes a company's `future_winner_score` from the Future Winners engine and maps it to a recommendation string via four fixed thresholds (≥80 Strong Buy, ≥60 Buy, ≥40 Hold, else Avoid), pairing each tier with a canned sentence template. **There is no machine learning, NLP, or generative model involved** — see [Machine Learning Components](#machine-learning-components) for why this matters to set expectations correctly.

### Capital Allocation Builder (`build_capital_allocation.py`)

Standalone script that applies `capital_allocation_pattern()` across the full cash flow dataset and writes `output/capital_allocation.csv`. Not currently surfaced in any dashboard page.

### Financial Health Analyzer (`financial_health.py`)

Computes Profit Margin, Operating Margin, Interest Coverage, and Earnings Quality (Net Profit / PBT), then derives a 0–4 point score from four boolean thresholds (Margin > 10%, Operating Margin > 15%, Interest Coverage > 3, Earnings Quality > 0.7) and buckets into Risky / Average / Healthy.

---

## Machine Learning Components

This section exists specifically to give an accurate, non-inflated picture of "ML" in this repository, since several module and page names (Health *Prediction*, Growth *Prediction*, AI *Insights*) could otherwise be read as implying trained models.

| Component | What it actually is | Library |
|---|---|---|
| `RevenueForecaster`, `ProfitForecaster`, `EPSForecaster` | **Genuine ML**: a separate `sklearn.linear_model.LinearRegression` fit per company, with `year_num` as the single feature and the target metric (Sales/Net Profit/EPS) as the label. Each requires ≥3 historical years to fit; returns `None` otherwise. | `scikit-learn` |
| `HealthPredictor` ("Health Prediction" page) | **Rule-based, not ML.** A fixed weighted sum (Revenue×0.4 + Profit×0.4 + EPS×0.2) compared against three hardcoded thresholds (5000 / 2000 / 500) to output Excellent/Good/Average/Weak. No model is trained or fit. | None |
| `GrowthPredictor` ("Growth Prediction" page) | **Rule-based, not ML.** A weighted formula (Revenue Growth×0.4 + Profit Growth×0.4 + EPS Growth×0.2) computed directly from the latest two fiscal years, no fitting or learning step. | None |
| `AIInsights` ("AI Insights" page) | **Rule-based, not ML/AI** in the generative or predictive-modeling sense. Four score thresholds mapped to a recommendation label and a canned text template. | None |

**Forecasting model limitations (genuinely ML-based ones):**
- Single-feature linear regression on a year index — no seasonality, no macro factors, no sector context, no confidence intervals.
- Requires at least 3 historical data points per company or returns `None`; companies with sparse history (recent IPOs, irregular reporting years) are silently excluded from forecasts.
- No train/test split, cross-validation, or accuracy metric (R², MAE, etc.) is computed or surfaced anywhere in the code or dashboard — there is currently no way to know how good these forecasts are without external validation.
- `scikit-learn` is imported in three files but **is missing from `requirements.txt`** — a clean `pip install -r requirements.txt` will not provide it. See [Installation Guide](#installation-guide).

---

## Dashboard Modules

The Streamlit app (`src/dashboard/app.py`) is a single-file sidebar-router with one `modules/*_page.py` file per feature. Of the pages defined in code, here is the **actual reachability status** as run through the live sidebar `selectbox`:

| Page | Reachable from sidebar? | Backing Module |
|---|---|---|
| Home (Executive Command Center) | ✅ Yes | `executive_command_center_page.py` |
| Top Companies | ✅ Yes | `top_companies_page.py` |
| Company History | ✅ Yes | `company_history_page.py` |
| Company Comparison | ✅ Yes | `company_compare_page.py` |
| Financial Health | ✅ Yes | `financial_health_page.py` |
| Company Snapshot | ✅ Yes | `company_snapshot_page.py` |
| Winner Dashboard | ✅ Yes | `winner_dashboard_page.py` |
| Sector Analytics | ✅ Yes | `sector_analytics_page.py` |
| Valuation Dashboard | ✅ Yes | `valuation_dashboard_page.py` |
| Growth Dashboard | ✅ Yes | `growth_dashboard_page.py` |
| Master Ranking | ✅ Yes | `master_ranking_dashboard_page.py` |
| Revenue Forecasting | ✅ Yes | `revenue_forecasting_page.py` |
| Profit Forecasting | ✅ Yes | `profit_forecasting_page.py` |
| EPS Forecasting | ✅ Yes | `eps_forecasting_page.py` |
| Health Prediction | ✅ Yes | `health_prediction_page.py` |
| Growth Prediction | ✅ Yes | `growth_prediction_page.py` |
| Future Winners | ✅ Yes | `future_winners_page.py` |
| AI Insights | ✅ Yes | `ai_insights_page.py` |
| **Ratio Analytics** | ❌ **No** — handling code exists (`elif page == "Ratio Analytics":`) and is imported, but no matching option exists in the sidebar `st.selectbox` list, so the branch is dead code in the running app | `ratio_analytics_page.py` |
| **Quality Dashboard** | ❌ **No** — module exists and is self-contained, but is never imported into `app.py` and has no sidebar entry or branch at all | `quality_dashboard_page.py` |

**17 of 19 implemented pages are reachable in the running app.** The README's installation/usage instructions below describe the 17 working pages; the two disconnected pages are flagged here and in `PROJECT_ARCHITECTURE.md` as a one-line fix (add the missing `selectbox` entries) rather than a missing feature.

A brief description of each reachable page:

- **Home / Executive Command Center** — Top Future Winner, top Growth company, two leaderboards, two bar charts, and a generated "AI Recommendation Feed" for the top 10 Future Winners.
- **Top Companies** — Top 10 by ROE, queried directly from the SQLite `companies` table.
- **Company History** — Per-company Revenue/Net Profit/EPS line charts, sourced from SQLite `profit_loss`.
- **Company Comparison** — Side-by-side Master Score breakdown for two selected companies, sourced from `master_ranking.py`.
- **Financial Health** — Full-universe Risky/Average/Healthy counts and table from `financial_health.py`.
- **Company Snapshot** — Single-company latest-year health score, growth %, and margin metrics.
- **Winner Dashboard** — Leaderboard, top 10, and bottom 10 by Financial Score with bar charts.
- **Sector Analytics** — Sector summary, weight leaderboard, and market-cap-category crosstab from `sectors.xlsx`.
- **Valuation Dashboard** — PE-ratio-based Undervalued/Overvalued screens with bar charts.
- **Growth Dashboard** — Top/bottom growth companies by blended growth score.
- **Master Ranking** — Top 20 leaderboard by `master_score` with component score breakdown.
- **Revenue / Profit / EPS Forecasting** (3 pages) — Per-company `LinearRegression` forecast for the next fiscal year, plotted against historical trend.
- **Health Prediction** — Single-company Excellent/Good/Average/Weak rule-based classification.
- **Growth Prediction** — Full-universe growth-score ranking table and top-20 bar chart.
- **Future Winners** — Blended Master Score + Growth Score ranking, the platform's flagship screen.
- **AI Insights** — Single-company Strong Buy/Buy/Hold/Avoid templated recommendation.

---

## Database Overview

**Engine:** SQLite, file at `db/nifty100.db` (gitignored — generated locally, not shipped in the repo).

**Schema-defined tables** (`db/schema.sql`):

```sql
companies (
    id TEXT PRIMARY KEY,
    company_name TEXT,
    website TEXT,
    face_value REAL,
    book_value REAL,
    roce_percentage REAL,
    roe_percentage REAL
)

profit_loss (
    id INTEGER PRIMARY KEY,
    company_id TEXT REFERENCES companies(id),
    year TEXT,
    sales REAL, expenses REAL, operating_profit REAL, opm_percentage REAL,
    other_income REAL, interest REAL, depreciation REAL,
    profit_before_tax REAL, tax_percentage REAL, net_profit REAL,
    eps REAL, dividend_payout REAL
)

balance_sheet (
    id INTEGER PRIMARY KEY,
    company_id TEXT REFERENCES companies(id),
    year TEXT,
    equity_capital REAL, reserves REAL, borrowings REAL,
    other_liabilities REAL, total_liabilities REAL,
    fixed_assets REAL, cwip REAL, investments REAL,
    other_asset REAL, total_assets REAL
)
```

**One additional table exists but is not in `schema.sql`:** `financial_ratios`, created dynamically by `pandas.DataFrame.to_sql(..., if_exists="replace")` inside `src/analytics/load_financial_ratios.py`. It is only created if that script is run manually — it is **not** part of `run_pipeline.py` (which is empty) or the `Makefile`'s `pipeline` target.

**Foreign keys are declared but not enforced** — SQLite does not enforce `FOREIGN KEY` constraints unless `PRAGMA foreign_keys = ON` is set per-connection, and no ETL or analytics code in this repository sets that pragma. In practice this matters: 8 company IDs present in `profitandloss.xlsx` (`ULTRACEMCO`, `UNIONBANK`, `UNITDSPR`, `VBL`, `VEDL`, `WIPRO`, `ZOMATO`, `ZYDUSLIFE`) have no corresponding row in `companies.xlsx`, so any inner join against `companies` will silently drop their P&L history.

**Most analytics and dashboard code bypasses the database entirely**, reading `data/raw/profitandloss.xlsx` directly with `pandas.read_excel(..., header=1)` instead. Only `top_companies.py`, `company_history.py`, their dashboard equivalents, and `load_financial_ratios.py` actually touch SQLite. See `PROJECT_ARCHITECTURE.md` → Database Layer Architecture for the full file-by-file breakdown.

---

## Repository Structure

```
N100-Financial-Intelligence-main/
├── Makefile                       # load / validate / pipeline / test / dashboard / api targets
├── README.md                      # (this file, regenerated)
├── requirements.txt                # UTF-16 encoded; ~150 pinned packages (scikit-learn missing)
├── db/
│   └── schema.sql                 # companies / profit_loss / balance_sheet DDL
├── data/
│   ├── raw/                       # 12 source Excel files (Bluestock Fintech Nifty 100 export)
│   │   ├── companies.xlsx          # 92 companies
│   │   ├── profitandloss.xlsx      # 1,263 rows, 100 unique company_ids
│   │   ├── balancesheet.xlsx       # 1,312 rows
│   │   ├── cashflow.xlsx           # 1,187 rows
│   │   ├── sectors.xlsx            # 92 rows, 10 broad sectors
│   │   ├── stock_prices.xlsx       # 5,520 rows, 2020–2024 daily-ish OHLC
│   │   ├── financial_ratios.xlsx   # 1,184 rows — pre-computed ratios (separate from the CSV the code generates)
│   │   ├── market_cap.xlsx         # 552 rows — UNUSED by any code path
│   │   ├── analysis.xlsx           # 20 rows  — UNUSED
│   │   ├── documents.xlsx          # 1,585 rows — UNUSED
│   │   ├── peer_groups.xlsx        # UNUSED
│   │   └── prosandcons.xlsx        # 16 rows — UNUSED
│   └── processed/
│       └── financial_ratios.csv   # output of build_financial_ratios.py (1,370 rows)
├── src/
│   ├── etl/                       # loader, normaliser, validator, db_utils, load_*.py, create_db.py
│   ├── analytics/                 # 28 active modules — ratios, growth, scoring, forecasting, AI insights
│   └── dashboard/
│       ├── app.py                 # Streamlit sidebar router
│       └── modules/                # 20 page files (17 wired, 2 orphaned, 1 empty stray file)
└── tests/
    ├── etl/                       # test_normaliser.py (35 tests); test_loader.py & test_validator.py are empty
    └── kpi/                       # test_cagr.py, test_cashflow.py, test_ratios.py (18 tests)
```

---

## Installation Guide

### Prerequisites

- Python 3.10+ (developed/tested against 3.12)
- pip
- ~50 MB free disk space for the SQLite DB and processed CSVs

### Step 1 — Clone and enter the repository

```bash
git clone <repository-url>
cd N100-Financial-Intelligence-main
```

### Step 2 — Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### Step 3 — Install dependencies

`requirements.txt` is UTF-16 encoded (a known quirk of this repo — most likely from being saved by an editor with a non-default encoding). Most tooling on Linux/macOS handles this transparently via `pip`, but if you hit a decode error, convert it first:

```bash
# Optional: only needed if pip raises an encoding error reading the file
iconv -f UTF-16 -t UTF-8 requirements.txt -o requirements_utf8.txt
pip install -r requirements_utf8.txt
```

Otherwise, install directly:

```bash
pip install -r requirements.txt
```

**Important — `scikit-learn` is required but not pinned in `requirements.txt`.** The three forecasting modules (`revenue_forecasting.py`, `profit_forecasting.py`, `eps_forecasting.py`) import `sklearn.linear_model.LinearRegression` directly. Install it explicitly:

```bash
pip install scikit-learn
```

Without this step, the Revenue/Profit/EPS Forecasting dashboard pages will raise `ModuleNotFoundError` on load.

### Step 4 — Create the runtime directories

`output/` and `logs/` are referenced by several scripts but are `.gitignore`d and not present in a fresh clone:

```bash
mkdir -p output logs
```

---

## Local Development Setup

All commands below assume you are in the **repository root** (the directory containing `Makefile`). Several scripts use relative paths like `"data/raw/companies.xlsx"` and `"db/nifty100.db"`, so running them from inside `src/etl/` or `src/analytics/` directly will fail with `FileNotFoundError` — this was confirmed by execution during this audit, not just by reading the code.

### Build the database

```bash
python src/etl/create_db.py        # creates db/nifty100.db from db/schema.sql
python src/etl/load_companies.py   # loads data/raw/companies.xlsx → companies table
python src/etl/load_profit_loss.py # loads data/raw/profitandloss.xlsx → profit_loss table
python src/etl/load_balance_sheet.py # loads data/raw/balancesheet.xlsx → balance_sheet table
```

This was executed during the audit of this repository and confirmed working: `92 companies loaded.` from a clean database.

To reset and reload from scratch:

```bash
python src/etl/reset_db.py
```

### Verify the load

```bash
python src/etl/check_db.py             # lists tables
python src/etl/check_companies.py      # row count
python src/etl/check_profit_loss.py    # row count
python src/etl/check_balance_sheet.py  # row count
```

---

## Running the ETL Pipeline

**There is currently no single command that runs the full pipeline.** `src/etl/run_pipeline.py` exists as a file but is empty (0 bytes), and the Makefile's `pipeline` target (`python src/etl/run_pipeline.py`) will execute successfully but do nothing.

Until that script is implemented, run the load steps individually as shown above, in this order:

```bash
python src/etl/create_db.py
python src/etl/load_companies.py
python src/etl/load_profit_loss.py
python src/etl/load_balance_sheet.py
python src/analytics/load_financial_ratios.py   # optional: also loads financial_ratios into SQLite
```

See `PROJECT_ARCHITECTURE.md` for a suggested implementation of `run_pipeline.py` that chains these steps.

---

## Running the Analytics Layer

Most analytics modules are designed to be imported as libraries (by the dashboard or your own scripts), but several have a runnable `if __name__ == "__main__":` block for standalone use:

```bash
python src/analytics/build_financial_ratios.py     # writes data/processed/financial_ratios.csv
python src/analytics/build_capital_allocation.py    # writes output/capital_allocation.csv
python src/analytics/build_ratio_edge_cases.py       # writes logs/ratio_edge_cases.log (runs at import time, no __main__ guard)
```

`build_financial_ratios.py` must be run **before** `load_financial_ratios.py`, since the latter reads the CSV the former produces.

Three modules run their entire body at **import time** rather than behind a `__main__` guard (`build_ratio_edge_cases.py`, `top_companies.py`, `company_history.py`), so simply importing them (e.g., from a test or another script) triggers file I/O and `print()` output as a side effect. This is flagged as technical debt in `PROJECT_ARCHITECTURE.md`.

---

## Running Streamlit

```bash
streamlit run src/dashboard/app.py
```

or, equivalently, via the Makefile:

```bash
make dashboard
```

The app will open in your browser (default `http://localhost:8501`). Use the **Navigation** sidebar dropdown to switch between the 17 reachable pages listed in [Dashboard Modules](#dashboard-modules).

> **Note:** the dashboard reads most of its data live from `data/raw/profitandloss.xlsx` and related Excel files on every page load — it does not require the SQLite database to be built first, **except** for the "Top Companies" and "Company History" pages, which query `db/nifty100.db` directly and will error if it hasn't been created and loaded per the steps above.

> **Note on the `api` Makefile target:** `make api` runs `uvicorn src.api.main:app --reload`, but **no `src/api/` directory exists in this repository.** This target is currently non-functional; FastAPI and uvicorn are installed as dependencies but unused by any working code path.

---

## Running Tests

```bash
pytest tests/
```

This was executed during the audit and produced:

```
53 passed in 0.75s
```

All 53 tests pass cleanly from the repository root. Coverage breakdown:

| File | Tests | Covers |
|---|---|---|
| `tests/etl/test_normaliser.py` | 35 | `normalize_ticker`, `normalize_year` |
| `tests/kpi/test_ratios.py` | 7 | `RatioEngine` |
| `tests/kpi/test_cashflow.py` | 6 | `CashFlowKPIs` |
| `tests/kpi/test_cagr.py` | 5 | `CAGRCalculator` |
| `tests/etl/test_loader.py` | 0 | **Empty file — no tests implemented** |
| `tests/etl/test_validator.py` | 0 | **Empty file — no tests implemented** |

There is currently no test coverage for: `loader.py`'s `load_excel()`, any of `validator.py`'s functions, any dashboard page module, the database load scripts, or any of the scoring/ranking/forecasting engines beyond CAGR/ratios/cash-flow KPIs.

To run with coverage reporting (pytest-cov is already a pinned dependency):

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Known Issues & Technical Debt

This section is intentionally blunt — it exists so a new contributor doesn't have to rediscover these the hard way.

**Broken or non-functional**
- `src/etl/run_pipeline.py` is empty; the Makefile's `pipeline` target does nothing.
- `make api` points at `src/api/main:app`, which doesn't exist.
- `src/analytics/scoring.py` is empty (0 bytes) — likely a placeholder for logic that ended up in `scoring_engine.py`.
- `src/analytics/build_financial_ratios.pybuild_financial_ratios.py` is an empty, malformed-filename stray file (looks like a copy/rename artifact) and should be deleted.
- `src/dashboard/modules/master_ranking.py` is empty, distinct from the working `master_ranking_dashboard_page.py` — likely a leftover from a rename.
- `tests/etl/test_loader.py` and `tests/etl/test_validator.py` are empty despite corresponding implementation files existing.

**Wired incorrectly (silent, not crashing)**
- **Ratio Analytics** page: imported and has a full `elif` branch in `app.py`, but is missing from the sidebar `selectbox` list — unreachable in the running app.
- **Quality Dashboard** page: fully implemented module, but never imported or referenced in `app.py` at all.
- The sidebar `selectbox` list contains `"Home"` twice (lines list it both first and last).
- `analytics_runner.py` uses bare imports (`from profitability import ...`) inconsistent with the `sys.path.append` + `analytics.` prefix pattern used everywhere else — it only runs correctly if executed from inside `src/analytics/`, unlike its siblings.

**Data quality**
- `market_cap = revenue * 10` is used as a market cap proxy across `master_ranking.py`, `winner_dashboard_page.py`, and the scoring engine's expected input, despite a real `market_cap.xlsx` (552 rows, real `market_cap_crore` figures) sitting unused in `data/raw/`.
- 4 of 12 raw Excel files are not read by any code: `analysis.xlsx`, `documents.xlsx`, `peer_groups.xlsx`, `prosandcons.xlsx`.
- 8 company IDs appear in `profitandloss.xlsx` with no matching row in `companies.xlsx` (`ULTRACEMCO`, `UNIONBANK`, `UNITDSPR`, `VBL`, `VEDL`, `WIPRO`, `ZOMATO`, `ZYDUSLIFE`) — any company-table join silently drops their history.
- `data/processed/financial_ratios.csv` contains at least one exact duplicate composite key (`ABB`, `Mar 2014` appears twice with differing computed values), suggesting a join fan-out somewhere in `build_financial_ratios.py`'s merge step.
- `data/raw/financial_ratios.xlsx` (a pre-supplied raw file with 1,184 rows) and `data/processed/financial_ratios.csv` (the platform's own computed output, 1,370 rows) have overlapping but not identical column sets and are read by different modules (`ratio_analytics.py` vs. `load_financial_ratios.py`) — there is no single source of truth for "financial ratios" in the current architecture.

**Code quality / consistency**
- SQL queries built with f-string interpolation of `company_id` appear in `company_history.py` and `company_history_page.py`. Current risk is low (values come from a `selectbox` populated from the DB itself, not free user text), but this is not parameterized and should not be treated as a safe pattern to extend.
- Several scripts execute all of their logic at module import time with no `__main__` guard (`top_companies.py`, `company_history.py`, `build_ratio_edge_cases.py`, the latter half of `validator.py` and `balance_validator.py`), so importing them as a module has side effects (file writes, stdout output, network-free DB reads).
- The three forecasting classes (`RevenueForecaster`, `ProfitForecaster`, `EPSForecaster`) duplicate an almost identical `clean_data()` method and constructor — a strong candidate for a shared base class.
- `build_capital_allocation.py` has a duplicated import block (`import pandas as pd` and the `CashFlowKPIs` import each appear twice).
- `revenue_forecasting.py`'s `predict_company_revenue()` method fits the same `LinearRegression` model twice in a row (duplicated code block, harmless but wasteful).

None of the above prevents the platform from running for its core, reachable feature set — they are documented here so they can be triaged deliberately rather than discovered by accident.

---

## Screenshots

> Screenshots are not included in this repository as of this audit. Suggested placeholders for a future update:

- `docs/screenshots/executive-command-center.png`
- `docs/screenshots/master-ranking.png`
- `docs/screenshots/company-comparison.png`
- `docs/screenshots/revenue-forecasting.png`
- `docs/screenshots/sector-analytics.png`

---

## Future Roadmap

Based on the gaps identified during this audit, in rough priority order:

1. **Wire up `run_pipeline.py`** to chain `create_db.py` → `load_companies.py` → `load_profit_loss.py` → `load_balance_sheet.py` → `build_financial_ratios.py` → `load_financial_ratios.py`, so `make pipeline` does what it claims to.
2. **Reconnect the two orphaned dashboard pages** (Ratio Analytics, Quality Dashboard) — a one-line fix to the sidebar list and, for Quality Dashboard, one new import and `elif` branch in `app.py`.
3. **Replace the `revenue * 10` market cap proxy** with the real `market_cap.xlsx` data, which already exists in the repository.
4. **Reconcile the company universe** — resolve the 8 P&L-only company IDs missing from `companies.xlsx`, and decide whether the platform is a "Nifty 100" (100 companies) or "92-company" universe.
5. **Pin `scikit-learn`** in `requirements.txt` and add a smoke test that imports all three forecaster classes.
6. **Add test coverage** for `loader.py`, `validator.py`, the scoring/ranking engines, and at least one dashboard page (e.g., via Streamlit's `AppTest` framework).
7. **Either build out `src/api/`** to match the Makefile's `api` target, or remove the target and the FastAPI/uvicorn dependencies if no API is planned.
8. **Surface forecast accuracy** — add a holdout-based R² or MAE metric to the three forecasting dashboards so users can gauge reliability.
9. **Investigate and deduplicate** the `financial_ratios.csv` composite-key duplicates.
10. **Consolidate the two parallel "financial ratios" data sources** (`data/raw/financial_ratios.xlsx` vs. the platform-generated `data/processed/financial_ratios.csv`) into one canonical pipeline output.

---

## Contribution Guide

This repository does not currently include a `CONTRIBUTING.md`, issue templates, or a CI workflow. Until those are added, a reasonable working process:

1. Fork and branch from `main`.
2. Run `pytest tests/` before and after your change — all 53 existing tests must continue to pass.
3. If you add a new analytics engine or KPI calculation, add corresponding unit tests under `tests/kpi/` or `tests/etl/` following the existing style (plain `assert`-based `pytest` functions, no fixtures framework currently in use).
4. If you touch `src/dashboard/app.py`, manually verify the page is both **imported** and **present in the sidebar `selectbox` list** — this repository currently has two examples of pages that are one or the other but not both.
5. Run `flake8` and `black` before submitting — both are already pinned in `requirements.txt`, though no CI currently enforces them.

---

## License

No `LICENSE` file is present in this repository at the time of this audit. Until one is added, treat the code as **all rights reserved** by default and confirm usage terms with the repository owner before reuse or redistribution.