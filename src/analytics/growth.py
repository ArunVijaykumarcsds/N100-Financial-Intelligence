import numpy as np
import pandas as pd


def calculate_revenue_growth(df):

    df = df.copy()

    df["revenue_growth_pct"] = (
        df.groupby("company_id")["sales"]
        .pct_change()
        * 100
    )

    df["revenue_growth_pct"] = (
        df["revenue_growth_pct"]
        .replace([np.inf, -np.inf], np.nan)
    )

    return df


def calculate_profit_growth(df):

    df = df.copy()

    df["profit_growth_pct"] = (
        df.groupby("company_id")["net_profit"]
        .pct_change()
        * 100
    )

    df["profit_growth_pct"] = (
        df["profit_growth_pct"]
        .replace([np.inf, -np.inf], np.nan)
    )

    return df


def load_growth_data():

    df = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    df = calculate_revenue_growth(df)

    df = calculate_profit_growth(df)

    return df


def growth_leaderboard():

    df = load_growth_data()

    latest = (
        df[df["year"] == "TTM"]
        .copy()
    )

    latest["growth_score"] = (
        latest["revenue_growth_pct"].fillna(0) * 0.5
        +
        latest["profit_growth_pct"].fillna(0) * 0.5
    )

    latest = latest.sort_values(
        "growth_score",
        ascending=False
    )

    return latest


def growth_summary():

    df = growth_leaderboard()

    return {
        "average_growth":
            round(df["growth_score"].mean(), 2),

        "highest_growth":
            round(df["growth_score"].max(), 2),

        "lowest_growth":
            round(df["growth_score"].min(), 2),

        "companies":
            len(df)
    }


def top_growth_companies():

    return growth_leaderboard().head(10)


def bottom_growth_companies():

    return growth_leaderboard().tail(10)