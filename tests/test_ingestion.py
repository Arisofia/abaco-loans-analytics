import pandas as pd
import pytest
from pathlib import Path

from python.pipeline.ingestion import UnifiedIngestion


def test_ingest_csv(tmp_path, minimal_config):
    csv_content = "measurement_date,total_receivable_usd,total_eligible_usd,discounted_balance_usd,dpd_0_7_usd,dpd_7_30_usd,dpd_30_60_usd,dpd_60_90_usd,dpd_90_plus_usd,cash_available_usd\n2025-12-01,1000.0,800,700,100,100,100,100,100,500\n2025-12-02,2000.0,1600,1400,200,200,200,200,200,1000"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    ingestion = UnifiedIngestion(minimal_config)
    result = ingestion.ingest_file(csv_file)
    assert not result.df.empty
    assert result.run_id == ingestion.run_id
    assert isinstance(result.df, pd.DataFrame)
    assert result.df["total_receivable_usd"].sum() == pytest.approx(3000.0)


def test_ingest_csv_error(tmp_path, minimal_config):
    ingestion = UnifiedIngestion(minimal_config)
    with pytest.raises(FileNotFoundError):
        ingestion.ingest_file(tmp_path / "nonexistent.csv")


def test_ingest_csv_empty_file(tmp_path, minimal_config):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")
    ingestion = UnifiedIngestion(minimal_config)
    with pytest.raises(Exception):
        ingestion.ingest_file(csv_file)


def test_ingest_csv_strict_schema_failure(tmp_path, minimal_config):
    csv_content = "measurement_date,total_receivable_usd\n2025-12-01,1000.0"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    minimal_config["pipeline"]["phases"]["ingestion"]["validation"]["strict"] = True
    ingestion = UnifiedIngestion(minimal_config)
    with pytest.raises(Exception):
        ingestion.ingest_file(csv_file)


def test_ingest_csv_success(tmp_path, minimal_config):
    csv_content = "measurement_date,total_receivable_usd,total_eligible_usd,discounted_balance_usd,cash_available_usd,dpd_0_7_usd,dpd_7_30_usd,dpd_30_60_usd,dpd_60_90_usd,dpd_90_plus_usd\n2025-12-01,1000.0,800,700,500,100,100,100,100,100"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    ingestion = UnifiedIngestion(minimal_config)
    result = ingestion.ingest_file(csv_file)
    assert result.df is not None
    assert len(result.df) == 1


def test_ingest_http(minimal_config):
    ingestion = UnifiedIngestion(minimal_config)
    with pytest.raises(Exception):
        ingestion.ingest_http("http://nonexistent-url.invalid/data.csv")


def test_run_id_generation(minimal_config):
    ingestion1 = UnifiedIngestion(minimal_config)
    ingestion2 = UnifiedIngestion(minimal_config)
    assert ingestion1.run_id != ingestion2.run_id
    assert ingestion1.run_id.startswith("ingest_")
    assert ingestion2.run_id.startswith("ingest_")


def test_audit_log_creation(tmp_path, minimal_config):
    csv_content = "measurement_date,total_receivable_usd,total_eligible_usd,discounted_balance_usd,cash_available_usd,dpd_0_7_usd,dpd_7_30_usd,dpd_30_60_usd,dpd_60_90_usd,dpd_90_plus_usd\n2025-12-01,1000.0,800,700,500,100,100,100,100,100"
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(csv_content)
    ingestion = UnifiedIngestion(minimal_config)
    result = ingestion.ingest_file(csv_file)
    assert len(ingestion.audit_log) > 0
    assert any(entry["event"] == "start" for entry in ingestion.audit_log)
    assert any(entry["event"] == "complete" for entry in ingestion.audit_log)
