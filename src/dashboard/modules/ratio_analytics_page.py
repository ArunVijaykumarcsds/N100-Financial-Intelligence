import plotly.express as px

from analytics.ratio_analytics import (
    RatioAnalytics
)


def get_ratio_dashboard():

    analytics = RatioAnalytics()

    summary = analytics.ratio_summary()

    top_roe = analytics.top_roe()

    lowest_debt = analytics.lowest_debt()

    coverage = analytics.highest_interest_coverage()

    return {
        "summary": summary,
        "top_roe": top_roe,
        "lowest_debt": lowest_debt,
        "coverage": coverage
    }