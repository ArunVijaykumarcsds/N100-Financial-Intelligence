import streamlit as st
import plotly.express as px

from analytics.future_winners import (
    FutureWinners
)

from analytics.growth_prediction import (
    GrowthPredictor
)


def get_executive_command_center():

    st.title(
        "Executive Command Center"
    )

    winners = (
        FutureWinners()
        .get_future_winners()
    )

    growth = (
        GrowthPredictor()
        .get_growth_ranking()
    )

    top_winner = winners.iloc[0]

    top_growth = growth.iloc[0]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Top Future Winner",
            top_winner["company_id"]
        )

    with col2:

        st.metric(
            "Best Growth Company",
            top_growth["company_id"]
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Top 10 Future Winners"
        )

        st.dataframe(
            winners[
                [
                    "future_rank",
                    "company_id",
                    "future_winner_score"
                ]
            ].head(10),
            use_container_width=True
        )

    with col2:

        st.subheader(
            "Top 10 Growth Companies"
        )

        st.dataframe(
            growth[
                [
                    "rank",
                    "company_id",
                    "growth_score"
                ]
            ].head(10),
            use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        fig1 = px.bar(
            winners.head(10),
            x="company_id",
            y="future_winner_score",
            title="Future Winner Scores"
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with col2:

        fig2 = px.bar(
            growth.head(10),
            x="company_id",
            y="growth_score",
            title="Growth Scores"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.divider()

    st.subheader(
        "AI Recommendation Feed"
    )

    recommendations = winners[
        [
            "company_id",
            "future_winner_score"
        ]
    ].head(10)

    for _, row in recommendations.iterrows():

        score = row[
            "future_winner_score"
        ]

        if score >= 80:

            recommendation = (
                "Strong Buy"
            )

        elif score >= 60:

            recommendation = (
                "Buy"
            )

        elif score >= 40:

            recommendation = (
                "Hold"
            )

        else:

            recommendation = (
                "Avoid"
            )

        st.write(
            f"**{row['company_id']}** → {recommendation}"
        )