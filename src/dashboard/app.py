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

from pages.financial_health_page import (
    get_financial_health
)

from pages.company_snapshot_page import (
    get_company_snapshot
)

from pages.winner_dashboard_page import (
    get_winner_dashboard
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
        "Company Comparison",
        "Financial Health",
        "Company Snapshot",
        "Winner Dashboard"
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

    

# =====================================================
# FINANCIAL HEALTH
# =====================================================

elif page == "Financial Health":

    st.header("Financial Health Dashboard")

    df = get_financial_health()

    st.dataframe(
        df,
        use_container_width=True
    )

    healthy_count = (
        df["financial_health_rating"] == "Healthy"
    ).sum()

    average_count = (
        df["financial_health_rating"] == "Average"
    ).sum()

    risky_count = (
        df["financial_health_rating"] == "Risky"
    ).sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Healthy Companies",
        healthy_count
    )

    col2.metric(
        "Average Companies",
        average_count
    )

    col3.metric(
        "Risky Companies",
        risky_count
    )

# =====================================================
# COMPANY SNAPSHOT
# =====================================================

elif page == "Company Snapshot":

    st.header("Company Snapshot")

    companies = get_companies()

    selected_company = st.selectbox(
        "Select Company",
        companies
    )

    snapshot = get_company_snapshot(
        selected_company
    )

    if snapshot:

        st.subheader(
            f"{snapshot['company_id']} - Latest Snapshot"
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Health Score",
            snapshot["financial_health_score"]
        )

        col2.metric(
            "Health Rating",
            snapshot["financial_health_rating"]
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Revenue Growth %",
            snapshot["revenue_growth_pct"]
        )

        col2.metric(
            "Profit Growth %",
            snapshot["profit_growth_pct"]
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Profit Margin %",
            snapshot["profit_margin_pct"]
        )

        col2.metric(
            "Operating Margin %",
            snapshot["operating_margin_pct"]
        )

# =====================================================
# WINNER DASHBOARD
# =====================================================

elif page == "Winner Dashboard":

    st.header("Financial Winners Dashboard")

    data = get_winner_dashboard()

    summary = data["summary"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Average Score",
        round(summary["average_score"], 2)
    )

    col2.metric(
        "Highest Score",
        round(summary["highest_score"], 2)
    )

    col3.metric(
        "Lowest Score",
        round(summary["lowest_score"], 2)
    )

    col4.metric(
        "Total Companies",
        summary["total_companies"]
    )

    st.subheader("Top 20 Leaderboard")

    st.dataframe(
        data["leaderboard"][
            [
                "rank",
                "company_id",
                "financial_score"
            ]
        ],
        use_container_width=True
    )

    st.subheader("Top 10 Winners")

    fig = px.bar(
        data["top_winners"],
        x="company_id",
        y="financial_score",
        title="Top Financial Winners"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("Bottom 10 Companies")

    fig = px.bar(
        data["bottom_companies"],
        x="company_id",
        y="financial_score",
        title="Bottom Financial Scores"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )