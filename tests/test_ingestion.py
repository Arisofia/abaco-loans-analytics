from pathlib import Path

import pandas as pd
import pytest

from python.pipeline.ingestion import UnifiedIngestion


def test_ingest_csv(tmp_path):
    csv_content = "period,measurement_date,total_receivable_usd,dpd_0_7_usd,dpd_7_30_usd,dpd_30_60_usd,dpd_60_90_usd,dpd_90_plus_usd,total_eligible_usd,discounted_balance_usd,cash_available_usd\n2025Q4,2025-12-01,1000.0,100,100,100,100,100,800,700,500\n2025Q4,2025-12-02,2000.0,200,200,200,200,200,1600,1400,1000"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    result = ingestion.ingest_file(csv_file)
    df = result.df
    assert not df.empty
    for col in [
        "period",
        "measurement_date",
        "total_receivable_usd",
        "total_eligible_usd",
        "discounted_balance_usd",
    ]:
        assert col in df.columns
    assert result.run_id == ingestion.run_id
    assert result.metadata["row_count"] == len(df)
    assert isinstance(result.metadata["audit_log"], list)
    assert isinstance(result.metadata["validation_errors"], list)
    assert df["total_receivable_usd"].sum() == pytest.approx(3000.0)


def test_ingest_csv_error(tmp_path):
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    with pytest.raises(FileNotFoundError):
        ingestion.ingest_file(Path("nonexistent.csv"))
    events = {entry.get("event") for entry in ingestion.audit_log}
    assert "file_check" in events


def test_ingest_csv_empty_file(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.touch()
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    with pytest.raises(Exception):
        ingestion.ingest_file(csv_file)
    assert len(ingestion.errors) == 1
    assert ingestion.errors[0].get("stage") == "fatal_error"


def test_ingest_csv_strict_schema_failure(tmp_path):
    csv_content = "period,measurement_date,total_receivable_usd\n2025Q4,2025-12-01,1000.0"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    with pytest.raises(ValueError, match="Schema validation failed"):
        ingestion.ingest_file(csv_file)
    assert ingestion.errors
    assert ingestion.errors[0].get("stage") == "fatal_error"


def test_validate_loans():
    df = pd.DataFrame(
        {
            "measurement_date": ["2025-12-01"],
            "total_receivable_usd": [1000.0],
            "total_eligible_usd": [900.0],
        }
    )
    config = {
        "pipeline": {
            "phases": {
                "ingestion": {
                    "validation": {
                        "required_columns": [
                            "measurement_date",
                            "total_receivable_usd",
                            "total_eligible_usd",
                        ],
                        "numeric_columns": ["total_receivable_usd", "total_eligible_usd"],
                        "date_columns": ["measurement_date"],
                    }
                }
            }
        }
    }
    ingestion = UnifiedIngestion(config)
    ingestion._validate_dataframe(df)


def test_validate_loans_missing_field():
    df = pd.DataFrame({"measurement_date": ["2025-12-01"]})
    config = {
        "pipeline": {
            "phases": {
                "ingestion": {
                    "validation": {"required_columns": ["measurement_date", "total_receivable_usd"]}
                }
            }
        }
    }
    ingestion = UnifiedIngestion(config)
    with pytest.raises(ValueError, match="Missing required column"):
        ingestion._validate_dataframe(df)


def test_validate_loans_invalid_numeric():
    df = pd.DataFrame(
        {
            "measurement_date": ["2025-12-01"],
            "total_receivable_usd": ["invalid"],
        }
    )
    config = {
        "pipeline": {
            "phases": {
                "ingestion": {"validation": {"numeric_columns": ["total_receivable_usd"]}}
            }
        }
    }
    ingestion = UnifiedIngestion(config)
    with pytest.raises(ValueError, match="must be numeric"):
        ingestion._validate_dataframe(df)


def test_ingest_file_metadata(tmp_path):
    csv_content = "period,measurement_date,total_receivable_usd,total_eligible_usd,discounted_balance_usd\n2025Q4,2025-12-01,1000.0,900.0,850.0"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    result = ingestion.ingest_file(csv_file)
    metadata = result.metadata
    for key in ["source_file", "checksum", "row_count", "audit_log", "validation_errors"]:
        assert key in metadata
    assert metadata["row_count"] == len(result.df)
    assert metadata["validation_errors"] == []


def test_ingest_file_audit_log(tmp_path):
    csv_content = "measurement_date,total_receivable_usd,total_eligible_usd,discounted_balance_usd\n2025-12-01,1000.0,900.0,850.0"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    config = {"pipeline": {"phases": {"ingestion": {}}}}
    ingestion = UnifiedIngestion(config)
    result = ingestion.ingest_file(csv_file)
    events = {entry.get("event") for entry in result.metadata["audit_log"]}
    assert "start" in events
    assert "raw_read" in events
    assert "complete" in events


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
    
    # Verify DPD bucketing logic (aggregated by measurement_date)
    assert len(result) == 1
    assert result["dpd_0_7_usd"].iloc[0] == pytest.approx(1000.0)
    assert result["dpd_7_30_usd"].iloc[0] == pytest.approx(500.0)
    assert result["dpd_30_60_usd"].iloc[0] == pytest.approx(300.0)
    assert result["dpd_60_90_usd"].iloc[0] == pytest.approx(200.0)
    assert result["dpd_90_plus_usd"].iloc[0] == pytest.approx(100.0)


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
