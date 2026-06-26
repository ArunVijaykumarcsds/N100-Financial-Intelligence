import pandas as pd


class HealthPredictor:

    def __init__(self):

        self.df = pd.read_excel(
            "data/raw/profitandloss.xlsx",
            header=1
        )

    def get_latest_company_data(
        self,
        company_id
    ):

        company = self.df[
            self.df["company_id"]
            == company_id
        ]

        latest = company.tail(1)

        revenue = float(
            latest["sales"].iloc[0]
        )

        profit = float(
            latest["net_profit"].iloc[0]
        )

        eps = float(
            latest["eps"].iloc[0]
        )

        score = (
            revenue * 0.4 +
            profit * 0.4 +
            eps * 0.2
        )

        if score > 5000:
            health = "Excellent"

        elif score > 2000:
            health = "Good"

        elif score > 500:
            health = "Average"

        else:
            health = "Weak"

        return {
            "company_id": company_id,
            "revenue": revenue,
            "profit": profit,
            "eps": eps,
            "health": health
        }