import json
import os
from pathlib import Path
from math import isclose

import pandas as pd
import psycopg
import pytest


DB_DSN = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
JSON_PATH = Path("exports/complete_kpi_dashboard.json")

ABS_TOL = 1e-6
REL_TOL = 1e-4


def _load_extended_kpis():
    print(f"\n[DEBUG] Loading JSON from {JSON_PATH.absolute()}")
    if not JSON_PATH.exists():
        pytest.skip(f"JSON export not found at {JSON_PATH}")
    with JSON_PATH.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    extended = obj.get("extended_kpis") or obj
    if "monthly_risk" in extended:
        print(f"[DEBUG] first monthly_risk total_outstanding: {extended['monthly_risk'][0].get('total_outstanding')}")
    return extended


def _df_from_list(records, date_col="year_month"):
    df = pd.DataFrame(records)
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col])
    return df


def _assert_series_almost_equal(left, right, cols, ctx=""):
    for col in cols:
        assert col in left.columns, f"{ctx}: column '{col}' missing on left"
        assert col in right.columns, f"{ctx}: column '{col}' missing on right"
        for i, (lv, rv) in enumerate(zip(left[col], right[col])):
            if pd.isna(lv) and pd.isna(rv):
                continue
            assert isclose(
                float(lv),
                float(rv),
                rel_tol=REL_TOL,
                abs_tol=ABS_TOL,
            ), f"{ctx}: mismatch in column '{col}' at row {i}: left={lv}, right={rv}"


def _query_df(sql: str) -> pd.DataFrame:
    with psycopg.connect(DB_DSN) as conn:
        return pd.read_sql(sql, conn)


def test_monthly_pricing_parity():
    extended = _load_extended_kpis()
    py_records = extended.get("monthly_pricing")
    assert py_records is not None, "extended_kpis.monthly_pricing not found in JSON"

    df_py = _df_from_list(py_records).sort_values("year_month").reset_index(drop=True)

    df_sql = _query_df(
        """
        SELECT
          year_month,
          weighted_apr,
          weighted_fee_rate,
          weighted_other_income_rate,
          weighted_effective_rate
        FROM analytics.kpi_monthly_pricing
        ORDER BY year_month
        """
    )
    df_sql["year_month"] = pd.to_datetime(df_sql["year_month"]).dt.normalize()
    df_sql = df_sql.reset_index(drop=True)

    common_months = sorted(set(df_py["year_month"]) & set(df_sql["year_month"]))
    assert common_months, "No overlapping year_month between Python and SQL for pricing"

    df_py_aligned = df_py[df_py["year_month"].isin(common_months)].sort_values("year_month").reset_index(drop=True)
    df_sql_aligned = df_sql[df_sql["year_month"].isin(common_months)].sort_values("year_month").reset_index(drop=True)

    assert len(df_py_aligned) == len(df_sql_aligned), "Row count mismatch in pricing parity"

    _assert_series_almost_equal(
        df_py_aligned,
        df_sql_aligned,
        cols=[
            "weighted_apr",
            "weighted_fee_rate",
            "weighted_other_income_rate",
            "weighted_effective_rate",
        ],
        ctx="kpi_monthly_pricing",
    )


def test_monthly_risk_parity():
    extended = _load_extended_kpis()
    py_records = extended.get("monthly_risk")
    assert py_records is not None, "extended_kpis.monthly_risk not found in JSON"

    df_py = _df_from_list(py_records).sort_values("year_month").reset_index(drop=True)

    df_sql = _query_df(
        """
        SELECT
          year_month,
          total_outstanding,
          dpd7_amount,
          dpd7_pct,
          dpd15_amount,
          dpd15_pct,
          dpd30_amount,
          dpd30_pct,
          dpd60_amount,
          dpd60_pct,
          dpd90_amount,
          default_pct
        FROM analytics.kpi_monthly_risk
        ORDER BY year_month
        """
    )
    df_sql["year_month"] = pd.to_datetime(df_sql["year_month"]).dt.normalize()
    df_sql = df_sql.reset_index(drop=True)

    common_months = sorted(set(df_py["year_month"]) & set(df_sql["year_month"]))
    assert common_months, "No overlapping year_month between Python and SQL for risk"

    df_py_aligned = df_py[df_py["year_month"].isin(common_months)].sort_values("year_month").reset_index(drop=True)
    df_sql_aligned = df_sql[df_sql["year_month"].isin(common_months)].sort_values("year_month").reset_index(drop=True)

    assert len(df_py_aligned) == len(df_sql_aligned), "Row count mismatch in risk parity"

    _assert_series_almost_equal(
        df_py_aligned,
        df_sql_aligned,
        cols=[
            "total_outstanding",
            "dpd7_amount",
            "dpd7_pct",
            "dpd15_amount",
            "dpd15_pct",
            "dpd30_amount",
            "dpd30_pct",
            "dpd60_amount",
            "dpd60_pct",
            "dpd90_amount",
            "default_pct",
        ],
        ctx="kpi_monthly_risk",
    )


def test_customer_types_parity():
    extended = _load_extended_kpis()
    py_records = extended.get("customer_types")
    assert py_records is not None, "extended_kpis.customer_types not found in JSON"

    df_py = _df_from_list(py_records).sort_values(["year_month", "customer_type"]).reset_index(drop=True)

    df_sql = _query_df(
        """
        SELECT
          year_month,
          customer_type,
          unique_customers,
          disbursement_amount
        FROM analytics.kpi_customer_types
        ORDER BY year_month, customer_type
        """
    )
    df_sql["year_month"] = pd.to_datetime(df_sql["year_month"]).dt.normalize()
    df_sql = df_sql.sort_values(["year_month", "customer_type"]).reset_index(drop=True)

    key_cols = ["year_month", "customer_type"]
    merged = df_py.merge(
        df_sql,
        on=key_cols,
        suffixes=("_py", "_sql"),
        how="inner",
    )

    assert not merged.empty, "No overlapping (year_month, customer_type) between Python and SQL"

    for col in ["unique_customers", "disbursement_amount"]:
        col_py = f"{col}_py"
        col_sql = f"{col}_sql"
        for i, (lv, rv) in enumerate(zip(merged[col_py], merged[col_sql])):
            if pd.isna(lv) and pd.isna(rv):
                continue
            assert isclose(
                float(lv),
                float(rv),
                rel_tol=REL_TOL,
                abs_tol=ABS_TOL,
            ), f"kpi_customer_types: mismatch in column '{col}' at row {i}: left={lv}, right={rv}"

