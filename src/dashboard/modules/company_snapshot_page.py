from pathlib import Path
import sys
import pandas as pd

sys.path.append(
    str(Path(__file__).resolve().parents[2])
)

from analytics.analytics_report import (
    AnalyticsReport
)

from analytics.financial_health import (
    FinancialHealthAnalyzer
)

from analytics.growth import (
    calculate_revenue_growth,
    calculate_profit_growth
)


def get_company_snapshot(company_id):

    df = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    analyzer = FinancialHealthAnalyzer()

    df = analyzer.calculate_metrics(df)

    df = analyzer.assign_health_rating(df)

    df = calculate_revenue_growth(df)

    df = calculate_profit_growth(df)

    report = AnalyticsReport()

    return report.company_snapshot(
        df,
        company_id
    )