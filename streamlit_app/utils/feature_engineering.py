"""Feature engineering utilities for customer analytics."""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


class FeatureEngineer:
    CUSTOMER_TYPES = {
        "corporate": ["S.A.", "SAC", "LLC", "INC"],
        "individual": ["SRL", "E.I.R.L", "PERSONAL"],
    }
    SEGMENTATION_THRESHOLDS = {
        "platinum": 1_000_000,
        "gold": 500_000,
        "silver": 100_000,
    }
    DPD_BUCKETS = [0, 30, 60, 90, np.inf]
    DPD_LABELS = ["Current", "30", "60", "90+"]

    @classmethod
    def classify_customer_type(cls, customer_name: str, customer_data: Dict) -> str:
        name_upper = customer_name.upper()
        for segment, tokens in cls.CUSTOMER_TYPES.items():
            if any(token in name_upper for token in tokens):
                return segment
        return customer_data.get("segment", "micro")

    @classmethod
    def calculate_segmentation(cls, customer_metrics: Dict) -> str:
        revenue = customer_metrics.get("revenue", 0)
        return next(
            (
                segment
                for segment, threshold in cls.SEGMENTATION_THRESHOLDS.items()
                if revenue >= threshold
            ),
            "starter",
        )

    @classmethod
    def bucket_dpd(cls, dpd_value: float) -> str:
        return pd.cut([dpd_value], bins=cls.DPD_BUCKETS, labels=cls.DPD_LABELS, right=False)[0]

    @classmethod
    def calculate_dpd_statistics(cls, dpd_series: pd.Series) -> Dict:
        buckets = pd.cut(dpd_series, bins=cls.DPD_BUCKETS, labels=cls.DPD_LABELS, right=False)
        distribution = buckets.value_counts(normalize=True).sort_index()
        return distribution.to_dict()

    @staticmethod
    def calculate_utilization(balance: float, limit: float) -> float:
        return 0.0 if limit == 0 else balance / limit

    @staticmethod
    def calculate_weighted_apr(facilities: List[Dict]) -> float:
        if not facilities:
            return 0.0
        total_balance = sum(item.get("balance", 0) for item in facilities)
        if total_balance == 0:
            return 0.0
        weighted_apr = sum(item.get("apr", 0) * item.get("balance", 0) for item in facilities) / total_balance
        return round(weighted_apr, 4)

    @staticmethod
    def calculate_z_scores(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
        z_scored = df.copy()
        for metric in metrics:
            if metric not in z_scored:
                continue
            mean = z_scored[metric].mean()
            std = z_scored[metric].std() or 1
            z_scored[f"{metric}_zscore"] = (z_scored[metric] - mean) / std
        return z_scored

    @classmethod
    def enrich_portfolio(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Derive portfolio features for downstream analytics dashboards.

        The enrichment adds utilization, DPD bucket, and revenue-based
        segmentation to support metrics, tables, and data quality checks
        without mutating the original dataset.
        """

        enriched = df.copy()
        if {"balance", "limit"}.issubset(enriched.columns):
            enriched["utilization"] = enriched.apply(
                lambda row: cls.calculate_utilization(row.get("balance", 0), row.get("limit", 0)), axis=1
            )

        if "dpd" in enriched.columns:
            enriched["dpd_bucket"] = enriched["dpd"].apply(cls.bucket_dpd)

        enriched["segment"] = enriched.apply(
            lambda row: cls.calculate_segmentation({"revenue": row.get("revenue", 0)}), axis=1
        )
        return enriched
