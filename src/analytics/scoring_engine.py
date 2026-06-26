import pandas as pd


class FinancialScoringEngine:
    """
    Generates a composite financial score (0-100)
    for each company based on multiple metrics.
    """

    def __init__(self):
        self.weights = {
            "market_cap": 0.20,
            "revenue": 0.25,
            "net_income": 0.25,
            "profit_margin": 0.15,
            "eps": 0.15
        }

    def normalize(self, series):
        min_val = series.min()
        max_val = series.max()

        if max_val == min_val:
            return pd.Series([50] * len(series))

        return ((series - min_val) / (max_val - min_val)) * 100

    def calculate_scores(self, df):
        result = df.copy()

        result["market_cap_score"] = self.normalize(result["market_cap"])
        result["revenue_score"] = self.normalize(result["revenue"])
        result["net_income_score"] = self.normalize(result["net_income"])
        result["profit_margin_score"] = self.normalize(result["profit_margin"])
        result["eps_score"] = self.normalize(result["eps"])

        result["financial_score"] = (
            result["market_cap_score"] * self.weights["market_cap"] +
            result["revenue_score"] * self.weights["revenue"] +
            result["net_income_score"] * self.weights["net_income"] +
            result["profit_margin_score"] * self.weights["profit_margin"] +
            result["eps_score"] * self.weights["eps"]
        )

        return result.sort_values(
            by="financial_score",
            ascending=False
        )