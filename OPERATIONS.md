# Abaco Loans Analytics - Operations Runbook

## 1. System Overview
The Abaco Loans Analytics system is a production-grade fintech intelligence pipeline. It orchestrates data ingestion from multiple sources (CSV, Parquet, Excel, HTTP APIs), applies advanced financial transformations, calculates key performance indicators (KPIs), and generates executive reports.

## 2. Environment Setup
- **Python**: 3.10+ (3.11 recommended)
- **Virtual Environment**: `.venv`
- **Dependencies**: `pip install -r requirements.txt -r dev-requirements.txt`

### Essential Environment Variables
- `PIPELINE_ENV`: `dev`, `staging`, or `production` (default: `dev`)
- `AZURE_STORAGE_CONNECTION_STRING`: Required for Azure Blob storage outputs.
- `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE`: Required for database sync.
- `NOTION_TOKEN` / `NOTION_REPORTS_PAGE_ID`: Required for Notion reporting.
- `FIGMA_TOKEN` / `FIGMA_FILE_KEY`: Required for Figma dashboard updates.

## 3. Core Operational Commands

### Running the Full Pipeline
The primary entry point for production runs is `apps/analytics/run_report.py`.

```bash
# Execute pipeline and generate executive report
python apps/analytics/run_report.py \
  --data data/raw/looker_exports/loans.csv \
  --output reports/daily_summary_$(date +%Y%m%d).md
```

### Manual Pipeline Execution (Internal)
```bash
python scripts/run_data_pipeline.py --input data/raw/abaco_portfolio.csv
```

### Health & Parity Checks
```bash
# Verify KPI parity (Python vs SQL)
make test-kpi-parity

# Full system bootstrap and health check
python tools/zencoder_bootstrap.py
```

## 4. Monitoring & Artifacts

### Log Location
- **Pipeline Runs**: `logs/runs/<run_id>/`
- **Daily Logs**: `logs/abaco.analytics.log`

### Success Criteria
1. `summary.json` contains `"status": "success"`.
2. `manifest.json` is generated with valid file hashes.
3. No critical anomalies flagged in `compliance.json`.

## 5. Incident Response & Triage

### Common Failure Modes
- **Schema Drift**: If ingestion fails due to missing columns, verify the input file against `config/data_schemas/`.
- **Circuit Breaker**: If the pipeline stops with a circuit breaker error, check recent data quality trends or downstream service availability.
- **KPI Anomalies**: If reports show unexpected KPI values, run `tests/test_kpi_parity.py` to rule out engine inconsistencies.

### Rollback Procedure
1. Identify the last successful `run_id`.
2. Re-run reporting scripts using the cached parquet files in `data/metrics/<run_id>.parquet`.

## 6. Maintenance
- **Weekly**: Run `make audit-code` to ensure engineering standards are maintained.
- **Monthly**: Review and update KPI definitions in `config/kpis/kpi_definitions.yaml`.
- **v2.0 Cutover**: Delete `config/LEGACY/` and archived modules as per the migration plan.

---
*Confidential - Abaco Loans Operations*
