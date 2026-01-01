import numpy as np
import pandas as pd

from apps.analytics.src.enterprise_analytics_engine import LoanAnalyticsEngine
from python.pipeline.data_validation import (
    REQUIRED_ANALYTICS_COLUMNS,
    safe_numeric,
    validate_dataframe,
)
from .quality_score import calculate_quality_score as calculate_portfolio_quality_score

# Alias for backward compatibility
standardize_numeric = safe_numeric

def calculate_quality_score(df: pd.DataFrame) -> float:
    """
    Calculate data quality score based on completeness (non-null values).
    Returns a score between 0 and 100.
    """
    if df.empty:
        return 0.0

    total_cells = df.size
    if total_cells == 0:
        return 0.0

    non_null_cells = df.count().sum()
    return (non_null_cells / total_cells) * 100.0


def project_growth(
    current_yield: float,
    target_yield: float,
    current_loan_volume: float,
    target_loan_volume: float,
    periods: int = 6,
) -> pd.DataFrame:
    """
    Generate a linear projection for yield and loan volume growth.
    """
    if periods < 2:
        raise ValueError("periods must be at least 2")

    dates = pd.date_range(start=pd.Timestamp.now(), periods=periods, freq="MS")

    yields = np.linspace(current_yield, target_yield, periods)
    volumes = np.linspace(current_loan_volume, target_loan_volume, periods)

    return pd.DataFrame({
        "date": dates,
        "yield": yields,
        "loan_volume": volumes
    })


from python.kpi_engine_v2 import KPIEngineV2

REQUIRED_ANALYTICS_COLUMNS = [
    "loan_amount",
    "appraised_value",
    "borrower_income",
    "monthly_debt",
    "interest_rate",
    "principal_balance",
]


def portfolio_kpis(df: pd.DataFrame) -> tuple[dict[str, float], pd.DataFrame]:
    """
    Calculate portfolio-level KPIs and enrich DataFrame with ratios using KPIEngineV2.
    """
    enriched = df.copy()
    metrics = {
        "delinquency_rate": 0.0,
        "portfolio_yield": 0.0,
        "average_ltv": 0.0,
        "average_dti": 0.0,
    }

    if enriched.empty:
        return metrics, enriched

    validate_dataframe(enriched, required_columns=REQUIRED_ANALYTICS_COLUMNS)

    # Use KPIEngineV2 for centralized, standardized calculations
    engine = KPIEngineV2(enriched, actor="portfolio_kpis_util")
    results = engine.calculate_all()

    # Get standardized KPIs from results
    metrics["delinquency_rate"] = results.get("PAR30", {}).get("value", 0.0)
    metrics["portfolio_yield"] = results.get("PortfolioYield", {}).get("value", 0.0)
    metrics["average_ltv"] = results.get("LTV", {}).get("value", 0.0)
    metrics["average_dti"] = results.get("DTI", {}).get("value", 0.0)

    # Enrich DataFrame with calculated ratios
    # Note: We calculate these specifically for enrichment as calculate_all returns scalars
    _, ltv_ctx = engine.calculate_ltv()
    _, dti_ctx = engine.calculate_dti()

    # Recalculate series for enrichment (Engine V2 returns averages, but utility expects series)
    enriched["ltv_ratio"] = np.where(
        enriched["appraised_value"] > 0,
        (enriched["loan_amount"] / enriched["appraised_value"]) * 100.0,
        np.nan
    )
    enriched["dti_ratio"] = np.where(
        enriched["borrower_income"] > 0,
        (enriched["monthly_debt"] / (enriched["borrower_income"] / 12.0)) * 100.0,
        np.nan
    )

    # Fill NaNs in metrics
    for k in metrics:
        if metrics[k] is None or pd.isna(metrics[k]):
            metrics[k] = 0.0

    return metrics, enriched

__all__ = [
    "calculate_quality_score",
    "calculate_portfolio_quality_score",
    "project_growth",
    "portfolio_kpis",
    "standardize_numeric",
]
