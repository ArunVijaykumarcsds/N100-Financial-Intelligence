import pandas as pd
import streamlit as st

from analytics.ai_insights import (
    AIInsights
)


def get_ai_insights_dashboard():

    st.title(
        "AI Insights Engine"
    )

    df = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    companies = sorted(
        df["company_id"].unique()
    )

    company = st.selectbox(
        "Select Company",
        companies
    )

    result = (
        AIInsights()
        .generate_insight(
            company
        )
    )

    if result is None:

        st.warning(
            "No insight available."
        )

        return

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Future Winner Score",
            result[
                "future_winner_score"
            ]
        )

    with col2:

        st.metric(
            "Recommendation",
            result[
                "recommendation"
            ]
        )

    st.subheader(
        "Generated Insight"
    )

    recommendation = result[
        "recommendation"
    ]

    if recommendation == (
        "Strong Buy"
    ):

        st.success(
            result["insight"]
        )

    elif recommendation == (
        "Buy"
    ):

        st.info(
            result["insight"]
        )

    elif recommendation == (
        "Hold"
    ):

        st.warning(
            result["insight"]
        )

    else:

        st.error(
            result["insight"]
        )