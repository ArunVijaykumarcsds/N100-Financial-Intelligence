import pandas as pd
import numpy as np


class ValuationAnalyzer:

    def load_latest_prices(self):

        prices = pd.read_excel(
            "data/raw/stock_prices.xlsx"
        )

        prices["date"] = pd.to_datetime(
            prices["date"]
        )

        latest_prices = (
            prices.sort_values("date")
            .groupby("company_id")
            .tail(1)
        )

        return latest_prices[
            [
                "company_id",
                "close_price"
            ]
        ]

    def load_financials(self):

        pnl = pd.read_excel(
            "data/raw/profitandloss.xlsx",
            header=1
        )

        latest_financials = (
            pnl.groupby("company_id")
            .tail(1)
        )

        return latest_financials[
            [
                "company_id",
                "year",
                "eps"
            ]
        ]

    def calculate_pe_ratios(self):

        prices = self.load_latest_prices()

        financials = self.load_financials()

        df = prices.merge(
            financials,
            on="company_id",
            how="inner"
        )

        df["pe_ratio"] = np.where(
            df["eps"] > 0,
            df["close_price"] / df["eps"],
            np.nan
        )

        return df

    def assign_valuation_status(self):

        df = self.calculate_pe_ratios()

        conditions = [
            df["pe_ratio"] < 15,
            (
                (df["pe_ratio"] >= 15)
                &
                (df["pe_ratio"] <= 30)
            ),
            df["pe_ratio"] > 30
        ]

        choices = [
            "Undervalued",
            "Fairly Valued",
            "Overvalued"
        ]

        df["valuation_status"] = np.select(
            conditions,
            choices,
            default="Unknown"
        )

        return df

    def top_undervalued(self, n=10):

        df = self.assign_valuation_status()

        return (
            df[
                df["valuation_status"]
                == "Undervalued"
            ]
            .sort_values(
                "pe_ratio"
            )
            .head(n)
        )

    def top_overvalued(self, n=10):

        df = self.assign_valuation_status()

        return (
            df[
                df["valuation_status"]
                == "Overvalued"
            ]
            .sort_values(
                "pe_ratio",
                ascending=False
            )
            .head(n)
        )

    def valuation_summary(self):

        df = self.assign_valuation_status()

        return {
            "average_pe":
                round(
                    df["pe_ratio"].mean(),
                    2
                ),
            "highest_pe":
                round(
                    df["pe_ratio"].max(),
                    2
                ),
            "lowest_pe":
                round(
                    df["pe_ratio"].min(),
                    2
                ),
            "companies":
                len(df)
        }