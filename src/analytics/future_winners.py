import pandas as pd

from analytics.master_ranking import (
    get_master_ranking
)

from analytics.growth_prediction import (
    GrowthPredictor
)


class FutureWinners:

    def get_future_winners(self):

        master_df = get_master_ranking()

        growth_df = (
            GrowthPredictor()
            .get_growth_ranking()
        )

        df = master_df.merge(
            growth_df[
                [
                    "company_id",
                    "growth_score"
                ]
            ],
            on="company_id",
            how="left"
        )

        df["growth_score"] = (
            df["growth_score"]
            .fillna(0)
        )

        df["future_winner_score"] = (
            df["master_score"] * 0.60
            +
            df["growth_score"] * 0.40
        )

        df = df.sort_values(
            "future_winner_score",
            ascending=False
        )

        df["future_rank"] = (
            range(
                1,
                len(df) + 1
            )
        )

        return df

    def summary(self):

        df = self.get_future_winners()

        return {
            "top_company":
                df.iloc[0][
                    "company_id"
                ],
            "average_score":
                round(
                    df[
                        "future_winner_score"
                    ].mean(),
                    2
                ),
            "companies":
                len(df)
        }