"""Utility functions for common loan analytics KPIs."""
from typing import Dict, Iterable

import numpy as np
import pandas as pd

REQUIRED_KPI_COLUMNS = [
    "loan_amount",
    "appraised_value",
    "borrower_income",
    "monthly_debt",
    "loan_status",
    "interest_rate",
    "principal_balance",
]

DELINQUENT_STATUSES = ["30-59 days past due", "60-89 days past due", "90+ days past due"]


def validate_kpi_columns(loan_data: pd.DataFrame) -> None:
    """Validate that all KPI columns exist in the provided dataframe."""
    missing_cols = [col for col in REQUIRED_KPI_COLUMNS if col not in loan_data.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in loan_data: {', '.join(missing_cols)}")


def loan_to_value(loan_amounts: pd.Series, appraised_values: pd.Series) -> pd.Series:
    """Compute LTV as a percentage while avoiding division by zero."""
    safe_appraised = appraised_values.replace(0, np.nan)
    return (loan_amounts / safe_appraised) * 100


def debt_to_income_ratio(monthly_debts: pd.Series, borrower_incomes: pd.Series) -> pd.Series:
    """Compute DTI as a percentage using monthly income with zero-income safeguards."""
    monthly_income = borrower_incomes / 12
    safe_income = monthly_income.replace({0: np.nan})
    return (monthly_debts / safe_income) * 100


def portfolio_delinquency_rate(statuses: Iterable[str]) -> float:
    """Return the delinquency rate as a percentage of total rows."""
    series = pd.Series(list(statuses))
    delinquent_count = series.isin(DELINQUENT_STATUSES).sum()
    total = len(series)
    return (delinquent_count / total) * 100 if total else 0.0


def weighted_portfolio_yield(interest_rates: pd.Series, principal_balances: pd.Series) -> float:
    """Calculate weighted yield, returning zero when principal is missing or zero."""
    total_principal = principal_balances.sum()
    if total_principal == 0:
        return 0.0
    weighted_interest = (interest_rates * principal_balances).sum()
    return (weighted_interest / total_principal) * 100


def portfolio_kpis(loan_data: pd.DataFrame) -> Dict[str, float]:
    """Aggregate portfolio KPIs used across analytics modules."""
    validate_kpi_columns(loan_data)

    ltv_series = (
        loan_data["ltv_ratio"]
        if "ltv_ratio" in loan_data.columns
        else loan_to_value(loan_data["loan_amount"], loan_data["appraised_value"])
    )
    dti_series = (
        loan_data["dti_ratio"]
        if "dti_ratio" in loan_data.columns
        else debt_to_income_ratio(loan_data["monthly_debt"], loan_data["borrower_income"])
    )

    return {
        "portfolio_delinquency_rate_percent": portfolio_delinquency_rate(
            loan_data["loan_status"]
        ),
        "portfolio_yield_percent": weighted_portfolio_yield(
            loan_data["interest_rate"], loan_data["principal_balance"]
        ),
        "average_ltv_ratio_percent": float(ltv_series.mean()),
        "average_dti_ratio_percent": float(dti_series.mean()),
    }
