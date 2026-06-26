import streamlit as st
import plotly.express as px

from analytics.growth_prediction import (
    GrowthPredictor
)


def get_growth_prediction_dashboard():

    st.title(
        "Growth Prediction Dashboard"
    )

    predictor = GrowthPredictor()

    df = predictor.get_growth_ranking()

    st.subheader(
        "Top Growth Companies"
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    st.subheader(
        "Top 20 Growth Scores"
    )

    fig = px.bar(
        df.head(20),
        x="company_id",
        y="growth_score",
        title="Growth Score Ranking"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )