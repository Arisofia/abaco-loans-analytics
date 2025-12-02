"""Abaco Enterprise Analytics Engine v2.1.0.
Risk and growth KPIs with audit-grade traceability.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, Sequence

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("AbacoRiskEngine")


class DataValidationError(Exception):
    """Raised when input data violates expected schema or quality thresholds."""


@dataclass(frozen=True)
class PortfolioReport:
    timestamp_utc: str
    portfolio_delinquency_rate_percent: float
    portfolio_yield_percent: float
    average_ltv_ratio_percent: float
    average_dti_ratio_percent: float
    total_exposure: float

    def as_dict(self) -> Dict[str, float]:
        return asdict(self)


class LoanAnalyticsEngine:
    """Stateless engine for portfolio KPIs with defensive validation."""

    REQUIRED_COLUMNS = {
        "loan_amount",
        "appraised_value",
        "borrower_income",
        "monthly_debt",
        "loan_status",
        "interest_rate",
        "principal_balance",
    }

    NUMERIC_COLUMNS = {
        "loan_amount",
        "appraised_value",
        "borrower_income",
        "monthly_debt",
        "interest_rate",
        "principal_balance",
    }

    def __init__(self, loan_data: pd.DataFrame):
        if not isinstance(loan_data, pd.DataFrame) or loan_data.empty:
            logger.error("Initialization failed: empty or non-DataFrame input.")
            raise DataValidationError("Input must be a non-empty pandas DataFrame.")

        self.timestamp = datetime.now(timezone.utc)
        self.loan_data = loan_data.copy()
        self._validate_schema()
        self._coerce_numeric()
        self._sanitize_data()
        self._validate_non_negative(["loan_amount", "appraised_value", "borrower_income", "principal_balance"])
        logger.info("Engine initialized with %s records.", len(self.loan_data))

    def _coerce_numeric(self) -> None:
        for column in self.NUMERIC_COLUMNS:
            coerced = pd.to_numeric(self.loan_data[column], errors="coerce")
            if coerced.isna().any():
                logger.error("Non-numeric or invalid values detected in %s.", column)
                raise DataValidationError(f"Invalid numeric values found in {column}")
            self.loan_data[column] = coerced.astype(float)

    def _validate_schema(self) -> None:
        missing = self.REQUIRED_COLUMNS - set(self.loan_data.columns)
        if missing:
            logger.critical("Schema violation: missing columns %s", sorted(missing))
            raise DataValidationError(f"Missing required columns: {', '.join(sorted(missing))}")

    def _sanitize_data(self) -> None:
        numeric_cols = self.loan_data.select_dtypes(include=[np.number]).columns
        if np.isinf(self.loan_data[numeric_cols]).any().any():
            logger.warning("Infinite values detected; replacing with NaN for safe calculations.")
            self.loan_data.replace([np.inf, -np.inf], np.nan, inplace=True)
        if self.loan_data[numeric_cols].isna().any().any():
            logger.warning("Null numeric values detected; coercing to zero for conservative KPIs.")
            self.loan_data[numeric_cols] = self.loan_data[numeric_cols].fillna(0.0)

    def _validate_non_negative(self, columns: Sequence[str]) -> None:
        for column in columns:
            if (self.loan_data[column] < 0).any():
                logger.error("Negative values detected in %s; aborting.", column)
                raise DataValidationError(f"Negative values found in {column}")

    def compute_loan_to_value(self) -> pd.Series:
        safe_appraised_value = self.loan_data["appraised_value"].replace(0, np.nan)
        ltv = (self.loan_data["loan_amount"] / safe_appraised_value) * 100
        logger.info(
            "LTV computed | mean=%.2f%% max=%.2f%%",
            float(ltv.mean(skipna=True)),
            float(ltv.max(skipna=True)),
        )
        return ltv.fillna(0.0).astype(float).round(2)

    def compute_debt_to_income(self) -> pd.Series:
        monthly_income = self.loan_data["borrower_income"] / 12
        dti = np.where(
            monthly_income > 0,
            (self.loan_data["monthly_debt"] / monthly_income) * 100,
            0.0,
        )
        logger.info("DTI computed | mean=%.2f%%", float(np.mean(dti)))
        return pd.Series(dti, dtype=float).round(2)

    def compute_delinquency_rate(self) -> float:
        delinquent_statuses = ["30-59 days past due", "60-89 days past due", "90+ days past due"]
        delinquent_count = self.loan_data["loan_status"].isin(delinquent_statuses).sum()
        total_loans = len(self.loan_data)
        rate = (delinquent_count / total_loans) * 100 if total_loans else 0.0
        if rate > 5.0:
            logger.warning("Delinquency rate %.2f%% exceeds threshold.", rate)
        return float(round(rate, 2))

    def compute_portfolio_yield(self) -> float:
        total_principal = float(self.loan_data["principal_balance"].sum())
        if total_principal == 0:
            return 0.0
        weighted_interest = float((self.loan_data["interest_rate"] * self.loan_data["principal_balance"]).sum())
        return float(round((weighted_interest / total_principal) * 100, 2))

    def run_full_analysis(self) -> Dict[str, float]:
        logger.info("Starting full portfolio analysis cycle.")
        self.loan_data["ltv_ratio"] = self.compute_loan_to_value()
        self.loan_data["dti_ratio"] = self.compute_debt_to_income()
        report = PortfolioReport(
            timestamp_utc=self.timestamp.isoformat(),
            portfolio_delinquency_rate_percent=self.compute_delinquency_rate(),
            portfolio_yield_percent=self.compute_portfolio_yield(),
            average_ltv_ratio_percent=float(round(self.loan_data["ltv_ratio"].mean(), 2)),
            average_dti_ratio_percent=float(round(self.loan_data["dti_ratio"].mean(), 2)),
            total_exposure=float(round(self.loan_data["principal_balance"].sum(), 2)),
        )
        logger.info("Analysis complete. KPIs ready for downstream dashboards.")
        return report.as_dict()


if __name__ == "__main__":
    sample = {
        "loan_amount": [250000, 450000, 150000, 600000, 0],
        "appraised_value": [300000, 500000, 160000, 750000, 0],
        "borrower_income": [80000, 120000, 60000, 150000, 50000],
        "monthly_debt": [1500, 2500, 1000, 3000, 500],
        "loan_status": ["current", "30-59 days past due", "current", "current", "90+ days past due"],
        "interest_rate": [0.035, 0.042, 0.038, 0.045, 0.060],
        "principal_balance": [240000, 440000, 145000, 590000, 10000],
    }
    frame = pd.DataFrame(sample)
    engine = LoanAnalyticsEngine(frame)
    dashboard = engine.run_full_analysis()

    print("\n--- Fintech Factory Dashboard ---")
    for key, val in dashboard.items():
        print(f"{key}: {val}")
    print("--------------------------------\n")
