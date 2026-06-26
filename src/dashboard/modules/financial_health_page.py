import pandas as pd
from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from analytics.financial_health import (
    FinancialHealthAnalyzer
)


def get_financial_health():

    df = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    analyzer = FinancialHealthAnalyzer()

    df = analyzer.calculate_metrics(df)

    df = analyzer.assign_health_rating(df)

    return df[
        [
            "company_id",
            "year",
            "financial_health_score",
            "financial_health_rating",
            "profit_margin_pct",
            "operating_margin_pct",
            "interest_coverage"
        ]
    ]


def get_company_health(company_id):

    df = get_financial_health()

    company = (
        df[df["company_id"] == company_id]
        .sort_values("year")
        .tail(1)
    )

    return company