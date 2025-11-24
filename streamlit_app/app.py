"""Streamlit application layout and interactions."""
from __future__ import annotations

import datetime as dt
from typing import Dict

import pandas as pd
import streamlit as st

from streamlit_app.config import theme
from streamlit_app.utils.business_rules import IndustryType, MYPEBusinessRules
from streamlit_app.utils.feature_engineering import FeatureEngineer
from streamlit_app.utils.ingestion import DataIngestionEngine


def _sidebar_filters() -> Dict:
    st.sidebar.subheader("Filters")
    industry = st.sidebar.selectbox(
        "Industry",
        options=[option.name for option in MYPEBusinessRules.INDUSTRY_GDP_CONTRIBUTION.keys()],
        index=0,
    )
    target_date = st.sidebar.date_input("As of", value=dt.date.today())
    return {"industry": industry, "as_of": target_date}


def _render_metrics(df: pd.DataFrame) -> None:
    utilization = FeatureEngineer.calculate_utilization(
        balance=df["balance"].sum(), limit=df["limit"].sum()
    )
    rotation, meets_target, _ = MYPEBusinessRules.check_rotation_target(
        total_revenue=df["revenue"].sum(), avg_balance=df["balance"].mean()
    )
    pod = (df["dpd"].mean() / MYPEBusinessRules.NPL_DAYS_THRESHOLD) * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Utilization", f"{utilization:.2%}")
    col2.metric("Rotation", f"{rotation:.1f}", delta="On target" if meets_target else "Below")
    col3.metric("Probability of Default", f"{pod:.1f}%", delta_color="inverse")


def render_dashboard() -> None:
    st.title("AI-Powered Loan Analytics")
    filters = _sidebar_filters()

    ingestion = DataIngestionEngine("", "", {})
    source_df = pd.DataFrame(
        [
            {"customer": "Acme", "balance": 120000, "limit": 200000, "revenue": 480000, "dpd": 12},
            {
                "customer": "Lumen",
                "balance": 80000,
                "limit": 150000,
                "revenue": 300000,
                "dpd": 45,
            },
        ]
    )
    df, _ = ingestion.normalize_dataframe(source_df, source_name="synthetic")

    st.subheader("Portfolio Overview")
    _render_metrics(df)

    st.subheader("Customer Table")
    st.dataframe(df)

    try:
        selected_industry = IndustryType[filters["industry"]]
    except (KeyError, ValueError):
        selected_industry = MYPEBusinessRules.default_industry()

    st.caption(
        f"Benchmarks for {selected_industry.name}: GDP contribution "
        f"{MYPEBusinessRules.INDUSTRY_GDP_CONTRIBUTION[selected_industry]:.1%}"
    )
