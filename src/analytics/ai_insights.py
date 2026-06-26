from analytics.future_winners import (
    FutureWinners
)


class AIInsights:

    def generate_insight(
        self,
        company_id
    ):

        df = (
            FutureWinners()
            .get_future_winners()
        )

        company = df[
            df["company_id"]
            == company_id
        ]

        if company.empty:
            return None

        company = company.iloc[0]

        score = company[
            "future_winner_score"
        ]

        if score >= 80:

            recommendation = (
                "Strong Buy"
            )

            insight = (
                f"{company_id} demonstrates "
                f"excellent growth potential "
                f"and ranks among the strongest "
                f"future performers."
            )

        elif score >= 60:

            recommendation = (
                "Buy"
            )

            insight = (
                f"{company_id} shows healthy "
                f"growth characteristics and "
                f"solid long-term potential."
            )

        elif score >= 40:

            recommendation = (
                "Hold"
            )

            insight = (
                f"{company_id} appears stable "
                f"but may require stronger "
                f"growth signals."
            )

        else:

            recommendation = (
                "Avoid"
            )

            insight = (
                f"{company_id} currently "
                f"shows weaker future "
                f"performance indicators."
            )

        return {

            "company_id":
                company_id,

            "future_winner_score":
                round(
                    score,
                    2
                ),

            "recommendation":
                recommendation,

            "insight":
                insight
        }