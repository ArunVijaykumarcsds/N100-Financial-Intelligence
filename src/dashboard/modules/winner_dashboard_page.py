import pandas as pd
from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from analytics.scoring_engine import (
    FinancialScoringEngine
)

from analytics.winner_analytics import (
    WinnerAnalytics
)


def get_winner_dashboard():

    df = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    latest_df = (
        df.sort_values("year")
        .groupby("company_id")
        .tail(1)
    )

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

    scored_df = engine.calculate_scores(
        latest_df
    )

    analytics = WinnerAnalytics(
        scored_df
    )

    return {
        "leaderboard":
            analytics.leaderboard(20),
        "top_winners":
            analytics.top_winners(10),
        "bottom_companies":
            analytics.bottom_companies(10),
        "summary":
            analytics.score_summary()
    }