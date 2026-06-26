import streamlit as st
import plotly.express as px

from analytics.future_winners import (
    FutureWinners
)


def get_future_winners_dashboard():

    st.title(
        "Future Winners Dashboard"
    )

    model = FutureWinners()

    summary = model.summary()

    df = model.get_future_winners()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Top Company",
            summary["top_company"]
        )

    with col2:
        st.metric(
            "Average Score",
            summary["average_score"]
        )

    with col3:
        st.metric(
            "Companies",
            summary["companies"]
        )

    st.subheader(
        "Future Winners Ranking"
    )

    st.dataframe(
        df[
            [
                "future_rank",
                "company_id",
                "future_winner_score",
                "master_score",
                "growth_score"
            ]
        ],
        use_container_width=True
    )

    st.subheader(
        "Top 20 Future Winners"
    )

    fig = px.bar(
        df.head(20),
        x="company_id",
        y="future_winner_score",
        title="Future Winner Scores"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )