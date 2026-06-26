import pandas as pd
import streamlit as st
import plotly.express as px

from analytics.eps_forecasting import (
    EPSForecaster
)


def get_eps_forecasting_dashboard():

    st.title(
        "EPS Forecasting Dashboard"
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

    model = EPSForecaster()

    result = model.predict_company_eps(
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
            "Predicted EPS",
             result["predicted_eps"]
        )

    st.subheader(
        "Forecast Summary"
    )

    st.write(
    f"""
    Based on historical EPS trends,
    {company} is projected to generate
    an EPS of {result['predicted_eps']}
    in {result['next_year']}.
    """
)

    history = model.clean_data()

    history = history[
        history["company_id"] == company
    ]

    fig = px.line(
    history,
    x="year_num",
    y="eps",
    title=f"{company} EPS Trend"
)

    fig.add_scatter(
    x=[result["next_year"]],
    y=[result["predicted_eps"]],
    mode="markers",
    name="Forecast"
)

    st.plotly_chart(
        fig,
        use_container_width=True
    )