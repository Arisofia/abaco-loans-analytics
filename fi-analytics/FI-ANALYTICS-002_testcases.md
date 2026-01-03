# FI-ANALYTICS-002: Detailed Test Cases

---

## SMOKE & SANITY TESTS

### Test Case A-01

**Test Case ID**: A-01  
**Test Case Title**: Pipeline Smoke Test — Execute with sample_small.csv, verify successful completion  
**Priority**: Critical  
**Type**: Functional  
**Preconditions**:
- Python 3.11+ environment with analytics dependencies installed
- `tests/data/archives/sample_small.csv` present (100 rows, 2024-01-01 to 2024-12-31)
- Working directory: project root
- No existing `exports/` directory (clean state)

**Tags**: smoke, sanity, fast, pr-gating  
**Test Data Requirements**:
- `tests/data/archives/sample_small.csv`: 100-row representative dataset

**Parameters**:
- dataset_path: `tests/data/archives/sample_small.csv`
- output_dir: `exports/`
- expected_exit_code: `0`
- timeout: `60` seconds

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Set environment: `ANALYTICS_ENABLE_FIGMA=false`, `ANALYTICS_ENABLE_NOTION=false`, `ANALYTICS_ENABLE_META=false`, `ANALYTICS_ENABLE_TRACING=false` | Export env vars | All integrations disabled |
| 2. Run: `python -m src.analytics.run_pipeline --dataset tests/data/archives/sample_small.csv --output exports/` | sample_small.csv | Process starts, logs "Pipeline start: run_id=..." |
| 3. Poll for process completion | N/A | Process exits within 60 seconds |
| 4. Check exit code | Subprocess return code | Return code == 0 |
| 5. Verify `exports/` directory exists | Filesystem | Directory created |
| 6. Check log stream for final message | logs to stdout/stderr | Log contains "Pipeline complete: status=success" |

---

### Test Case A-02

**Test Case ID**: A-02  
**Test Case Title**: Output Artifacts Existence and Schema Validation  
**Priority**: Critical  
**Type**: Functional  
**Preconditions**:
- A-01 has completed successfully
- `exports/` directory populated
- JSON schema file `tests/fixtures/schemas/kpi_results_schema.json` present

**Tags**: artifact, schema, validation, fast, pr-gating  
**Test Data Requirements**:
- Expected schema: `tests/fixtures/schemas/kpi_results_schema.json`
- Expected CSV schema: `tests/fixtures/schemas/metrics_schema.json`

**Parameters**:
- artifact_paths: `["exports/kpi_results.json", "exports/metrics.csv"]`
- schema_files: `["kpi_results_schema.json", "metrics_schema.json"]`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. List files in `exports/` directory | Filesystem | Both `kpi_results.json` and `metrics.csv` present |
| 2. Load `exports/kpi_results.json` and parse as JSON | File I/O | Valid JSON, no parse errors |
| 3. Validate JSON against schema using `jsonschema` | kpi_results.json + schema | All required fields present (e.g., `total_revenue`, `avg_deal_size`, `run_id`, `timestamp`) |
| 4. Load `exports/metrics.csv` and parse with `pandas` | File I/O | Valid CSV with headers |
| 5. Validate CSV columns against expected schema | metrics.csv + schema | All expected columns present (e.g., `metric_name`, `value`, `unit`, `date`) |
| 6. Check file sizes are non-zero | Filesystem | Both files >100 bytes |
| 7. Verify metadata: `run_id` and `timestamp` present in JSON | kpi_results.json | Both fields are strings with valid format (ISO 8601 for timestamp) |

---

## KPI CORRECTNESS & EDGE CASES

### Test Case B-01

**Test Case ID**: B-01  
**Test Case Title**: KPI Calculation Baseline Match — Computed values within tolerance (±5%)  
**Priority**: Critical  
**Type**: Functional  
**Preconditions**:
- `tests/data/archives/sample_small.csv` available
- `tests/fixtures/baseline_kpis.json` with expected KPI values (frozen/reviewed)
- Pipeline run completes successfully on sample_small

**Tags**: kpi, correctness, regression, baseline, pr-gating  
**Test Data Requirements**:
- sample_small.csv (100 rows)
- baseline_kpis.json: `{ "total_revenue": 1250000.50, "avg_deal_size": 15234.20, "num_deals": 82, "roi_pct": 8.5 }`
- tolerance: 5% (0.05)

**Parameters**:
- tolerance: `0.05`
- baseline_file: `tests/fixtures/baseline_kpis.json`
- dataset: sample_small.csv

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Run pipeline on sample_small.csv → get `kpi_results.json` | sample_small.csv | Pipeline completes, kpi_results.json exists |
| 2. Load computed KPIs from `exports/kpi_results.json` | JSON artifact | Dict of KPI keys and numeric values |
| 3. Load expected baseline from `tests/fixtures/baseline_kpis.json` | baseline_kpis.json | Dict of expected KPI values |
| 4. For each key in baseline, calculate relative error: `abs(computed[key] - baseline[key]) / baseline[key]` | Computed & baseline dicts | All relative errors ≤ 0.05 (±5%) |
| 5. Log comparison table: computed vs. baseline vs. error % | Validation results | All rows pass ✅ |
| 6. Assert no NaN or infinite values in computed KPIs | kpi_results.json | All values are finite floats |

**Note**: If tolerance violated, test fails with delta report (e.g., "total_revenue: expected 1250000.50, got 1287000.00 (+2.96% ✅)").

---

### Test Case B-02

**Test Case ID**: B-02  
**Test Case Title**: KPI Boundary Values & Null Handling  
**Priority**: High  
**Type**: Functional  
**Preconditions**:
- Analytics pipeline code accessible
- Test dataset with edge cases ready

**Tags**: boundary, null-handling, edge-case, robustness  
**Test Data Requirements**:
- `tests/data/archives/sample_null_zeros.csv`: 50 rows with nulls, zeros, negative values

**Parameters**:
- Parameters: null_columns, zero_columns, negative_columns (as list of field names)
- dataset: sample_null_zeros.csv

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Create test dataset with null, zero, and negative values in key numeric columns | CSV creation | File created with expected nulls |
| 2. Run pipeline: `python -m src.analytics.run_pipeline --dataset tests/data/archives/sample_null_zeros.csv --output exports_edge/` | sample_null_zeros.csv | Pipeline completes without exception |
| 3. Load output JSON `exports_edge/kpi_results.json` | File I/O | Valid JSON parsed |
| 4. Verify context/metadata: `null_count`, `zero_count` fields present | JSON artifact | Fields exist and values ≥0 |
| 5. Verify KPIs are computed (no NaN or inf values) | kpi_results.json | All KPI values are valid floats (not NaN, not inf) |
| 6. Verify pipeline logs note the edge case handling (e.g., "Skipping X null rows in revenue column") | logs | Log entry present |

---

### Test Case B-03

**Test Case ID**: B-03  
**Test Case Title**: Performance: Large Dataset Completes Within SLA (20 minutes)  
**Priority**: High  
**Type**: Performance  
**Preconditions**:
- `tests/data/archives/sample_large.csv` present (10k rows)
- Environment: typical CI runner (2 CPU, 8 GB RAM) or local with similar specs

**Tags**: performance, sla, benchmark, nightly  
**Test Data Requirements**:
- sample_large.csv: 10,000 rows, same date range as sample_small

**Parameters**:
- dataset: sample_large.csv
- sla_seconds: `1200` (20 minutes)
- cpu_alert_percent: `90` (warn if CPU >90% sustained)
- memory_alert_mb: `500` (warn if peak memory >500 MB)

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Record start time and system metrics (CPU, memory baseline) | System state | Baseline recorded |
| 2. Run pipeline: `python -m src.analytics.run_pipeline --dataset tests/data/archives/sample_large.csv --output exports_perf/` | sample_large.csv | Process starts |
| 3. Poll CPU and memory every 5 seconds during execution | psutil metrics | Metrics logged to perf.log |
| 4. Record end time when process completes | System state | End time captured |
| 5. Calculate elapsed time: `end_time - start_time` | Timestamps | Elapsed time ≤ 1200 seconds |
| 6. Verify artifacts created (same as A-02) | File I/O | kpi_results.json and metrics.csv present |
| 7. Generate performance report: elapsed time, peak CPU %, peak memory MB | Metrics | Report created in `exports_perf/performance_report.json` |
| 8. Assert SLA: elapsed time ≤ 1200 seconds | Report | ✅ PASS if ≤1200s, ⚠️ WARN if CPU >90%, ⚠️ WARN if memory >500 MB |

---

## INTEGRATION (MOCKED)

### Test Case C-01

**Test Case ID**: C-01  
**Test Case Title**: Figma Sync Success — Mocked endpoint returns OK, pipeline records success flag  
**Priority**: High  
**Type**: Integration  
**Preconditions**:
- Mock Figma server fixture running on `http://localhost:5000`
- `ANALYTICS_ENABLE_FIGMA=true`, `FIGMA_TOKEN=test-token-123`
- Sample KPI payload ready to post

**Tags**: integration, figma, mock, external-api  
**Test Data Requirements**:
- Mock response: `{ "id": "file-abc123", "status": "updated" }`
- Figma API URL mock: `http://localhost:5000/v1/files/figma-doc-id`

**Parameters**:
- mock_url: `http://localhost:5000`
- expected_status: `200`
- expected_response_keys: `["id", "status"]`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Start mock HTTP server on port 5000 with Figma success response | Mock setup | Server listening, ready for requests |
| 2. Configure pipeline with mock endpoint: `FIGMA_API_BASE_URL=http://localhost:5000` | Environment | Config applied |
| 3. Run pipeline with sample_small.csv | sample_small.csv | Pipeline executes |
| 4. Pipeline attempts Figma sync (posts KPI data to mock) | Request to mock | HTTP POST sent to `/v1/files/...` with authorization header |
| 5. Mock server receives request and returns `{ "id": "file-abc123", "status": "updated" }` | Mock response | Response sent to pipeline |
| 6. Verify logs contain "Figma sync successful: id=file-abc123" | logs | Log entry present |
| 7. Check `kpi_results.json` for `figma_sync_status: "success"` field | Artifact | Field == "success" |

---

### Test Case C-02

**Test Case ID**: C-02  
**Test Case Title**: Notion Sync Success — Mocked endpoint creates page, pipeline logs success  
**Priority**: High  
**Type**: Integration  
**Preconditions**:
- Mock Notion server fixture running on `http://localhost:5001`
- `ANALYTICS_ENABLE_NOTION=true`, `NOTION_API_KEY=ntn-key-456`
- Notion database ID configured

**Tags**: integration, notion, mock, external-api  
**Test Data Requirements**:
- Mock response: `{ "id": "page-xyz789", "object": "page", "created_time": "2024-01-01T00:00:00.000Z" }`
- Notion API URL mock: `http://localhost:5001/v1/pages`

**Parameters**:
- mock_url: `http://localhost:5001`
- expected_status: `200`
- expected_object_type: `"page"`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Start mock HTTP server on port 5001 with Notion success response | Mock setup | Server listening |
| 2. Configure pipeline: `NOTION_API_BASE_URL=http://localhost:5001` | Environment | Config applied |
| 3. Run pipeline with sample_small.csv | sample_small.csv | Pipeline executes |
| 4. Pipeline attempts Notion sync (posts KPI data to mock) | Request to mock | HTTP POST to `/v1/pages` with auth header |
| 5. Mock returns `{ "id": "page-xyz789", "object": "page", ... }` | Mock response | Response received |
| 6. Verify logs contain "Notion page created: id=page-xyz789" | logs | Log entry present |
| 7. Check `kpi_results.json` for `notion_sync_status: "success"` and `notion_page_id: "page-xyz789"` | Artifact | Both fields present and correct |

---

### Test Case C-03

**Test Case ID**: C-03  
**Test Case Title**: Meta Sync Graceful Degradation — Mocked endpoint returns 500, pipeline logs error & continues  
**Priority**: High  
**Type**: Integration  
**Preconditions**:
- Mock Meta server fixture running on `http://localhost:5002`
- Server configured to return HTTP 500 for Meta endpoint
- `ANALYTICS_ENABLE_META=true`, `META_ACCESS_TOKEN=meta-token-789`

**Tags**: integration, meta, graceful-degradation, error-handling  
**Test Data Requirements**:
- Mock response: HTTP 500 with error body `{ "error": "Internal server error" }`
- Meta API URL mock: `http://localhost:5002/v1/create_event`

**Parameters**:
- mock_url: `http://localhost:5002`
- error_status: `500`
- expect_pipeline_success: `true` (pipeline should NOT fail)

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Start mock HTTP server on port 5002 configured to return 500 for all requests | Mock setup | Server ready, returns 500 |
| 2. Configure pipeline: `META_API_BASE_URL=http://localhost:5002` | Environment | Config applied |
| 3. Run pipeline with sample_small.csv | sample_small.csv | Pipeline starts |
| 4. Pipeline attempts Meta sync (posts to mock) | Request to mock | HTTP POST to `/v1/create_event` |
| 5. Mock returns HTTP 500 with error body | Mock response | Error response received by pipeline |
| 6. Verify logs contain "Meta sync failed with status 500: Internal server error" | logs | Error logged at WARNING level |
| 7. Verify logs do NOT contain stack trace or internal error details | logs | Log is sanitized (no sensitive context) |
| 8. Pipeline continues and produces valid artifacts | Artifact | kpi_results.json and metrics.csv exist |
| 9. Check `kpi_results.json` for `meta_sync_status: "failed"` and `pipeline_status: "success"` | Artifact | Both fields present; pipeline_status == "success" despite meta failure |

---

### Test Case C-04

**Test Case ID**: C-04  
**Test Case Title**: All Integrations Missing (no tokens set) — Pipeline runs, marks integrations skipped  
**Priority**: High  
**Type**: Integration  
**Preconditions**:
- Environment cleared: `FIGMA_TOKEN=`, `NOTION_API_KEY=`, `META_ACCESS_TOKEN=` (unset or empty)
- `ANALYTICS_ENABLE_FIGMA=true`, `ANALYTICS_ENABLE_NOTION=true`, `ANALYTICS_ENABLE_META=true` (integrations enabled, but no credentials)

**Tags**: integration, secret-gating, graceful-degradation  
**Test Data Requirements**:
- None (no mocks needed)

**Parameters**:
- missing_tokens: `["FIGMA_TOKEN", "NOTION_API_KEY", "META_ACCESS_TOKEN"]`
- expect_pipeline_success: `true`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Unset all integration tokens from environment | Environment vars | All cleared |
| 2. Run pipeline with sample_small.csv | sample_small.csv | Pipeline starts |
| 3. Pipeline checks for credentials at startup | Config validation | Pipeline logs "FIGMA_TOKEN not set, skipping Figma sync" (3 times for each) |
| 4. Pipeline proceeds with data processing (no mock servers running) | Execution | KPI computation continues |
| 5. Verify pipeline completes successfully | Exit code | Exit code == 0 |
| 6. Verify artifacts created (no integration attempts) | File I/O | kpi_results.json and metrics.csv exist |
| 7. Check `kpi_results.json` for integration status fields | Artifact | `figma_sync_status: "skipped"`, `notion_sync_status: "skipped"`, `meta_sync_status: "skipped"` |
| 8. Verify no HTTP requests attempted (logs show no connection errors) | logs | Logs contain "Skipped" messages, NO "connection refused" or network errors |

---

## TRACING & OBSERVABILITY

### Test Case D-01

**Test Case ID**: D-01  
**Test Case Title**: Tracing Spans Emitted — Test collector receives spans with job attributes  
**Priority**: High  
**Type**: Integration  
**Preconditions**:
- Mock OTLP collector fixture running on `localhost:4317`
- `ANALYTICS_ENABLE_TRACING=true`
- Pipeline tracing library (OpenTelemetry) configured to export to mock collector

**Tags**: observability, tracing, otlp, integration  
**Test Data Requirements**:
- Mock OTLP receiver (test double in `tests/fixtures/mock_otel_collector.py`)

**Parameters**:
- otel_endpoint: `http://localhost:4317`
- expected_span_names: `["pipeline_start", "kpi_computation", "integration_sync", "artifact_upload"]`
- required_attributes: `["job_name", "run_id", "client_id"]`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Start mock OTLP collector on port 4317 | Mock setup | Listening, captures spans |
| 2. Configure pipeline: `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`, `ANALYTICS_ENABLE_TRACING=true` | Environment | Config applied |
| 3. Run pipeline with sample_small.csv (with unique run_id) | sample_small.csv + run_id | Pipeline executes |
| 4. Pipeline emits tracing spans during execution | Execution | Spans sent to mock collector |
| 5. Retrieve captured spans from mock collector | Mock state | List of spans (JSON) |
| 6. Verify span count ≥ 4 (one per major step) | Spans | At least 4 distinct spans received |
| 7. For each span, verify required attributes present | Span attributes | All spans have job_name, run_id, client_id |
| 8. Verify run_id attribute matches pipeline run_id | Span + artifact | Span run_id == kpi_results.json run_id |
| 9. Verify span timing chain (start → computation → sync → upload) | Span timestamps | Timestamps in correct order, durations reasonable |

---

### Test Case D-02

**Test Case ID**: D-02  
**Test Case Title**: Tracing Fallback — Missing/misconfigured tracing logs mock messages & completes  
**Priority**: Medium  
**Type**: Integration  
**Preconditions**:
- Tracing library disabled or missing OTEL endpoint
- `ANALYTICS_ENABLE_TRACING=false` OR `OTEL_EXPORTER_OTLP_ENDPOINT=` (invalid/missing)
- Mock OTLP collector NOT running

**Tags**: observability, fallback, robustness  
**Test Data Requirements**:
- None (no collector needed)

**Parameters**:
- otel_endpoint: (unset or invalid)
- enable_tracing: `false`
- expect_pipeline_success: `true`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Unset `OTEL_EXPORTER_OTLP_ENDPOINT` or set to invalid value | Environment | Config invalid |
| 2. Set `ANALYTICS_ENABLE_TRACING=false` | Environment | Tracing disabled |
| 3. Run pipeline with sample_small.csv | sample_small.csv | Pipeline starts |
| 4. Pipeline attempts tracing initialization | Execution | Tracing library tries to connect, fails gracefully |
| 5. Verify logs contain "Tracing disabled or unavailable, using fallback logging" | logs | Fallback message present |
| 6. Pipeline continues processing (no crash) | Execution | KPI computation proceeds |
| 7. Verify pipeline completes successfully | Exit code | Exit code == 0 |
| 8. Verify artifacts created (with or without tracing) | File I/O | kpi_results.json and metrics.csv exist |
| 9. Verify NO errors or exceptions in logs related to tracing initialization | logs | Logs are clean (no "connection refused", no "NameError") |

---

## ROBUSTNESS & RETRIES

### Test Case E-01

**Test Case ID**: E-01  
**Test Case Title**: External Integration Transient Error + Retry — Mock fails 2x, succeeds 3rd  
**Priority**: High  
**Type**: Robustness  
**Preconditions**:
- Mock Figma server fixture configured with retry-fail logic
- `ANALYTICS_ENABLE_FIGMA=true`, `FIGMA_TOKEN=test-token`
- Retry policy configured (e.g., exponential backoff, max 3 attempts)

**Tags**: robustness, retry, transient-failure, external-api  
**Test Data Requirements**:
- Mock server setup: fail requests 1–2, succeed on request 3

**Parameters**:
- max_retries: `3`
- backoff_multiplier: `2`
- timeout_per_attempt: `5` seconds

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Start mock Figma server configured to fail first 2 requests with HTTP 503 (Service Unavailable) | Mock setup | Server ready |
| 2. Configure pipeline: `FIGMA_API_BASE_URL=http://localhost:5000`, retry max=3 | Environment | Config applied |
| 3. Run pipeline with sample_small.csv | sample_small.csv | Pipeline starts |
| 4. Pipeline attempts Figma sync (request 1) | Request | Mock returns 503 |
| 5. Pipeline logs retry attempt 1 and waits with backoff (2 seconds) | logs | Retry logged |
| 6. Pipeline retries (request 2) | Request | Mock returns 503 again |
| 7. Pipeline logs retry attempt 2 and waits with backoff (4 seconds) | logs | Retry logged |
| 8. Pipeline retries (request 3) | Request | Mock returns 200 OK with success response |
| 9. Pipeline logs "Figma sync successful after 3 attempts" | logs | Success message present |
| 10. Verify pipeline completes successfully and artifacts contain `figma_sync_status: "success"` | Artifact | Status == "success" |

---

### Test Case E-02

**Test Case ID**: E-02  
**Test Case Title**: Rate Limiting on Artifact Upload — Pipeline retries rate-limited responses  
**Priority**: High  
**Type**: Robustness  
**Preconditions**:
- Mock artifact storage (S3 or similar) configured to return HTTP 429 (Too Many Requests)
- Pipeline configured to upload artifacts to mock endpoint
- Retry policy with exponential backoff in place

**Tags**: robustness, rate-limiting, artifact-upload, transient-failure  
**Test Data Requirements**:
- Mock response: HTTP 429 with `Retry-After: 2` header

**Parameters**:
- max_upload_retries: `3`
- rate_limit_status: `429`
- initial_backoff_seconds: `1`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Start mock artifact storage server on port 6000, configured to return 429 for first request, then 200 OK | Mock setup | Server ready |
| 2. Configure pipeline: `ARTIFACT_UPLOAD_URL=http://localhost:6000/upload` | Environment | Config applied |
| 3. Run pipeline with sample_small.csv (generate KPI artifacts) | sample_small.csv | Pipeline produces artifacts |
| 4. Pipeline attempts artifact upload (request 1) | Request | Mock returns 429 with Retry-After header |
| 5. Pipeline logs rate limit detected and schedules retry per Retry-After header | logs | Rate limit message logged |
| 6. Pipeline waits 2 seconds (per Retry-After) | Execution | Delay observed |
| 7. Pipeline retries artifact upload (request 2) | Request | Mock returns 200 OK |
| 8. Verify logs contain "Artifact upload successful after 2 attempts" | logs | Success message present |
| 9. Verify pipeline completes successfully | Exit code | Exit code == 0 |
| 10. Verify final artifacts are present and complete | File I/O | kpi_results.json and metrics.csv exist, not corrupted |

---

## SECURITY & SECRETS

### Test Case F-01

**Test Case ID**: F-01  
**Test Case Title**: Secrets Not Leaked in Logs — No secret substrings in output  
**Priority**: Critical  
**Type**: Security  
**Preconditions**:
- Test with real secret values set (e.g., `FIGMA_TOKEN=sk_live_1234567890abcdef`)
- Pipeline executed with secrets in environment
- Log output captured to file for audit

**Tags**: security, secrets, audit, pr-gating  
**Test Data Requirements**:
- Test secrets: `FIGMA_TOKEN=test-secret-abc123`, `NOTION_API_KEY=test-key-xyz789`, `META_ACCESS_TOKEN=test-meta-token-111`

**Parameters**:
- secrets_to_check: `["test-secret-abc123", "test-key-xyz789", "test-meta-token-111"]`
- log_file: `tests/logs/pipeline_audit.log`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Set environment with test secret tokens | Environment vars | Secrets in memory |
| 2. Redirect pipeline logs to file: `tests/logs/pipeline_audit.log` | Log capture | Log file created |
| 3. Run pipeline with sample_small.csv | sample_small.csv | Pipeline executes, logs written to file |
| 4. Read log file into memory | File I/O | Log content loaded |
| 5. For each secret, search log using regex (whole-word match) | Audit logic | Search for exact token strings |
| 6. Verify NO occurrences found for any secret | Search result | All searches return 0 matches |
| 7. Verify logs contain sanitized references instead (e.g., "Using token ***abc123" or "Using token [REDACTED]") | logs | Sanitized message present for each integration |
| 8. Document audit result: "✅ PASS: 0 secrets leaked" | Report | Audit report generated |

---

### Test Case F-02

**Test Case ID**: F-02  
**Test Case Title**: Secret Validation — Missing required secrets triggers warnings, skips integration  
**Priority**: Medium  
**Type**: Security  
**Preconditions**:
- `ANALYTICS_ENABLE_FIGMA=true` but `FIGMA_TOKEN` unset
- `ANALYTICS_ENABLE_NOTION=true` but `NOTION_API_KEY` unset

**Tags**: security, secret-validation, graceful-degradation  
**Test Data Requirements**:
- None (secrets intentionally unset)

**Parameters**:
- required_secrets: `{ "FIGMA": "FIGMA_TOKEN", "NOTION": "NOTION_API_KEY", "META": "META_ACCESS_TOKEN" }`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Unset required secret tokens | Environment | Tokens cleared |
| 2. Set integration enable flags to true: `ANALYTICS_ENABLE_FIGMA=true`, `ANALYTICS_ENABLE_NOTION=true` | Environment | Integrations enabled |
| 3. Run pipeline with sample_small.csv | sample_small.csv | Pipeline starts |
| 4. Pipeline validates secrets at initialization | Config check | Secret validation runs |
| 5. Verify logs contain warnings: "FIGMA_TOKEN not set, Figma integration will be skipped" (and for Notion, Meta) | logs | Warning message for each missing secret |
| 6. Pipeline continues (no exception raised) | Execution | Proceeds to KPI computation |
| 7. Verify pipeline completes successfully | Exit code | Exit code == 0 |
| 8. Verify artifacts contain `figma_sync_status: "skipped"`, `notion_sync_status: "skipped"`, etc. | Artifact | All integration statuses == "skipped" |
| 9. Verify NO HTTP requests attempted to mock servers (no connection errors in logs) | logs | No network-related errors |

---

## FAILURE MODES / RESUMPTION / IDEMPOTENCY

### Test Case G-01

**Test Case ID**: G-01  
**Test Case Title**: Partial Failure Mid-Run — Exception during processing, re-run produces identical artifacts  
**Priority**: High  
**Type**: Robustness  
**Preconditions**:
- Custom test dataset with deliberate error condition (e.g., row 50 triggers division by zero in KPI computation)
- Pipeline configured to catch exceptions and log them
- Re-run capability (pipeline can be invoked again with same inputs)

**Tags**: robustness, idempotency, recovery, failure-handling  
**Test Data Requirements**:
- `tests/data/archives/sample_error.csv`: 100 rows with error trigger at row 50

**Parameters**:
- error_row: `50`
- error_type: `ZeroDivisionError` (simulated)
- expect_partial_output: `true` (some artifacts may be partial on first run)

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Create test dataset with intentional error condition at row 50 | CSV creation | File created |
| 2. Clear output directory: `rm -rf exports_partial/` | Filesystem | Clean slate |
| 3. Run pipeline (1st attempt) with sample_error.csv | sample_error.csv | Pipeline encounters error at row 50 |
| 4. Verify pipeline logs error but doesn't crash completely | logs | Error logged (not unhandled exception) |
| 5. Check partial output: some KPI values computed for rows 1–49 | File I/O | Partial artifacts exist |
| 6. Run pipeline again (2nd attempt, resume) with same dataset | sample_error.csv | Pipeline re-runs |
| 7. Verify pipeline handles error gracefully (e.g., skips problem row and continues) | Execution | Processing continues or fails deterministically |
| 8. Compare artifacts from run 1 and run 2 (final state) | File comparison | Final outputs identical (deterministic) |
| 9. Verify no duplicate KPI entries in final artifact | Artifact audit | All KPI values appear once, counts correct |
| 10. Verify `run_id` and `timestamp` are updated on re-run (but KPI values same) | Artifact fields | Metadata updated, data values unchanged |

---

### Test Case G-02

**Test Case ID**: G-02  
**Test Case Title**: Concurrent Runs with Same run_id — Outputs remain deterministic (no corruption)  
**Priority**: Medium  
**Type**: Robustness  
**Preconditions**:
- Pipeline supports concurrent execution (thread-safe or process-safe)
- Artifact file locking or atomic writes in place
- Test environment with 2+ CPU cores

**Tags**: robustness, concurrency, idempotency, determinism  
**Test Data Requirements**:
- sample_small.csv (2 copies for concurrent runs)

**Parameters**:
- num_concurrent_runs: `2`
- same_run_id: `run-id-12345` (forced same ID)
- timeout_per_run: `60` seconds

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Generate unique run_id: `run-id-12345` | ID generation | ID created |
| 2. Clear output directory: `rm -rf exports_concurrent/` | Filesystem | Clean slate |
| 3. Start concurrent run 1 with sample_small.csv, forcing run_id=run-id-12345 | Thread 1 | Process 1 starts |
| 4. Start concurrent run 2 with sample_small.csv, forcing run_id=run-id-12345 | Thread 2 | Process 2 starts (while process 1 still running) |
| 5. Both processes execute simultaneously (KPI computation, integration sync) | Execution | Both processes run in parallel |
| 6. Wait for both processes to complete | Polling | Both exit with code 0 |
| 7. Check output directory for artifacts | Filesystem | Expected files present (1 set, not 2) |
| 8. Load final `exports_concurrent/kpi_results.json` and inspect | File I/O | Single valid JSON file |
| 9. Verify no duplicate KPI entries, no partial state, no corruption | Audit | Data structure clean |
| 10. Verify `run_id` in artifact == `run-id-12345` | Artifact field | Correct run_id |
| 11. Manually inspect for file locking evidence (logs mention file lock acquired/released) | logs | Locking messages present if applicable |

**Note**: This test is marked **Partial** for automation; final state comparison may need manual verification of determinism across runs.

---

## CI & CONFIG CHECKS

### Test Case H-01

**Test Case ID**: H-01  
**Test Case Title**: Unit Tests for KPI Functions — >90% Coverage, all regression tests pass  
**Priority**: Critical  
**Type**: Regression  
**Preconditions**:
- Unit test suite exists in `tests/unit/test_kpi_functions.py`
- pytest-cov installed
- Coverage threshold set to 90%

**Tags**: unit, coverage, regression, ci-gating  
**Test Data Requirements**:
- Unit test fixtures in `tests/fixtures/`

**Parameters**:
- coverage_threshold: `0.90` (90%)
- target_modules: `["src.analytics.kpi_functions"]`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Run unit tests: `pytest tests/unit/test_kpi_functions.py -v --cov=src.analytics.kpi_functions --cov-report=term-missing` | Test suite | Tests execute |
| 2. Verify all tests pass (exit code 0) | Test output | 0 failures |
| 3. Extract coverage percentage from report | Coverage output | e.g., "TOTAL 150 18 88%" |
| 4. Verify coverage ≥ 90% | Coverage metric | Coverage ≥ 0.90 |
| 5. Verify missing coverage is documented (non-critical paths) | Report | Comment explains why lines uncovered |
| 6. Generate coverage HTML report: `pytest ... --cov-report=html` | File I/O | Report generated in `htmlcov/` |
| 7. Verify no regressions: test count >= previous baseline | Test count | Same or more tests than last merge |

---

### Test Case H-02

**Test Case ID**: H-02  
**Test Case Title**: mypy Type-Check — Analytics modules pass mypy strict mode  
**Priority**: Critical  
**Type**: Regression  
**Preconditions**:
- mypy installed
- mypy config in `pyproject.toml` or `mypy.ini` with strict settings
- Analytics modules typed (no `Any` unless justified)

**Tags**: type-check, regression, ci-gating  
**Test Data Requirements**:
- None (static analysis)

**Parameters**:
- mypy_strict: `true`
- target_modules: `["src/analytics/"]`

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Run mypy on analytics modules: `mypy src/analytics/ --strict` | mypy | Analysis runs |
| 2. Capture output and exit code | mypy output | Exit code == 0 or list of errors |
| 3. If exit code != 0, verify NO NEW errors (compare against baseline) | Error diff | Only pre-approved errors allowed |
| 4. Verify specific error count (document approved deviations) | Error count | Count matches approved threshold (e.g., 0 new errors) |
| 5. Generate mypy report: `mypy src/analytics/ --html-report=mypy_report/` | Report | Report file created |
| 6. Document any `# type: ignore` comments and justification | Code comments | Comments present and reviewed |

---

## END-TO-END ACCEPTANCE

### Test Case I-01

**Test Case ID**: I-01  
**Test Case Title**: Full E2E with sample dataset + mocked integrations — Artifacts, traces, notifications correct  
**Priority**: High  
**Type**: Integration  
**Preconditions**:
- All mock servers running (Figma, Notion, Meta, OTLP, artifact storage, Slack notification)
- All prerequisites from earlier tests met
- sample_small.csv available

**Tags**: e2e, acceptance, integration, nightly  
**Test Data Requirements**:
- sample_small.csv
- All mock service configurations
- Expected notification payload template

**Parameters**:
- dataset: sample_small.csv
- num_mocks_enabled: `4` (Figma, Notion, Meta, OTLP)
- expect_success: `true`
- expect_notification: `true` (Slack)

**Test Steps — Data — Expected Result**:

| Step | Data | Expected Result |
|---|---|---|
| 1. Start all mock servers (Figma, Notion, Meta, OTLP, artifact storage, Slack webhook) | Mock setup | All servers listening on expected ports |
| 2. Configure pipeline with all mocked endpoints | Environment | All integration URLs point to mocks |
| 3. Set environment for full tracing: `ANALYTICS_ENABLE_TRACING=true`, `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317` | Environment | Tracing enabled |
| 4. Set all integration tokens (test values): `FIGMA_TOKEN`, `NOTION_API_KEY`, `META_ACCESS_TOKEN` | Environment | Secrets set |
| 5. Run pipeline with sample_small.csv | sample_small.csv | Pipeline executes end-to-end |
| 6. Verify pipeline completes successfully (exit code 0) | Exit code | 0 |
| 7. Verify all artifacts produced: `kpi_results.json`, `metrics.csv`, `performance_report.json` | File I/O | All files exist, non-empty |
| 8. Verify JSON schema validation for all artifacts (A-02 equivalent) | Schema validation | All pass |
| 9. Verify KPI values correct (B-01 equivalent, within tolerance) | Baseline validation | All KPIs within ±5% |
| 10. Verify all integration sync statuses recorded | Artifact | `figma_sync_status`, `notion_sync_status`, `meta_sync_status` == "success" |
| 11. Retrieve captured tracing spans from mock OTLP collector | Mock state | ≥4 spans with proper attributes |
| 12. Verify Slack notification sent (check mock server request log) | Mock audit | POST to Slack webhook endpoint received |
| 13. Verify notification payload contains: run_id, timestamp, KPI summary, artifact links | Payload check | All fields present and formatted correctly |
| 14. Verify no secrets in final logs or notification payload | Audit | No secret tokens visible |
| 15. Generate final E2E acceptance report: ✅ PASS | Report | Document all verifications as pass |

---

## Test Execution Schedule

### Sprint 0 (Days 1–2)
**Tests**: A-01, A-02, B-01, B-02, H-01, H-02  
**Duration**: ~8 hours  
**Output**: Smoke baseline and unit regression

### Sprint 1 (Days 3–7)
**Tests**: C-01, C-02, C-03, C-04, D-01, D-02, F-01, F-02  
**Duration**: ~12 hours  
**Output**: Integration and security tests

### Sprint 2 (Week 2)
**Tests**: B-03, E-01, E-02, G-01, G-02, I-01  
**Duration**: ~16 hours  
**Output**: Performance, robustness, E2E

### Ongoing
**Maintenance**: Benchmark monitoring, baseline updates, new edge cases
