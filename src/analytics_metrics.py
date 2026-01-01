import json
from pathlib import Path
from typing import Any, Dict, List

# Re-exporting real implementations from python/analytics package
from python.analytics import (
    calculate_quality_score,
    portfolio_kpis,
    project_growth,
    standardize_numeric,
)

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_JSON = ROOT / "exports" / "complete_kpi_dashboard.json"


def load_dashboard_metrics() -> Dict[str, Any]:
    """Load computed KPI dashboard from JSON."""
    if not DASHBOARD_JSON.exists():
        return {}
    with DASHBOARD_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_portfolio_fundamentals() -> Dict[str, Any]:
    """Get portfolio fundamentals from dashboard."""
    data = load_dashboard_metrics()
    return data.get("portfolio_fundamentals", {})


def get_growth_metrics() -> Dict[str, Any]:
    """Get growth metrics from dashboard."""
    data = load_dashboard_metrics()
    return data.get("growth_metrics", {})


def get_monthly_pricing() -> List[Dict[str, Any]]:
    """Get monthly pricing from dashboard."""
    data = load_dashboard_metrics()
    return data.get("extended_kpis", {}).get("monthly_pricing", [])


def get_monthly_risk() -> List[Dict[str, Any]]:
    """Get monthly risk from dashboard."""
    data = load_dashboard_metrics()
    return data.get("extended_kpis", {}).get("monthly_risk", [])


def get_customer_types() -> List[Dict[str, Any]]:
    """Get customer types from dashboard."""
    data = load_dashboard_metrics()
    return data.get("extended_kpis", {}).get("customer_types", [])

__all__ = [
    "calculate_quality_score",
    "portfolio_kpis",
    "project_growth",
    "standardize_numeric",
    "load_dashboard_metrics",
    "get_portfolio_fundamentals",
    "get_growth_metrics",
    "get_monthly_pricing",
    "get_monthly_risk",
    "get_customer_types",
]
