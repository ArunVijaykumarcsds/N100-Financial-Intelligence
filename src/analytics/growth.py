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