import plotly.express as px
import streamlit as st
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from analytics.company_compare import compare_companies
from pages.top_companies_page import get_top_roe
from pages.company_history_page import (
    get_companies,
    get_company_history
)

st.set_page_config(
    page_title="N100 Financial Intelligence",
    layout="wide"
)

st.title("N100 Financial Intelligence")

st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Choose Module",
    [
        "Home",
        "Top Companies",
        "Company History",
        "Company Comparison"
    ]
)

# =====================================================
# HOME
# =====================================================

if page == "Home":

    st.header("Dashboard Home")
    st.write("Welcome to N100 Financial Intelligence")

# =====================================================
# TOP COMPANIES
# =====================================================

elif page == "Top Companies":

    st.header("Top 10 Companies by ROE")

    df = get_top_roe()

    st.dataframe(
        df,
        use_container_width=True
    )

# =====================================================
# COMPANY HISTORY
# =====================================================

elif page == "Company History":

    st.header("Company History")

    companies = get_companies()

    selected_company = st.selectbox(
        "Select Company",
        companies
    )

    df = get_company_history(
        selected_company
    )

    st.dataframe(
        df,
        width="stretch"
    )

    # Revenue Trend

    st.subheader("Revenue Trend")

    fig = px.line(
        df,
        x="year",
        y="sales",
        markers=True,
        title=f"{selected_company} Revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Net Profit Trend

    st.subheader("Net Profit Trend")

    fig = px.line(
        df,
        x="year",
        y="net_profit",
        markers=True,
        title=f"{selected_company} Net Profit"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # EPS Trend

    st.subheader("EPS Trend")

    fig = px.line(
        df,
        x="year",
        y="eps",
        markers=True,
        title=f"{selected_company} EPS"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# COMPANY COMPARISON
# =====================================================

elif page == "Company Comparison":

    st.header("Company Comparison Analytics")

    companies = get_companies()

    company1 = st.selectbox(
        "Company 1",
        companies,
        index=0
    )

    company2 = st.selectbox(
        "Company 2",
        companies,
        index=1
    )

    df = compare_companies(
        company1,
        company2
    )

    st.dataframe(
        df,
        width="stretch"
    )

    # ROE Comparison

    st.subheader("ROE Comparison")

    fig = px.bar(
        df,
        x="company_name",
        y="roe_percentage",
        title="ROE Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ROCE Comparison

    st.subheader("ROCE Comparison")

    fig = px.bar(
        df,
        x="company_name",
        y="roce_percentage",
        title="ROCE Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Book Value Comparison

    st.subheader("Book Value Comparison")

    fig = px.bar(
        df,
        x="company_name",
        y="book_value",
        title="Book Value Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # Face Value Comparison

    st.subheader("Face Value Comparison")

    fig = px.bar(
        df,
        x="company_name",
        y="face_value",
        title="Face Value Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )