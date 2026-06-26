import pandas as pd
import streamlit as st
import plotly.express as px

from analytics.revenue_forecasting import (
    RevenueForecaster
)


def get_revenue_forecasting_dashboard():

    st.title(
        "Revenue Forecasting Dashboard"
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

    model = RevenueForecaster()

    result = model.predict_company_revenue(
        company
    )

    if result is None:
        st.warning(
            "Not enough historical data."
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Forecast Year",
            result["next_year"]
        )

    with col2:
        st.metric(
            "Predicted Revenue",
            f"{result['predicted_revenue']:,.2f}"
        )

    history = model.clean_data()

    history = history[
        history["company_id"] == company
    ]

    fig = px.line(
        history,
        x="year_num",
        y="sales",
        title=f"{company} Revenue Trend"
    )

    fig.add_scatter(
        x=[result["next_year"]],
        y=[result["predicted_revenue"]],
        mode="markers",
        name="Forecast"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )