import pandas as pd


class RatioAnalytics:

    def __init__(self):

        self.df = pd.read_excel(
            "data/raw/financial_ratios.xlsx"
        )

        self.latest_df = (
            self.df
            .groupby("company_id")
            .tail(1)
            .copy()
        )

    def ratio_summary(self):

        return {
            "average_roe":
                round(
                    self.latest_df[
                        "return_on_equity_pct"
                    ].mean(),
                    2
                ),

            "average_debt_equity":
                round(
                    self.latest_df[
                        "debt_to_equity"
                    ].mean(),
                    2
                ),

            "average_interest_coverage":
                round(
                    self.latest_df[
                        "interest_coverage"
                    ].mean(),
                    2
                ),

            "companies":
                len(self.latest_df)
        }

    def top_roe(self, n=10):

        return (
            self.latest_df
            .sort_values(
                "return_on_equity_pct",
                ascending=False
            )
            .head(n)
        )

    def lowest_debt(self, n=10):

        return (
            self.latest_df
            .sort_values(
                "debt_to_equity"
            )
            .head(n)
        )

    def highest_interest_coverage(self, n=10):

        return (
            self.latest_df
            .sort_values(
                "interest_coverage",
                ascending=False
            )
            .head(n)
        )