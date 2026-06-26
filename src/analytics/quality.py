import numpy as np


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