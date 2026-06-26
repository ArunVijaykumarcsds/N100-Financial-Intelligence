import numpy as np
import pandas as pd

def normalize(series):

    min_val = series.min()
    max_val = series.max()

    if min_val == max_val:
        return pd.Series([50] * len(series))

    return (
        (series - min_val)
        /
        (max_val - min_val)
    ) * 100


def quality_score(df):

    result = df.copy()

    result["opm_score"] = normalize(
        result["opm_percentage"].fillna(0)
    )

    result["eps_score"] = normalize(
        result["eps"].fillna(0)
    )

    result["dividend_score"] = normalize(
        result["dividend_payout"].fillna(0)
    )

    result["quality_score"] = (
        result["opm_score"] * 0.40
        +
        result["eps_score"] * 0.40
        +
        result["dividend_score"] * 0.20
    )

    return result


def top_quality_companies(df):

    df = quality_score(df)

    return (
        df.sort_values(
            "quality_score",
            ascending=False
        )
        .head(10)
    )


def bottom_quality_companies(df):

    df = quality_score(df)

    return (
        df.sort_values(
            "quality_score"
        )
        .head(10)
    )


def quality_summary(df):

    df = quality_score(df)

    return {
        "average_quality":
            round(
                df["quality_score"].mean(),
                2
            ),

        "highest_quality":
            round(
                df["quality_score"].max(),
                2
            ),

        "lowest_quality":
            round(
                df["quality_score"].min(),
                2
            ),

        "companies":
            len(df)
    }


def remove_extreme_growth(df):

    df = df.copy()

    df.loc[
        df["revenue_growth_pct"] > 1000,
        "revenue_growth_pct"
    ] = np.nan

    df.loc[
        df["profit_growth_pct"] > 1000,
        "profit_growth_pct"
    ] = np.nan

    return df