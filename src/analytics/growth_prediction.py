import pandas as pd


class GrowthPredictor:

    def __init__(self):

        self.df = pd.read_excel(
            "data/raw/profitandloss.xlsx",
            header=1
        )

    def get_growth_ranking(self):

        df = self.df.copy()

        latest_records = []

        for company in df["company_id"].unique():

            company_df = df[
                df["company_id"] == company
            ]

            company_df = company_df.sort_values(
                "year"
            )

            if len(company_df) < 2:
                continue

            latest = company_df.iloc[-1]
            previous = company_df.iloc[-2]

            revenue_growth = (
                (
                    latest["sales"]
                    - previous["sales"]
                )
                / max(previous["sales"], 1)
            ) * 100

            profit_growth = (
                (
                    latest["net_profit"]
                    - previous["net_profit"]
                )
                / max(abs(previous["net_profit"]), 1)
            ) * 100

            eps_growth = (
                (
                    latest["eps"]
                    - previous["eps"]
                )
                / max(abs(previous["eps"]), 1)
            ) * 100

            growth_score = (
                revenue_growth * 0.4
                + profit_growth * 0.4
                + eps_growth * 0.2
            )

            latest_records.append(
                {
                    "company_id": company,
                    "revenue_growth": round(
                        revenue_growth,
                        2
                    ),
                    "profit_growth": round(
                        profit_growth,
                        2
                    ),
                    "eps_growth": round(
                        eps_growth,
                        2
                    ),
                    "growth_score": round(
                        growth_score,
                        2
                    )
                }
            )

        result = pd.DataFrame(
            latest_records
        )

        result = result.sort_values(
            "growth_score",
            ascending=False
        )

        result["rank"] = (
            range(
                1,
                len(result) + 1
            )
        )

        return result