from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class LoanAnalyticsConfig:
    """Static configuration controlling portfolio KPI computations."""

    arrears_threshold: int = 90
    currency: str = "USD"
    numeric_missing_fill_value: float | None = None


class LoanAnalyticsEngine:
    """Compute portfolio KPIs, risk metrics, and cashflow views for loan books."""

    required_columns: Sequence[str] = (
        "loan_id",
        "principal",
        "interest_rate",
        "term_months",
        "origination_date",
        "status",
        "outstanding_principal",
        "days_in_arrears",
        "charge_off_amount",
        "recoveries",
        "paid_principal",
    )

    def __init__(self, data: pd.DataFrame, config: LoanAnalyticsConfig | None = None):
        self.config = config or LoanAnalyticsConfig()
        self.data = self._prepare_data(data.copy())

    @classmethod
    def from_csv(cls, path: str, config: LoanAnalyticsConfig | None = None) -> "LoanAnalyticsEngine":
        frame = pd.read_csv(path)
        return cls(frame, config=config)

    def _prepare_data(self, frame: pd.DataFrame) -> pd.DataFrame:
        missing = [col for col in self.required_columns if col not in frame.columns]
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        frame["origination_date"] = pd.to_datetime(
            frame["origination_date"], format="%Y-%m-%d", errors="coerce"
        )
        if frame["origination_date"].isna().any():
            raise ValueError("origination_date contains invalid or missing values")
        numeric_cols: Iterable[str] = [
            "principal",
            "interest_rate",
            "term_months",
            "outstanding_principal",
            "days_in_arrears",
            "charge_off_amount",
            "recoveries",
            "paid_principal",
        ]
        for col in numeric_cols:
            coerced = pd.to_numeric(frame[col], errors="coerce")
            invalid_mask = frame[col].notna() & coerced.isna()
            if invalid_mask.any():
                bad_values = frame.loc[invalid_mask, col].unique()
                raise ValueError(f"Column '{col}' contains non-numeric values: {bad_values.tolist()}")
            missing_mask = frame[col].isna() & coerced.isna()
            if missing_mask.any() and self.config.numeric_missing_fill_value is None:
                raise ValueError(
                    f"Column '{col}' contains missing numeric values; "
                    "set numeric_missing_fill_value to fill explicitly"
                )
            frame[col] = coerced.fillna(self.config.numeric_missing_fill_value or 0)

        frame["status"] = frame["status"].fillna("").astype(str)
        frame["arrears_flag"] = (
            (frame["days_in_arrears"] >= self.config.arrears_threshold)
            | frame["status"].str.lower().eq("defaulted")
        )
        frame["origination_quarter"] = frame["origination_date"].dt.to_period("Q")
        frame["exposure_at_default"] = frame[["outstanding_principal", "charge_off_amount"]].max(axis=1)
        return frame

    def portfolio_kpis(self) -> dict:
        portfolio = self.data
        return self._portfolio_kpis_from_prepared(portfolio)

    def _portfolio_kpis_from_prepared(self, portfolio: pd.DataFrame) -> dict:
        total_outstanding = portfolio["outstanding_principal"].sum()
        total_principal = portfolio["principal"].sum()

        if total_outstanding > 0:
            weighted_rate = np.average(
                portfolio["interest_rate"], weights=portfolio["outstanding_principal"]
            )
        elif total_principal > 0:
            weighted_rate = np.average(portfolio["interest_rate"], weights=portfolio["principal"])
        else:
            weighted_rate = float("nan")

        default_mask = portfolio["status"].str.lower().eq("defaulted")
        defaults = portfolio[default_mask]
        npl_outstanding = portfolio.loc[portfolio["arrears_flag"], "outstanding_principal"].sum()
        npl_ratio = npl_outstanding / total_outstanding if total_outstanding else float("nan")
        default_rate = len(defaults) / len(portfolio) if len(portfolio) else float("nan")

        lgd = self._loss_given_default(defaults)
        prepayment_rate = (
            portfolio["paid_principal"].sum() / total_principal if total_principal else float("nan")
        )
        repayment_velocity = self._repayment_velocity(portfolio)

        return {
            "currency": self.config.currency,
            "total_outstanding": total_outstanding,
            "total_principal": total_principal,
            "weighted_interest_rate": weighted_rate,
            "non_performing_loan_ratio": npl_ratio,
            "default_rate": default_rate,
            "loss_given_default": lgd,
            "prepayment_rate": prepayment_rate,
            "repayment_velocity": repayment_velocity,
        }

    def _loss_given_default(self, defaults: pd.DataFrame) -> float:
        exposure = defaults["exposure_at_default"].sum()
        if not exposure:
            return float("nan")
        losses = (defaults["charge_off_amount"] - defaults["recoveries"]).clip(lower=0).sum()
        return losses / exposure

    def _repayment_velocity(self, portfolio: pd.DataFrame) -> float:
        active_terms = portfolio["term_months"].replace(0, np.nan)
        scheduled_principal = portfolio["principal"] / active_terms
        scheduled_principal = scheduled_principal.replace([np.inf, -np.inf], np.nan).fillna(0)
        scheduled_total = scheduled_principal.sum()
        if not scheduled_total:
            return float("nan")
        return portfolio["paid_principal"].sum() / scheduled_total

    def segment_kpis(self, segment_by: List[str]) -> pd.DataFrame:
        if not segment_by:
            raise ValueError("segment_by must contain at least one column")
        missing = [col for col in segment_by if col not in self.data.columns]
        if missing:
            raise ValueError(f"Segment columns not found: {', '.join(missing)}")

        grouped = self.data.groupby(segment_by)
        rows = []
        for keys, frame in grouped:
            metrics = self._portfolio_kpis_from_prepared(frame)
            if not isinstance(keys, tuple):
                keys = (keys,)
            rows.append({**dict(zip(segment_by, keys)), **metrics})
        return pd.DataFrame(rows)

    def vintage_default_table(self) -> pd.DataFrame:
        grouped = self.data.groupby("origination_quarter")
        rows = []
        for vintage, frame in grouped:
            if not len(frame):
                continue
            defaults = frame[frame["status"].str.lower().eq("defaulted")]
            rate = len(defaults) / len(frame) if len(frame) else float("nan")
            coverage = frame["principal"].sum()
            rows.append({
                "origination_quarter": vintage,
                "default_rate": rate,
                "principal_at_origination": coverage,
            })
        return pd.DataFrame(rows).sort_values("origination_quarter").reset_index(drop=True)

    def cashflow_curve(self, freq: str = "M") -> pd.DataFrame:
        expanded = self.data.copy()
        expanded["period"] = expanded["origination_date"].dt.to_period(freq)
        grouped = expanded.groupby("period")
        curve = grouped.agg(
            principal_funded=("principal", "sum"),
            principal_repaid=("paid_principal", "sum"),
            outstanding=("outstanding_principal", "sum"),
        )
        curve["net_cashflow"] = curve["principal_repaid"] - curve["principal_funded"]
        curve["cumulative_cashflow"] = curve["net_cashflow"].cumsum()
        return curve.reset_index()

    def scorecard(self) -> pd.DataFrame:
        kpis = self.portfolio_kpis()
        return pd.DataFrame(
            {
                "metric": list(kpis.keys()),
                "value": list(kpis.values()),
            }
        )
