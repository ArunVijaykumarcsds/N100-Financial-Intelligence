import pandas as pd


def load_sector_data():

    return pd.read_excel(
        "data/raw/sectors.xlsx"
    )


def sector_summary():

    df = load_sector_data()

    return (
        df.groupby("broad_sector")
        .agg(
            companies=("company_id", "count"),
            total_weight=("index_weight_pct", "sum"),
            avg_weight=("index_weight_pct", "mean")
        )
        .reset_index()
        .sort_values(
            "total_weight",
            ascending=False
        )
    )


def sector_leaderboard():

    df = load_sector_data()

    return (
        df.groupby("broad_sector")
        ["index_weight_pct"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "index_weight_pct":
                "sector_weight"
            }
        )
        .sort_values(
            "sector_weight",
            ascending=False
        )
    )


def top_sector():

    leaderboard = sector_leaderboard()

    return leaderboard.iloc[0]


def bottom_sector():

    leaderboard = sector_leaderboard()

    return leaderboard.iloc[-1]


def market_cap_distribution():

    df = load_sector_data()

    return pd.crosstab(
        df["broad_sector"],
        df["market_cap_category"]
    )