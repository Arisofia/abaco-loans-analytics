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
    df, quality_score = ingestion.normalize_dataframe(source_df, source_name="synthetic")
    df = FeatureEngineer.enrich_portfolio(df)

    st.subheader("Portfolio Overview")
    _render_metrics(df)

    col_quality, col_benchmark = st.columns(2)
    quality_tier = "Excellent" if quality_score >= 90 else "Good" if quality_score >= 75 else "Review"
    col_quality.metric("Data Quality Score", f"{quality_score}/100", help="Completeness and uniqueness weighted score")
    col_quality.caption(f"Quality tier: {quality_tier}")

    try:
        selected_industry = IndustryType[filters["industry"]]
    except (KeyError, ValueError):
        selected_industry = MYPEBusinessRules.default_industry()

    col_benchmark.metric(
        "Rotation Target",
        f"{MYPEBusinessRules.TARGET_ROTATION:.1f}x",
        help="Annual revenue divided by average balance benchmark",
    )
    col_benchmark.metric(
        "Collection Target",
        f"{MYPEBusinessRules.TARGET_COLLECTION_RATE:.0%}",
        help="Expected on-time collections for the segment",
    )

    st.subheader("Customer Table")
    st.dataframe(df)

    st.caption(
        f"Benchmarks for {selected_industry.name}: GDP contribution "
        f"{MYPEBusinessRules.INDUSTRY_GDP_CONTRIBUTION[selected_industry]:.1%}"
    )

    st.subheader("DPD Distribution & Segmentation")
    dpd_distribution = (
        df.get("dpd_bucket", pd.Series(dtype=str))
        .value_counts(normalize=True)
        .reindex(FeatureEngineer.DPD_LABELS, fill_value=0)
        .rename("share")
        .reset_index()
        .rename(columns={"index": "dpd_bucket"})
    )
    segment_distribution = (
        df.get("segment", pd.Series(dtype=str)).value_counts().rename("customers").reset_index().rename(columns={"index": "segment"})
    )

    col_dpd, col_segment = st.columns(2)
    col_dpd.bar_chart(data=dpd_distribution.set_index("dpd_bucket"))
    col_segment.bar_chart(data=segment_distribution.set_index("segment"))
