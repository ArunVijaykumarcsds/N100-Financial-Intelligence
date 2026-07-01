from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

import pandas as pd

from analytics.ratios import RatioEngine
from analytics.cashflow_kpis import CashFlowKPIs
from analytics.cagr_builder import get_5yr_cagr


def build_financial_ratios():

    pnl = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    bs = pd.read_excel(
        "data/raw/balancesheet.xlsx",
        header=1
    )

    cf = pd.read_excel(
        "data/raw/cashflow.xlsx",
        header=1
    )

    df = pnl.merge(
        bs,
        on=["company_id", "year"],
        how="left"
    )

    df = df.merge(
        cf,
        on=["company_id", "year"],
        how="left"
    )

    df["net_profit_margin_pct"] = df.apply(
        lambda x: RatioEngine.net_profit_margin(
            x["net_profit"],
            x["sales"]
        ),
        axis=1
    )

    df["operating_profit_margin_pct"] = df.apply(
        lambda x: RatioEngine.operating_profit_margin(
            x["operating_profit"],
            x["sales"]
        ),
        axis=1
    )

    df["return_on_equity_pct"] = df.apply(
        lambda x: RatioEngine.roe(
            x["net_profit"],
            x["equity_capital"],
            x["reserves"]
        ),
        axis=1
    )

    df["return_on_assets_pct"] = df.apply(
        lambda x: RatioEngine.roa(
            x["net_profit"],
            x["total_assets"]
        ),
        axis=1
    )

    df["debt_to_equity"] = df.apply(
        lambda x: RatioEngine.debt_to_equity(
            x["borrowings"],
            x["equity_capital"],
            x["reserves"]
        ),
        axis=1
    )

    df["interest_coverage"] = df.apply(
        lambda x: RatioEngine.interest_coverage(
            x["operating_profit"],
            x["other_income"],
            x["interest"]
        ),
        axis=1
    )

    df["asset_turnover"] = df.apply(
        lambda x: RatioEngine.asset_turnover(
            x["sales"],
            x["total_assets"]
        ),
        axis=1
    )

    df["free_cash_flow"] = df.apply(
        lambda x: CashFlowKPIs.free_cash_flow(
            x["operating_activity"],
            x["investing_activity"]
        ),
        axis=1
    )

    df["cfo_quality_score"] = df.apply(
        lambda x: CashFlowKPIs.cfo_quality_score(
            x["operating_activity"],
            x["net_profit"]
        ),
        axis=1
    )

    df["capex_intensity"] = df.apply(
        lambda x: CashFlowKPIs.capex_intensity(
            x["investing_activity"],
            x["sales"]
        ),
        axis=1
    )

    df["fcf_conversion"] = df.apply(
        lambda x: CashFlowKPIs.fcf_conversion(
            x["free_cash_flow"],
            x["operating_profit"]
        ),
        axis=1
    )

    # ==================================
    # Additional Sprint 2 KPI Columns
    # ==================================

    df["earnings_per_share"] = df["eps"]

    df["dividend_payout_ratio_pct"] = (
        df["dividend_payout"]
    )

    df["total_debt_cr"] = (
        df["borrowings"]
    )

    df["cash_from_operations_cr"] = (
        df["operating_activity"]
    )

    df["book_value_per_share"] = (
        (
            df["equity_capital"]
            +
            df["reserves"]
        )
        /
        df["equity_capital"]
    )

    df["composite_quality_score"] = (
        df["opm_percentage"].fillna(0) * 0.40
        +
        df["eps"].fillna(0) * 0.40
        +
        df["dividend_payout"].fillna(0) * 0.20
    )

    # ==================================
    # CAGR Metrics
    # ==================================

    df["revenue_cagr_5yr"] = None
    df["pat_cagr_5yr"] = None
    df["eps_cagr_5yr"] = None

    for company in df["company_id"].unique():

        company_df = (
            df[df["company_id"] == company]
            .sort_values("year")
        )

        revenue_cagr = get_5yr_cagr(
            company_df["sales"]
        )

        pat_cagr = get_5yr_cagr(
            company_df["net_profit"]
        )

        eps_cagr = get_5yr_cagr(
            company_df["eps"]
        )

        df.loc[
            df["company_id"] == company,
            "revenue_cagr_5yr"
        ] = revenue_cagr

        df.loc[
            df["company_id"] == company,
            "pat_cagr_5yr"
        ] = pat_cagr

        df.loc[
            df["company_id"] == company,
            "eps_cagr_5yr"
        ] = eps_cagr

        output_columns = [

        "company_id",
        "year",

        "net_profit_margin_pct",
        "operating_profit_margin_pct",

        "return_on_equity_pct",
        "return_on_assets_pct",

        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",

        "free_cash_flow",
        "cfo_quality_score",
        "capex_intensity",
        "fcf_conversion",

        "earnings_per_share",
        "book_value_per_share",
        "dividend_payout_ratio_pct",

        "total_debt_cr",
        "cash_from_operations_cr",

        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",

        "composite_quality_score"
    ]

    result = df[
        output_columns
    ]

    result.to_csv(
        "data/processed/financial_ratios.csv",
        index=False
    )

    return result


if __name__ == "__main__":

    result = build_financial_ratios()

    print(result.head())

    print(
        "\nRows:",
        len(result)
    )