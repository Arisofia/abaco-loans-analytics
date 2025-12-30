import io
import re
from typing import Optional

import pandas as pd

try:
    import plotly.express as px
except ImportError as e:
    raise ImportError(
        "plotly.express could not be imported. Ensure 'plotly' is installed in your environment."
    ) from e
import streamlit as st

from src.analytics_metrics import (
    calculate_quality_score,
    import pandas as pd
    import streamlit as st
    from src.analytics_metrics import get_kpi_metrics
    from streamlit_app.utils.ingestion import parse_uploaded_file
    from streamlit_app.utils.business_rules import apply_business_rules, engineer_features

    def main():
        st.title("Abaco Loans Analytics Dashboard")
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        df = parse_uploaded_file(uploaded_file)
        if df is not None:
            st.write("Raw Data", df.head())
            df_clean = apply_business_rules(df)
            df_features = engineer_features(df_clean)
            st.write("Processed Data", df_features.head())
            kpi_metrics = get_kpi_metrics(df_features)
            st.write("KPI Metrics", kpi_metrics)
        else:
            st.info("Please upload a CSV file to begin.")

    if __name__ == "__main__":
        main()


def ensure_required_columns(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        st.error(f"Missing required columns: {', '.join(missing)}")
        return None
    return df


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    for col in [
        "loan_amount",
        "appraised_value",
        "borrower_income",
        "monthly_debt",
        "interest_rate",
        "principal_balance",
    ]:
        work[col] = standardize_numeric(work[col])
    return work


def render_metrics(df: pd.DataFrame) -> None:
    # Compute portfolio KPIs and get enriched DataFrame
    metrics, enriched = portfolio_kpis(df)
    quality = calculate_quality_score(df)

    st.subheader("Portfolio KPIs")
    cols = st.columns(4)
    cols[0].metric("Delinquency rate", f"{metrics['delinquency_rate']:.2f}%")
    cols[1].metric("Portfolio yield", f"{metrics['portfolio_yield']:.2f}%")
    cols[2].metric("Average LTV", f"{metrics['average_ltv']:.2f}%")
    cols[3].metric("Average DTI", f"{metrics['average_dti']:.2f}")

    st.metric("Data quality score", f"{quality:.0f}/100")

    # Projection logic is independent of enrichment/metrics
    st.subheader("Projection")
    projection = project_growth(
        current_yield=float(metrics["portfolio_yield"]),
        target_yield=float(metrics["portfolio_yield"] * 1.1),
        current_loan_volume=float(df["principal_balance"].sum()),
        target_loan_volume=float(df["principal_balance"].sum() * 1.2),
    )
    fig = px.line(projection, x="date", y=["yield", "loan_volume"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # Show a sample of the enriched DataFrame
    st.subheader("Enriched sample")
    st.dataframe(enriched.head())


def main() -> None:
    st.set_page_config(page_title="ABACO Analytics", layout="wide")
    st.title("ABACO Loan Analytics")
    st.write("Upload a portfolio extract to compute governed KPIs and quality signals.")

    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv", "xls", "xlsx"])
    df = parse_uploaded_file(uploaded)
    if df.empty:
        st.info("Awaiting data upload.")
        return

    df = ensure_required_columns(df)
    if df is None:
        return

    df = coerce_numeric(df)
    render_metrics(df)


if __name__ == "__main__":
    main()
