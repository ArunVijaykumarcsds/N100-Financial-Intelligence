import pandas as pd
import numpy as np


class FinancialHealthAnalyzer:

    def calculate_metrics(self, df):

        result = df.copy()

        # Profit Margin
        result["profit_margin_pct"] = np.where(
            result["sales"] > 0,
            (result["net_profit"] / result["sales"]) * 100,
            0
        )

        # Operating Margin
        result["operating_margin_pct"] = np.where(
            result["sales"] > 0,
            (result["operating_profit"] / result["sales"]) * 100,
            0
        )

        # Interest Coverage
        result["interest_coverage"] = np.where(
            result["interest"] > 0,
            result["operating_profit"] / result["interest"],
            np.nan
        )

        # Earnings Quality
        result["earnings_quality"] = np.where(
            result["profit_before_tax"] > 0,
            result["net_profit"] / result["profit_before_tax"],
            np.nan
        )

        return result

    def assign_health_rating(self, df):

        result = df.copy()

        score = (
            (result["profit_margin_pct"] > 10).astype(int) +
            (result["operating_margin_pct"] > 15).astype(int) +
            (result["interest_coverage"] > 3).astype(int) +
            (result["earnings_quality"] > 0.7).astype(int)
        )

        result["financial_health_score"] = score

        result["financial_health_rating"] = pd.cut(
            score,
            bins=[-1, 1, 3, 4],
            labels=[
                "Risky",
                "Average",
                "Healthy"
            ]
        )

        return result