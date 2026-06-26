from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

import pandas as pd

from analytics.scoring_engine import (
    FinancialScoringEngine
)

from analytics.quality import (
    quality_score
)

from analytics.valuation import (
    ValuationAnalyzer
)


def get_master_ranking():

    df = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    latest_df = (
        df.sort_values("year")
        .groupby("company_id")
        .tail(1)
        .copy()
    )

    # ==========================
    # Quality Score FIRST
    # ==========================

    latest_df = quality_score(
        latest_df
    )

    # ==========================
    # Financial Score
    # ==========================

    latest_df = latest_df.rename(
        columns={
            "sales": "revenue",
            "net_profit": "net_income",
            "opm_percentage": "profit_margin"
        }
    )

    latest_df["market_cap"] = (
        latest_df["revenue"] * 10
    )

    engine = FinancialScoringEngine()

    latest_df = engine.calculate_scores(
        latest_df
    )

    # ==========================
    # Valuation Score
    # ==========================

    valuation = ValuationAnalyzer()

    valuation_df = (
        valuation.calculate_pe_ratios()
    )

    valuation_df["valuation_score"] = (
        100 /
        valuation_df["pe_ratio"]
    )

    latest_df = latest_df.merge(
        valuation_df[
            [
                "company_id",
                "valuation_score"
            ]
        ],
        on="company_id",
        how="left"
    )

    latest_df["valuation_score"] = (
        latest_df["valuation_score"]
        .fillna(0)
    )

    # ==========================
    # Master Score
    # ==========================

    latest_df["master_score"] = (
        latest_df["financial_score"] * 0.40
        +
        latest_df["quality_score"] * 0.35
        +
        latest_df["valuation_score"] * 0.25
    )

    latest_df = (
        latest_df.sort_values(
            "master_score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    latest_df["rank"] = (
        latest_df.index + 1
    )

    return latest_df