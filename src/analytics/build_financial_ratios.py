from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

import pandas as pd

from analytics.ratios import RatioEngine
from analytics.cashflow_kpis import CashFlowKPIs


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
        "fcf_conversion"
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