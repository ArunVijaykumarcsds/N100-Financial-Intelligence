import plotly.express as px
import streamlit as st
import sys
from pathlib import Path

from modules.master_ranking_dashboard_page import (
    get_master_dashboard
)

from modules.ratio_analytics_page import (
    get_ratio_dashboard
)

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from analytics.company_compare import get_company_comparison
from modules.top_companies_page import get_top_roe
from modules.company_history_page import (
    get_companies,
    get_company_history
)

from modules.financial_health_page import (
    get_financial_health
)

from modules.company_snapshot_page import (
    get_company_snapshot
)

from modules.winner_dashboard_page import (
    get_winner_dashboard
)

from modules.sector_analytics_page import (
    get_sector_dashboard
)

from modules.valuation_dashboard_page import (
    get_valuation_dashboard
)

from modules.growth_dashboard_page import (
    get_growth_dashboard
)

from modules.eps_forecasting_page import (
    get_eps_forecasting_dashboard
)

st.set_page_config(
    page_title="N100 Financial Intelligence",
    layout="wide"
)

from modules.company_compare_page import (
    get_company_compare_dashboard
)

from modules.revenue_forecasting_page import (
    get_revenue_forecasting_dashboard
)

from modules.profit_forecasting_page import (
    get_profit_forecasting_dashboard
)

from modules.health_prediction_page import (
    get_health_prediction_dashboard
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
        "Winner Dashboard",
        "Sector Analytics",
        "Valuation Dashboard",
        "Growth Dashboard",
        "Master Ranking",
        "Revenue Forecasting",
        "Profit Forecasting",
        "EPS Forecasting",
        "Health Prediction",
        
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

    get_company_compare_dashboard()

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

# =====================================================
# SECTOR ANALYTICS
# =====================================================

elif page == "Sector Analytics":

    st.header("Sector Analytics Dashboard")

    data = get_sector_dashboard()

    col1, col2 = st.columns(2)

    col1.metric(
        "Top Sector",
        data["top_sector"]["broad_sector"]
    )

    col2.metric(
        "Bottom Sector",
        data["bottom_sector"]["broad_sector"]
    )

    st.subheader(
        "Sector Summary"
    )

    st.dataframe(
        data["summary"],
        use_container_width=True
    )

    st.subheader(
        "Sector Weight Leaderboard"
    )

    st.dataframe(
        data["leaderboard"],
        use_container_width=True
    )

    st.subheader(
        "Market Cap Distribution"
    )

    st.dataframe(
        data["market_cap_distribution"],
        use_container_width=True
    )

    fig = px.bar(
        data["leaderboard"],
        x="broad_sector",
        y="sector_weight",
        title="Sector Weight Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# VALUATION DASHBOARD
# =====================================================

elif page == "Valuation Dashboard":

    st.header("Valuation Dashboard")

    data = get_valuation_dashboard()

    summary = data["summary"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Average PE",
        summary["average_pe"]
    )

    col2.metric(
        "Highest PE",
        summary["highest_pe"]
    )

    col3.metric(
        "Lowest PE",
        summary["lowest_pe"]
    )

    col4.metric(
        "Companies",
        summary["companies"]
    )

    st.subheader(
        "Top Undervalued Companies"
    )

    st.dataframe(
        data["undervalued"],
        use_container_width=True
    )

    st.subheader(
        "Top Overvalued Companies"
    )

    st.dataframe(
        data["overvalued"],
        use_container_width=True
    )

    fig = px.bar(
        data["undervalued"],
        x="company_id",
        y="pe_ratio",
        title="Top Undervalued Companies"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.bar(
        data["overvalued"],
        x="company_id",
        y="pe_ratio",
        title="Top Overvalued Companies"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# GROWTH DASHBOARD
# =====================================================

elif page == "Growth Dashboard":

    st.header("Growth Analytics Dashboard")

    data = get_growth_dashboard()

    summary = data["summary"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Average Growth",
        summary["average_growth"]
    )

    col2.metric(
        "Highest Growth",
        summary["highest_growth"]
    )

    col3.metric(
        "Lowest Growth",
        summary["lowest_growth"]
    )

    col4.metric(
        "Companies",
        summary["companies"]
    )

    st.subheader(
        "Top Growth Companies"
    )

    st.dataframe(
        data["top_growth"][
            [
                "company_id",
                "revenue_growth_pct",
                "profit_growth_pct",
                "growth_score"
            ]
        ],
        use_container_width=True
    )

    st.subheader(
        "Bottom Growth Companies"
    )

    st.dataframe(
        data["bottom_growth"][
            [
                "company_id",
                "revenue_growth_pct",
                "profit_growth_pct",
                "growth_score"
            ]
        ],
        use_container_width=True
    )

    fig = px.bar(
        data["top_growth"],
        x="company_id",
        y="growth_score",
        title="Top Growth Companies"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    fig = px.bar(
        data["bottom_growth"],
        x="company_id",
        y="growth_score",
        title="Bottom Growth Companies"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================================
# MASTER RANKING
# =====================================================

elif page == "Master Ranking":

    st.header("Master Ranking Dashboard")

    data = get_master_dashboard()

    summary = data["summary"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Companies",
        summary["total_companies"]
    )

    col2.metric(
        "Highest Score",
        summary["highest_score"]
    )

    col3.metric(
        "Average Score",
        summary["average_score"]
    )

    st.subheader(
        "Top 20 Leaderboard"
    )

    st.dataframe(
        data["leaderboard"][
            [
                "rank",
                "company_id",
                "master_score",
                "financial_score",
                "quality_score",
                "valuation_score"
            ]
        ],
        use_container_width=True
    )

    fig = px.bar(
        data["leaderboard"].head(10),
        x="company_id",
        y="master_score",
        title="Top 10 Master Ranked Companies"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# app.py UI block below 

elif page == "Ratio Analytics":

    data = get_ratio_dashboard()

    st.header(
        "Ratio Analytics Dashboard"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average ROE",
        data["summary"]["average_roe"]
    )

    c2.metric(
        "Average Debt/Equity",
        data["summary"][
            "average_debt_equity"
        ]
    )

    c3.metric(
        "Interest Coverage",
        data["summary"][
            "average_interest_coverage"
        ]
    )

    c4.metric(
        "Companies",
        data["summary"]["companies"]
    )

    st.subheader(
        "Top ROE Companies"
    )

    st.dataframe(
        data["top_roe"]
    )

    fig = px.bar(
        data["top_roe"],
        x="company_id",
        y="return_on_equity_pct"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Lowest Debt Companies"
    )

    st.dataframe(
        data["lowest_debt"]
    )

    st.subheader(
        "Highest Interest Coverage"
    )

    st.dataframe(
        data["coverage"]
    )

# revenue forecasting via Linear regression 
elif page == "Revenue Forecasting":

    get_revenue_forecasting_dashboard()

# profit forecasting Dashboard 
elif page == "Profit Forecasting":

    get_profit_forecasting_dashboard()

# EPS Forecasting Dashboard 
elif page == "EPS Forecasting":

    get_eps_forecasting_dashboard()

# health_prediction_page Dashboard 
elif page == "Health Prediction":

    get_health_prediction_dashboard()