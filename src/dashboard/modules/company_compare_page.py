import pandas as pd
import streamlit as st
import plotly.express as px

from analytics.company_compare import (
    get_company_comparison
)


def get_company_compare_dashboard():

    st.title(
        "Company Comparison Dashboard"
    )

    df = pd.read_excel(
        "data/raw/profitandloss.xlsx",
        header=1
    )

    companies = sorted(
        df["company_id"].unique()
    )

    col1, col2 = st.columns(2)

    with col1:
        company1 = st.selectbox(
            "Company 1",
            companies,
            index=0
        )

    with col2:
        company2 = st.selectbox(
            "Company 2",
            companies,
            index=1
        )

    comparison = get_company_comparison(
        company1,
        company2
    )

    st.subheader(
        "Comparison Table"
    )

    st.dataframe(
        comparison,
        use_container_width=True
    )

    chart_df = comparison[
        [
            "company_id",
            "master_score"
        ]
    ]

    fig = px.bar(
        chart_df,
        x="company_id",
        y="master_score",
        title="Master Score Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )