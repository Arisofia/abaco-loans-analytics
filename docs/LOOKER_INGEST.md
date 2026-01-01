# Looker Ingest (Cascade Disabled)

This workflow runs the unified pipeline using Looker exports while Cascade ingestion is offline.

## Required Files

- `data/raw/looker_exports/loan_par_balances.csv` (preferred snapshot with PAR buckets)
- `data/raw/looker_exports/loans.csv` (fallback if PAR balances are unavailable)
- `data/raw/financial_statements/*.csv` (optional, used to populate cash balance)

## How Looker Data Is Mapped

The ingestion layer converts Looker PAR balances into the loan tape schema expected by the pipeline:

- `reporting_date` → `measurement_date`
- `outstanding_balance_usd` → `total_receivable_usd`
- `par_90_balance_usd` → `dpd_90_plus_usd`
- `par_60_balance_usd` → `dpd_60_90_usd` (net of PAR90)
- `par_30_balance_usd` → `dpd_30_60_usd` (net of PAR60)
- `par_7_balance_usd` → `dpd_7_30_usd` (net of PAR30)
- `total_receivable_usd` - `par_7_balance_usd` → `dpd_0_7_usd`

Optional financial statements can provide a `cash_balance` column (see `config/pipeline.yml` for candidate column names). If unavailable, `cash_available_usd` defaults to `0`.

If `loan_par_balances.csv` is missing, the pipeline can fall back to `loans.csv` and bucket balances by `dpd`. The snapshot date is controlled by `pipeline.phases.ingestion.looker.measurement_date_strategy` in `config/pipeline.yml` (`today`, `max_disburse_date`, `max_maturity_date`, or a custom `measurement_date_column`).

## Run the Pipeline

```bash
PIPELINE_ENV=development python scripts/run_data_pipeline.py \
  --input data/raw/looker_exports/loan_par_balances.csv
```

The development environment is configured to use Looker sources by default. Adjust `config/environments/development.yml` if you want a different Looker file path.
