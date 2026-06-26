import pandas as pd

from profitability import (
    add_profitability_metrics
)

from growth import (
    calculate_revenue_growth,
    calculate_profit_growth
)

from ranking import (
    top_revenue_growth,
    top_profit_growth
)

from financial_health import (
    FinancialHealthAnalyzer
)

from quality import remove_extreme_growth


# Load data first
df = pd.read_excel(
    "data/raw/profitandloss.xlsx",
    header=1
)

# Analytics pipeline
df = add_profitability_metrics(df)

df = calculate_revenue_growth(df)

df = calculate_profit_growth(df)

df = remove_extreme_growth(df)

health = FinancialHealthAnalyzer()

df = health.calculate_metrics(df)

df = health.assign_health_rating(df)

# Display results
print(
    df[
        [
            "company_id",
            "year",
            "profit_margin_pct",
            "operating_margin_pct",
            "interest_coverage",
            "earnings_quality",
            "financial_health_score",
            "financial_health_rating"
        ]
    ].head(15)
)