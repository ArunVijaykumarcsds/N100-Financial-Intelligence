import pandas as pd

from sklearn.linear_model import LinearRegression


class EPSForecaster:

    def __init__(self):

        self.df = pd.read_excel(
            "data/raw/profitandloss.xlsx",
            header=1
        )

    def clean_data(self):

        df = self.df.copy()

        df["year_num"] = (
            df["year"]
            .astype(str)
            .str.extract(r"(\d{4})")
        )

        df = df.dropna(
            subset=["year_num"]
        )

        df["year_num"] = (
            df["year_num"]
            .astype(int)
        )

        return df

    def predict_company_eps(
        self,
        company_id
    ):

        df = self.clean_data()

        company = df[
            df["company_id"]
            == company_id
        ]

        company = company.sort_values(
            "year_num"
        )

        X = company[
            ["year_num"]
        ]

        y = company["eps"]

        if len(company) < 3:
            return None

        model = LinearRegression()

        model.fit(X, y)

        next_year = int(
            company["year_num"].max() + 1
        )

        prediction = float(
            model.predict(
                pd.DataFrame(
                    {"year_num": [next_year]}
                )
            )[0]
        )

        return {
    "company_id": company_id,
    "next_year": next_year,
    "predicted_eps": round(
        prediction,
        2
    )
}