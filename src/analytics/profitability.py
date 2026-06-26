import pandas as pd


def operating_margin(row):
    if row["sales"] == 0:
        return 0

    return (
        row["operating_profit"]
        / row["sales"]
    ) * 100


def net_profit_margin(row):
    if row["sales"] == 0:
        return 0

    return (
        row["net_profit"]
        / row["sales"]
    ) * 100


def add_profitability_metrics(df):

    df["calculated_opm"] = (
        df.apply(
            operating_margin,
            axis=1
        )
    )

    df["net_profit_margin"] = (
        df.apply(
            net_profit_margin,
            axis=1
        )
    )

    return df