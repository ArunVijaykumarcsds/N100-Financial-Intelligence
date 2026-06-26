import pandas as pd
import streamlit as st

from analytics.health_prediction import (
    HealthPredictor
)


def get_health_prediction_dashboard():

    st.title(
        "Financial Health Prediction Dashboard"
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

    predictor = HealthPredictor()

    result = predictor.get_latest_company_data(
        company
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Revenue",
            f"{result['revenue']:,.0f}"
        )

    with col2:
        st.metric(
            "Net Profit",
            f"{result['profit']:,.0f}"
        )

    with col3:
        st.metric(
            "EPS",
            f"{result['eps']:,.2f}"
        )

    st.subheader(
        "Predicted Financial Health"
    )

    st.success(
        result["health"]
    )

    st.write(
        f"""
        Based on revenue, profit,
        and EPS performance,
        {company} is classified as
        **{result['health']}**.
        """
    )