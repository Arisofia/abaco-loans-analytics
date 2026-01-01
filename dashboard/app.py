"""Streamlit dashboard for Abaco Loans Analytics - Real Data Dashboard."""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path
import logging
import sys

st.set_page_config(layout="wide", page_title="Abaco Loans Analytics - Executive Dashboard")

logger = logging.getLogger(__name__)

# Initialize tracing early; tolerate missing exporters in dev
try:
    from tracing_setup import init_tracing, enable_auto_instrumentation
    init_tracing(service_name="abaco-dashboard")
    enable_auto_instrumentation()
except Exception as tracing_err:  # pragma: no cover - defensive
    logger.warning("Tracing not initialized: %s", tracing_err)

# Health check page - responds to /?page=health
query_params = st.query_params
page = query_params.get("page")
if page == "health" or page == ["health"] or (isinstance(page, list) and "health" in page):
    st.write("ok")
    st.stop()

@st.cache_data
def load_loan_data():
    """Load real loan data from CSV files."""
    data_path = Path(__file__).parent.parent / "data" / "raw" / "looker_exports" / "loans.csv"
    if not data_path.exists():
        data_path = Path(__file__).parent / "data" / "raw" / "looker_exports" / "loans.csv"
    
    if not data_path.exists():
        st.error(f"Data file not found: {data_path}")
        return None
    
    df = pd.read_csv(data_path)
    
    # Clean and prepare data
    df['outstanding_balance'] = pd.to_numeric(df['outstanding_balance'], errors='coerce').fillna(0)
    df['disburse_principal'] = pd.to_numeric(df['disburse_principal'], errors='coerce').fillna(0)
    df['interest_rate'] = pd.to_numeric(df['interest_rate'], errors='coerce').fillna(0)
    df['dpd'] = pd.to_numeric(df['dpd'], errors='coerce').fillna(0)
    df['term'] = pd.to_numeric(df['term'], errors='coerce').fillna(0)
    
    # Convert date columns
    date_cols = ['application_date', 'disburse_date', 'maturity_date', 'pledge_date']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

@st.cache_data
def calculate_portfolio_metrics(df):
    """Calculate key portfolio metrics."""
    if df is None or df.empty:
        return None
    
    metrics = {
        'total_loans': len(df),
        'active_loans': len(df[df['loan_status'] != 'Complete']),
        'total_principal': df['disburse_principal'].sum(),
        'outstanding_balance': df['outstanding_balance'].sum(),
        'avg_interest_rate': df['interest_rate'].mean(),
        'current_customers': df['customer_id'].nunique(),
        'collection_rate': (1 - (df['outstanding_balance'].sum() / df['disburse_principal'].sum())) * 100 if df['disburse_principal'].sum() > 0 else 0,
    }
    
    # Delinquency metrics
    metrics['dpd_30_plus'] = len(df[df['dpd'] >= 30])
    metrics['dpd_90_plus'] = len(df[df['dpd'] >= 90])
    metrics['delinquency_rate_30'] = (metrics['dpd_30_plus'] / len(df)) * 100 if len(df) > 0 else 0
    metrics['delinquency_rate_90'] = (metrics['dpd_90_plus'] / len(df)) * 100 if len(df) > 0 else 0
    
    # PAR (Portfolio at Risk) - loans with 90+ DPD
    par_balance = df[df['dpd'] >= 90]['outstanding_balance'].sum()
    metrics['par_90_amount'] = par_balance
    metrics['par_90_ratio'] = (par_balance / metrics['outstanding_balance'] * 100) if metrics['outstanding_balance'] > 0 else 0
    
    return metrics


# --- Main Application ---
st.markdown(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.title("💰 Abaco Loans Analytics - Executive Dashboard")

# Load data
loan_data = load_loan_data()
if loan_data is None:
    st.stop()

metrics = calculate_portfolio_metrics(loan_data)

# --- 1. PORTFOLIO OVERVIEW ---
st.header("📊 Portfolio Overview")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Loans", f"{metrics['total_loans']:,}", help="Total number of loans in portfolio")
col2.metric("Active Loans", f"{metrics['active_loans']:,}", help="Number of currently active loans")
col3.metric("Unique Customers", f"{metrics['current_customers']:,}", help="Total unique customers")
col4.metric("Total Principal", f"${metrics['total_principal']:,.0f}", help="Total disbursed amount")
col5.metric("Outstanding Balance", f"${metrics['outstanding_balance']:,.0f}", help="Current balance due")

# --- 2. FINANCIAL METRICS ---
st.header("💵 Financial Metrics")
fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
fin_col1.metric("Collection Rate", f"{metrics['collection_rate']:.1f}%", help="% of principal collected")
fin_col2.metric("Avg Interest Rate", f"{metrics['avg_interest_rate']:.2%}", help="Average interest rate across portfolio")
fin_col3.metric("Outstanding Balance", f"${metrics['outstanding_balance']/1_000_000:.2f}M", help="Total balance remaining")
fin_col4.metric("Average Loan Size", f"${metrics['total_principal']/metrics['total_loans']:,.0f}", help="Average disbursed amount per loan")

# --- 3. RISK INDICATORS ---
st.header("⚠️ Risk Indicators (KRI)")
risk_col1, risk_col2, risk_col3, risk_col4 = st.columns(4)
risk_col1.metric("30+ Delinquency Rate", f"{metrics['delinquency_rate_30']:.2f}%", help="% of loans with 30+ DPD")
risk_col2.metric("90+ Delinquency Rate", f"{metrics['delinquency_rate_90']:.2f}%", help="% of loans with 90+ DPD")
risk_col3.metric("PAR 90 Ratio", f"{metrics['par_90_ratio']:.2f}%", help="% of balance at risk (90+ DPD)")
risk_col4.metric("PAR 90 Amount", f"${metrics['par_90_amount']:,.0f}", help="Total balance at risk")

# --- 4. SEGMENT ANALYSIS ---
st.header("📈 Commercial Analysis - By Product")
if 'product_type' in loan_data.columns:
    product_analysis = loan_data.groupby('product_type').agg({
        'loan_id': 'count',
        'disburse_principal': 'sum',
        'outstanding_balance': 'sum',
        'dpd': lambda x: (x >= 90).sum()
    }).rename(columns={
        'loan_id': 'Count',
        'disburse_principal': 'Total Principal',
        'outstanding_balance': 'Outstanding',
        'dpd': 'PAR 90 Count'
    })
    product_analysis['Collection %'] = ((product_analysis['Total Principal'] - product_analysis['Outstanding']) / product_analysis['Total Principal'] * 100).round(2)
    st.dataframe(product_analysis.style.format(lambda x: f"{x:,.0f}" if x > 100 else f"{x:.2f}"))
    
    # Product distribution chart
    product_chart = alt.Chart(loan_data.groupby('product_type').size().reset_index(name='count')).mark_bar().encode(
        x=alt.X('product_type:N', title='Product Type'),
        y=alt.Y('count:Q', title='Number of Loans'),
        tooltip=['product_type', 'count']
    ).properties(title='Loan Count by Product Type', height=300)
    st.altair_chart(product_chart, use_container_width=True)

# --- 5. DPD DISTRIBUTION ---
st.header("📉 Delinquency Distribution (DPD Buckets)")
dpd_bins = [0, 1, 30, 60, 90, 1000]
dpd_labels = ['Current', '1-30 DPD', '31-60 DPD', '61-90 DPD', '90+ DPD']
loan_data['dpd_bucket'] = pd.cut(loan_data['dpd'], bins=dpd_bins, labels=dpd_labels, right=True)

dpd_dist = loan_data['dpd_bucket'].value_counts().sort_index()
dpd_chart = alt.Chart(dpd_dist.reset_index()).mark_bar(color='steelblue').encode(
    x=alt.X('dpd_bucket:N', title='DPD Bucket', sort=dpd_labels),
    y=alt.Y('count:Q', title='Number of Loans'),
    tooltip=['dpd_bucket', 'count']
).properties(title='Loan Distribution by Days Past Due', height=300)
st.altair_chart(dpd_chart, use_container_width=True)

# --- 6. GEOGRAPHIC ANALYSIS ---
st.header("🗺️ Geographic Analysis")
if 'location_state_province' in loan_data.columns:
    geo_dist = loan_data['location_state_province'].value_counts().head(10).reset_index(name='count')
    geo_dist.columns = ['location', 'count']
    geo_chart = alt.Chart(geo_dist).mark_barh().encode(
        y=alt.Y('location:N', sort='-x', title='Location'),
        x=alt.X('count:Q', title='Number of Loans'),
        tooltip=['location', 'count']
    ).properties(title='Top 10 Locations by Loan Count', height=300)
    st.altair_chart(geo_chart, use_container_width=True)

# --- 7. LOAN STATUS BREAKDOWN ---
st.header("📋 Loan Status Summary")
if 'loan_status' in loan_data.columns:
    status_dist = loan_data['loan_status'].value_counts()
    status_chart = alt.Chart(status_dist.reset_index()).mark_arc().encode(
        theta=alt.Theta('count:Q'),
        color=alt.Color('loan_status:N', title='Status'),
        tooltip=['loan_status', 'count']
    ).properties(title='Loan Status Distribution', height=400)
    st.altair_chart(status_chart, use_container_width=True)
    
    # Status table
    st.subheader("Status Details")
    status_detail = loan_data.groupby('loan_status').agg({
        'loan_id': 'count',
        'disburse_principal': 'sum',
        'outstanding_balance': 'sum'
    }).rename(columns={'loan_id': 'Count', 'disburse_principal': 'Total Principal', 'outstanding_balance': 'Outstanding'})
    st.dataframe(status_detail.style.format(lambda x: f"{x:,.0f}"))

# --- 8. DETAILED DATA TABLE ---
st.header("📊 Detailed Loan Portfolio Data")
st.subheader("View & Export")
cols_to_display = ['loan_id', 'customer_id', 'product_type', 'disburse_principal', 'outstanding_balance', 'dpd', 'loan_status', 'interest_rate', 'location_state_province']
display_df = loan_data[[col for col in cols_to_display if col in loan_data.columns]].head(100)
st.dataframe(display_df, use_container_width=True)

st.caption(f"Showing first 100 of {len(loan_data):,} loans. Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
