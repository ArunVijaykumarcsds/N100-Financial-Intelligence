import pandas as pd
import streamlit as st
import plotly.express as px

from analytics.profit_forecasting import (
    ProfitForecaster
)


def get_profit_forecasting_dashboard():

    st.title(
        "Profit Forecasting Dashboard"
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

    model = ProfitForecaster()

    result = model.predict_company_profit(
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
            "Predicted Profit",
            f"{result['predicted_profit']:,.2f}"
        )

    st.subheader(
        "Forecast Summary"
    )

    st.write(
        f"""
        Based on historical profit trends,
        {company} is projected to generate
        ₹{result['predicted_profit']:,.2f}
        profit in {result['next_year']}.
        """
    )

    history = model.clean_data()

    history = history[
        history["company_id"] == company
    ]

    fig = px.line(
        history,
        x="year_num",
        y="net_profit",
        title=f"{company} Profit Trend"
    )

    fig.add_scatter(
        x=[result["next_year"]],
        y=[result["predicted_profit"]],
        mode="markers",
        name="Forecast"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )