import pandas as pd
import pytest

from python.pipeline.ingestion import UnifiedIngestion


def test_ingest_csv(tmp_path):
    csv_content = "period,measurement_date,total_receivable_usd,dpd_0_7_usd,dpd_7_30_usd,dpd_30_60_usd,dpd_60_90_usd,dpd_90_plus_usd,total_eligible_usd,discounted_balance_usd,cash_available_usd\n2025Q4,2025-12-01,1000.0,100,100,100,100,100,800,700,500\n2025Q4,2025-12-02,2000.0,200,200,200,200,200,1600,1400,1000"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    df = ingestion.ingest_csv("sample.csv")
    assert not df.empty
    for col in [
        "period",
        "measurement_date",
        "total_receivable_usd",
        "_ingest_run_id",
        "_ingest_timestamp",
    ]:
        assert col in df.columns
    assert hasattr(ingestion, "run_id")
    assert hasattr(ingestion, "timestamp")
    assert isinstance(ingestion.run_id, str)
    assert isinstance(ingestion.timestamp, str)
    assert all(df["_ingest_run_id"] == ingestion.run_id)
    assert all(isinstance(ts, str) for ts in df["_ingest_timestamp"])
    assert isinstance(ingestion.errors, list)
    assert df["total_receivable_usd"].sum() == pytest.approx(3000.0)


def test_ingest_csv_error(tmp_path):
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    df = ingestion.ingest_csv("nonexistent.csv")
    assert df.empty
    assert len(ingestion.errors) == 1
    err = ingestion.errors[0]
    for key in ["file", "error", "timestamp", "run_id"]:
        assert key in err
    assert err["file"] == "nonexistent.csv"
    assert "no such file".lower() in err["error"].lower()


def test_ingest_csv_empty_file(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.touch()
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    df = ingestion.ingest_csv("empty.csv")
    assert df.empty
    assert len(ingestion.errors) == 1
    assert "empty" in ingestion.errors[0]["error"].lower()


def test_ingest_csv_strict_schema_failure(tmp_path):
    csv_content = "period,measurement_date,total_receivable_usd\n2025Q4,2025-12-01,1000.0"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    df = ingestion.ingest_csv("sample.csv")
    assert df.empty  # strict mode aborts on schema issues
    assert ingestion.errors
    err = ingestion.errors[0]
    assert err.get("stage") == "ingestion_validation"
    assert "missing required numeric columns" in err.get("error", "").lower()


def test_validate_loans():
    df = pd.DataFrame(
        {"period": ["2025Q4"], "measurement_date": ["2025-12-01"], "total_receivable_usd": [1000.0]}
    )
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    validated = ingestion.validate_loans(df)
    assert "_validation_passed" in validated.columns
    # With hardened required fields, minimal rows fail validation
    assert bool(validated["_validation_passed"].iloc[0]) is False
    assert isinstance(ingestion.errors, list)
    assert len(ingestion.errors) >= 1


def test_validate_loans_missing_field():
    df = pd.DataFrame({"period": ["2025Q4"], "measurement_date": ["2025-12-01"]})
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    validated = ingestion.validate_loans(df)
    assert "_validation_passed" in validated.columns
    assert bool(validated["_validation_passed"].iloc[0]) is False
    assert isinstance(ingestion.errors, list)
    assert len(ingestion.errors) >= 1
    assert ingestion.errors[0].get("stage") == "validation_schema_assertion"


def test_validate_loans_invalid_numeric():
    df = pd.DataFrame(
        {
            "period": ["2025Q4"],
            "measurement_date": ["2025-12-01"],
            "total_receivable_usd": ["invalid"],
        }
    )
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    validated = ingestion.validate_loans(df)
    assert "_validation_passed" in validated.columns
    assert bool(validated["_validation_passed"].iloc[0]) is False
    assert isinstance(ingestion.errors, list)
    numeric_errors = [
        err for err in ingestion.errors if err.get("stage") == "validation_schema_assertion"
    ]
    assert numeric_errors
    assert any("total_receivable_usd" in err.get("error", "") for err in numeric_errors)


def test_get_ingest_summary():
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    summary = ingestion.get_ingest_summary()
    for key in ["run_id", "timestamp", "total_errors", "errors"]:
        assert key in summary
    assert summary["run_id"] == ingestion.run_id
    assert summary["timestamp"] == ingestion.timestamp
    assert isinstance(summary["total_errors"], int)
    assert isinstance(summary["errors"], list)


def test_update_summary_tracks_counts():
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    ingestion._update_summary(10, "file1.csv")
    ingestion._update_summary(5, "file2.csv")
    ingestion._update_summary(20)  # No filename (e.g. dataframe ingest)

    summary = ingestion.get_ingest_summary()
    assert summary["rows_ingested"] == 35
    assert summary["files"]["file1.csv"] == 10
    assert summary["files"]["file2.csv"] == 5


def test_looker_par_balances_to_loan_tape(tmp_path):
    """Test conversion of Looker PAR balance data to loan tape format."""
    par_csv = """reporting_date,outstanding_balance_usd,par_7_balance_usd,par_30_balance_usd,par_60_balance_usd,par_90_balance_usd
2025-12-01,10000.0,500.0,300.0,200.0,100.0
2025-12-02,15000.0,750.0,450.0,300.0,150.0"""
    csv_file = tmp_path / "par_balances.csv"
    csv_file.write_text(par_csv)
    
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    df = pd.read_csv(csv_file)
    cash_by_date = {}
    result = ingestion._looker_par_balances_to_loan_tape(df, cash_by_date)
    
    # Verify required columns are present
    assert "measurement_date" in result.columns
    assert "total_receivable_usd" in result.columns
    assert "dpd_90_plus_usd" in result.columns
    assert "dpd_60_90_usd" in result.columns
    assert "dpd_30_60_usd" in result.columns
    assert "dpd_7_30_usd" in result.columns
    assert "dpd_0_7_usd" in result.columns
    
    # Verify data correctness for first row
    assert result["total_receivable_usd"].iloc[0] == pytest.approx(10000.0)
    assert result["dpd_90_plus_usd"].iloc[0] == pytest.approx(100.0)
    # PAR columns are cumulative, so dpd_60_90 = par_60 - par_90
    assert result["dpd_60_90_usd"].iloc[0] == pytest.approx(200.0 - 100.0)


def test_looker_dpd_to_loan_tape(tmp_path):
    """Test conversion of Looker DPD-based loan data to loan tape format."""
    dpd_csv = """dpd,outstanding_balance_usd,disburse_date
0,1000.0,2025-01-01
15,500.0,2025-01-02
45,300.0,2025-01-03
75,200.0,2025-01-04
95,100.0,2025-01-05"""
    csv_file = tmp_path / "loans_dpd.csv"
    csv_file.write_text(dpd_csv)
    
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    df = pd.read_csv(csv_file)
    cash_by_date = {}
    result = ingestion._looker_dpd_to_loan_tape(df, cash_by_date)
    
    # Verify DPD bucketing columns are present
    assert "dpd_0_7_usd" in result.columns
    assert "dpd_7_30_usd" in result.columns
    assert "dpd_30_60_usd" in result.columns
    assert "dpd_60_90_usd" in result.columns
    assert "dpd_90_plus_usd" in result.columns
    
    # Verify DPD bucketing logic
    # Row with dpd=0 should go to dpd_0_7_usd
    assert result["dpd_0_7_usd"].iloc[0] == pytest.approx(1000.0)
    # Row with dpd=15 should go to dpd_7_30_usd
    assert result["dpd_7_30_usd"].iloc[1] == pytest.approx(500.0)
    # Row with dpd=45 should go to dpd_30_60_usd
    assert result["dpd_30_60_usd"].iloc[2] == pytest.approx(300.0)
    # Row with dpd=95 should go to dpd_90_plus_usd
    assert result["dpd_90_plus_usd"].iloc[4] == pytest.approx(100.0)


def test_ingest_looker_with_par_balances(tmp_path):
    """Test Looker ingestion with PAR balance data."""
    par_csv = """reporting_date,outstanding_balance_usd,par_7_balance_usd,par_30_balance_usd,par_60_balance_usd,par_90_balance_usd
2025-12-01,10000.0,500.0,300.0,200.0,100.0"""
    loans_file = tmp_path / "par_balances.csv"
    loans_file.write_text(par_csv)
    
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    result = ingestion.ingest_looker(loans_file)
    
    assert isinstance(result.df, pd.DataFrame)
    assert not result.df.empty
    assert "measurement_date" in result.df.columns
    assert "total_receivable_usd" in result.df.columns
    assert result.df["total_receivable_usd"].iloc[0] == pytest.approx(10000.0)


def test_ingest_looker_with_dpd_data(tmp_path):
    """Test Looker ingestion with DPD-based loan data."""
    dpd_csv = """dpd,outstanding_balance_usd
10,1000.0
50,500.0"""
    loans_file = tmp_path / "loans_dpd.csv"
    loans_file.write_text(dpd_csv)
    
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    result = ingestion.ingest_looker(loans_file)
    
    assert isinstance(result.df, pd.DataFrame)
    assert not result.df.empty
    assert "dpd_7_30_usd" in result.df.columns
    assert "dpd_30_60_usd" in result.df.columns
