import hashlib
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from utils.feature_engineering import FeatureEngineer

st.set_page_config(layout="wide", page_title="Abaco Loans Analytics Dashboard")

# --- Data Ingestion Simulation ---
@st.cache_data
def load_and_prepare_data():
    rng_seed = 7
    rng = np.random.default_rng(rng_seed)
    data = {
        'customer_id': range(100),
        'revenue': rng.uniform(10000, 150000, 100),
        'balance': rng.uniform(1000, 50000, 100),
        'limit': rng.uniform(20000, 100000, 100),
        'dpd': rng.choice([-1, 0, 15, 45, 75, 100], 100, p=[0.1, 0.6, 0.1, 0.1, 0.05, 0.05]),
    }
    raw_df = pd.DataFrame(data)

    completeness = (raw_df.notna().sum().sum() / (raw_df.shape[0] * raw_df.shape[1])) * 100
    freshness_days = rng.integers(0, 5)
    checksum = hashlib.sha256(pd.util.hash_pandas_object(raw_df, index=True).values).hexdigest()
    metadata = {
        "rng_seed": rng_seed,
        "record_count": len(raw_df),
        "completeness_pct": completeness,
        "freshness_days": int(freshness_days),
        "ingestion_ts": pd.Timestamp.utcnow().isoformat(),
        "source_system": "demo-synthetic-generator",
        "dataset_checksum": checksum,
    }
    return raw_df, metadata

# --- Main Application ---
st.title("Abaco Loans Analytics Dashboard")

# 1. Ingestion and Enrichment
raw_portfolio_df, ingestion_metadata = load_and_prepare_data()
enriched_df = FeatureEngineer.enrich_portfolio(raw_portfolio_df)

st.caption(
    "Data sources mocked for demo purposes. KPIs are derived deterministically for traceability."
)

portfolio_size = len(enriched_df)
delinquency_rate = (enriched_df['dpd'] > 30).mean() * 100
avg_utilization = (
    enriched_df['utilization'].mean() * 100 if 'utilization' in enriched_df.columns else 0
)
avg_yield = (enriched_df['revenue'] / enriched_df['balance']).mean()
limit_utilization = (enriched_df['balance'] / enriched_df['limit']).mean() * 100
dpd_30_rate = (enriched_df['dpd'] >= 30).mean() * 100

# 2. Display High-Level Metrics
st.header("Portfolio Health & Quality Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Data Quality Score", f"{ingestion_metadata['completeness_pct']:.2f}%", help="Completeness of the source data.")
col2.metric("Data Freshness", f"{ingestion_metadata['freshness_days']} days", help="Lag since last ingestion.")
col3.metric("Delinquency Rate", f"{delinquency_rate:.1f}%", delta="vs. target 6.5%", delta_color="inverse")
col4.metric("Avg. Portfolio Yield", f"{avg_yield:.2f}x", help="Revenue-to-balance yield factor.")
col5.metric("Limit Utilization", f"{limit_utilization:.1f}%", help="Balance-to-limit consumption.")

kpi_table = pd.DataFrame([
    {"KPI": "Active Customers", "Value": portfolio_size, "Target": 100, "Status": "On Track"},
    {"KPI": "Avg Utilization", "Value": f"{avg_utilization:.1f}%", "Target": "< 65%", "Status": "On Track"},
    {"KPI": "30+ DPD", "Value": f"{dpd_30_rate:.1f}%", "Target": "< 12%", "Status": "Watch"},
    {"KPI": "90+ DPD", "Value": f"{(enriched_df['dpd'] >= 90).mean() * 100:.1f}%", "Target": "< 5%", "Status": "Watch"},
    {"KPI": "Collections Coverage", "Value": "92%", "Target": "95%", "Status": "Catch-Up"},
])

st.dataframe(kpi_table, hide_index=True, use_container_width=True)

controls_table = pd.DataFrame([
    {
        "Control": "Deterministic Seed",
        "Owner": "Data Engineering",
        "Status": "Pass",
        "Detail": f"rng_seed={ingestion_metadata['rng_seed']} ensures reproducibility",
    },
    {
        "Control": "Data Completeness",
        "Owner": "Data Quality",
        "Status": "Pass" if ingestion_metadata['completeness_pct'] >= 95 else "Watch",
        "Detail": f"{ingestion_metadata['completeness_pct']:.2f}% non-null coverage",
    },
    {
        "Control": "Checksum Traceability",
        "Owner": "Risk & Controls",
        "Status": "Pass",
        "Detail": f"SHA-256: {ingestion_metadata['dataset_checksum'][:12]}...",
    },
    {
        "Control": "Freshness SLA",
        "Owner": "Ops",
        "Status": "Pass" if ingestion_metadata['freshness_days'] <= 1 else "Watch",
        "Detail": f"{ingestion_metadata['freshness_days']} days since last load",
    },
])

st.subheader("Operational Controls & Audit Trail")
st.dataframe(controls_table, hide_index=True, use_container_width=True)

# 3. Display Distribution Charts
st.header("Customer Distributions")
col_dist1, col_dist2 = st.columns(2)

with col_dist1:
    dpd_chart = alt.Chart(enriched_df).mark_bar().encode(
        x=alt.X('dpd_bucket:N', title='DPD Bucket', sort=['Current', '1-30 DPD', '31-60 DPD', '61-90 DPD', '90+ DPD']),
        y=alt.Y('count():Q', title='Number of Customers'),
        tooltip=['dpd_bucket', 'count()']
    ).properties(
        title='DPD Bucket Distribution'
    )
    st.altair_chart(dpd_chart, use_container_width=True)

with col_dist2:
    segment_chart = alt.Chart(enriched_df).mark_bar().encode(
        x=alt.X('segment:N', title='Customer Segment', sort=['Bronze', 'Silver', 'Gold']),
        y=alt.Y('count():Q', title='Number of Customers'),
        tooltip=['segment', 'count()']
    ).properties(
        title='Customer Segment Distribution'
    )
    st.altair_chart(segment_chart, use_container_width=True)

st.header("Utilization by Segment")
utilization_chart = alt.Chart(enriched_df).mark_bar().encode(
    x=alt.X('segment:N', sort=['Bronze', 'Silver', 'Gold'], title='Customer Segment'),
    y=alt.Y('mean(utilization):Q', title='Avg Utilization'),
    color='segment:N',
    tooltip=[
        alt.Tooltip('segment', title='Segment'),
        alt.Tooltip('mean(utilization)', title='Avg Utilization', format='.1%'),
        alt.Tooltip('count()', title='Customers')
    ]
).properties(title='Segment Utilization Efficiency')
st.altair_chart(utilization_chart, use_container_width=True)

st.header("Yield and Risk Correlation")
yield_risk_chart = alt.Chart(enriched_df).mark_circle(size=80, opacity=0.7).encode(
    x=alt.X('utilization:Q', title='Utilization'),
    y=alt.Y('dpd:Q', title='Days Past Due'),
    color=alt.Color('segment:N', title='Segment'),
    size=alt.Size('revenue:Q', title='Revenue', legend=None),
    tooltip=[
        alt.Tooltip('customer_id', title='Customer'),
        alt.Tooltip('segment', title='Segment'),
        alt.Tooltip('utilization', title='Utilization', format='.1%'),
        alt.Tooltip('dpd', title='DPD'),
        alt.Tooltip('revenue', title='Revenue', format=',.0f')
    ]
).properties(title='Utilization vs. Delinquency by Segment')
st.altair_chart(yield_risk_chart, use_container_width=True)

st.header("Delinquency Incidence by Segment")
segment_delinquency = (
    enriched_df.assign(delinquent=lambda df: df['dpd'] >= 30)
    .groupby('segment')
    .agg(
        customers=('customer_id', 'count'),
        delinquent_customers=('delinquent', 'sum'),
        delinquency_rate=('delinquent', 'mean'),
    )
    .reset_index()
)

segment_dpd_chart = alt.Chart(segment_delinquency).mark_bar().encode(
    x=alt.X('segment:N', sort=['Bronze', 'Silver', 'Gold'], title='Customer Segment'),
    y=alt.Y('delinquency_rate:Q', title='30+ DPD Rate', axis=alt.Axis(format='%')),
    tooltip=[
        alt.Tooltip('segment', title='Segment'),
        alt.Tooltip('customers', title='Customers'),
        alt.Tooltip('delinquent_customers', title='30+ DPD'),
        alt.Tooltip('delinquency_rate', title='30+ DPD Rate', format='.1%'),
    ],
    color='segment:N',
).properties(title='30+ DPD Incidence by Segment')
st.altair_chart(segment_dpd_chart, use_container_width=True)

# 4. Display Customer Data Table
st.header("Enriched Customer Portfolio Data")
st.dataframe(enriched_df)
with st.expander("Data lineage & governance"):
    st.json(
        {
            "ingestion_ts": ingestion_metadata['ingestion_ts'],
            "rng_seed": ingestion_metadata['rng_seed'],
            "records": ingestion_metadata['record_count'],
            "completeness_pct": round(ingestion_metadata['completeness_pct'], 2),
            "freshness_days": ingestion_metadata['freshness_days'],
            "source_system": ingestion_metadata['source_system'],
            "dataset_checksum": ingestion_metadata['dataset_checksum'],
        }
    )
st.caption("Industry GDP Benchmark: +2.1% (YoY)")
