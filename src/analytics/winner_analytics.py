import pandas as pd


class WinnerAnalytics:

    def __init__(self, scored_df):
        self.df = scored_df.copy()

    def top_winners(self, n=10):
        return self.df.nlargest(n, "financial_score")

    def bottom_companies(self, n=10):
        return self.df.nsmallest(n, "financial_score")

    def score_summary(self):
        return {
            "average_score": round(
                self.df["financial_score"].mean(), 2
            ),
            "highest_score": round(
                self.df["financial_score"].max(), 2
            ),
            "lowest_score": round(
                self.df["financial_score"].min(), 2
            ),
            "total_companies": len(self.df)
        }

    def leaderboard(self, n=20):

        leaderboard = self.df.sort_values(
            by="financial_score",
            ascending=False
        ).reset_index(drop=True)

        leaderboard["rank"] = (
            leaderboard.index + 1
        )

        return leaderboard.head(n)