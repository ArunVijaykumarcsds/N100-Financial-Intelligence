import pandas as pd

from analytics.master_ranking import (
    get_master_ranking
)


def get_company_comparison(
    company1,
    company2
):

    df = get_master_ranking()

    comparison_df = df[
        df["company_id"].isin(
            [company1, company2]
        )
    ]

    return comparison_df[
        [
            "company_id",
            "revenue",
            "net_income",
            "eps",
            "financial_score",
            "quality_score",
            "valuation_score",
            "master_score",
            "rank"
        ]
    ]


def comparison_summary(
    company1,
    company2
):

    return get_company_comparison(
        company1,
        company2
    )