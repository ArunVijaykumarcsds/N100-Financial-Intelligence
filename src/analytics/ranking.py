import pandas as pd


def top_revenue_growth(df, top_n=10):

    return (
        df.sort_values(
            "revenue_growth_pct",
            ascending=False
        )
        [
            [
                "company_id",
                "year",
                "revenue_growth_pct"
            ]
        ]
        .head(top_n)
    )


def top_profit_growth(df, top_n=10):

    return (
        df.sort_values(
            "profit_growth_pct",
            ascending=False
        )
        [
            [
                "company_id",
                "year",
                "profit_growth_pct"
            ]
        ]
        .head(top_n)
    )