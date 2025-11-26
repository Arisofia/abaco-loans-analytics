"""Tests for portfolio feature engineering utilities."""
from __future__ import annotations

import pandas as pd

from streamlit_app.utils.feature_engineering import FeatureEngineer


def test_enrich_portfolio_adds_features():
    df = pd.DataFrame(
        [
            {"customer": "Acme", "balance": 100000, "limit": 200000, "dpd": 15, "revenue": 750000},
            {"customer": "Nova", "balance": 50000, "limit": 50000, "dpd": 95, "revenue": 90000},
        ]
    )

    enriched = FeatureEngineer.enrich_portfolio(df)

    assert {"utilization", "dpd_bucket", "segment"}.issubset(enriched.columns)
    assert enriched.loc[0, "segment"] == "gold"
    assert enriched.loc[1, "dpd_bucket"] == "90+"
    assert enriched.loc[1, "utilization"] == 1.0


def test_enrich_portfolio_handles_missing_columns_gracefully():
    df = pd.DataFrame([
        {"customer": "Flux", "revenue": 120000},
    ])

    enriched = FeatureEngineer.enrich_portfolio(df)

    assert "utilization" not in enriched.columns
    assert enriched.loc[0, "segment"] == "silver"
