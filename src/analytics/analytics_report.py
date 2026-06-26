import pandas as pd


class AnalyticsReport:

    def company_snapshot(self, df, company_id):

        company = (
            df[df["company_id"] == company_id]
            .sort_values("year")
            .tail(1)
        )

        if company.empty:
            return None

        row = company.iloc[0]

        return {
            "company_id": str(row["company_id"]),
            "year": str(row["year"]),
            "financial_health_rating": str(
                row["financial_health_rating"]
            ),
            "financial_health_score": int(
                row["financial_health_score"]
            ),
            "revenue_growth_pct": round(
                float(row["revenue_growth_pct"]), 2
            ),
            "profit_growth_pct": round(
                float(row["profit_growth_pct"]), 2
            ),
            "profit_margin_pct": round(
                float(row["profit_margin_pct"]), 2
            ),
            "operating_margin_pct": round(
                float(row["operating_margin_pct"]), 2
            )
        }