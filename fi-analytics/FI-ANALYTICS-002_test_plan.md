# FI-ANALYTICS-002: Analytics Pipeline / Batch Export — Test Plan

## Objectives

1. **Functional Correctness**: Verify end-to-end pipeline execution produces accurate KPI outputs matching baseline values within tolerance (+/− specified delta).
2. **Integration Reliability**: Validate graceful degradation when external integrations (Figma, Notion, Meta) fail, are missing, or return errors.
3. **Observability & Tracing**: Confirm tracing spans are emitted for top-level jobs with proper context attributes (client_id, run_id) without breaking batch execution.
4. **Performance SLAs**: Ensure full pipeline run completes within scheduled window (20 minutes for sample dataset; 60+ minutes for production dataset).
5. **Security & Secret Handling**: Verify no secrets are leaked in logs; secret validation gates integrations gracefully.
6. **Robustness & Idempotency**: Confirm retry logic handles transient failures; concurrent or re-run scenarios produce deterministic outputs without data loss or corruption.

## Scope

**In Scope**:
- End-to-end analytics pipeline execution (data ingestion → KPI computation → integration sync → artifact upload)
- KPI calculation logic with boundary conditions and null handling
- Integration with mocked Figma, Notion, Meta, and OTLP tracing endpoints
- Artifact production (kpi_results.json, metrics.csv) and schema validation
- Secret gating and sanitization in logs
- Retry and graceful degradation behavior
- Performance benchmarking (runtime, CPU, memory)
- CI validation on PRs and nightly full E2E runs

**Out of Scope**:
- Figma, Notion, Meta API production-level testing (external responsibility)
- Real credential storage or rotation testing (GitOps/secrets management)
- Full OTLP backend integration (test double sufficient)
- Data pipeline source-level ML model quality (data science responsibility)
- Historical baseline drift analysis over time

## Test Approach

### Levels

| Level | Focus | Tools | Duration |
|---|---|---|---|
| **Unit** | KPI functions, boundary values, null handling | pytest, hypothesis | <1 min |
| **Integration** | Mocked externals (Figma, Notion, Meta, OTLP), secret gating | pytest-httpserver, responses, testcontainers | 2–3 min |
| **End-to-End** | Full pipeline on sample dataset, artifact validation, tracing capture | pytest fixtures, local artifacts | 5–10 min |
| **Performance** | Runtime on larger dataset, CPU/memory profiling | pytest-benchmark, psutil | 10–20 min |
| **Robustness** | Transient failures, retries, idempotency, concurrency | pytest, fault-injection | 3–5 min |
| **Security** | Secret leakage, credential validation, sanitized output | audit log scanning, regex assertions | <1 min |

### Test Matrix

| Aspect | Smoke | Functional | Integration | E2E | Performance | Robustness | Security |
|---|---|---|---|---|---|---|---|
| Pipeline execution | ✅ |  |  |  |  |  |  |
| KPI correctness |  | ✅ |  | ✅ |  |  |  |
| Artifact schema |  | ✅ |  | ✅ |  |  |  |
| Figma/Notion/Meta sync |  |  | ✅ | ✅ |  |  |  |
| Tracing spans |  |  | ✅ | ✅ |  |  |  |
| Graceful degradation |  | ✅ | ✅ | ✅ |  |  |  |
| Transient retries |  |  | ✅ |  |  | ✅ |  |
| Runtime SLA |  |  |  |  | ✅ |  |  |
| Secret handling |  |  | ✅ |  |  |  | ✅ |
| Idempotency |  |  |  |  |  | ✅ |  |
| Concurrent runs |  |  |  |  |  | ✅ |  |

## Test Environment Requirements

### Local Development

```bash
# Python environment
python 3.11+
pip install pytest pytest-cov pytest-httpserver responses pytest-benchmark pytest-asyncio

# Test data
tests/data/archives/sample_small.csv         # ~100 rows, representative
tests/data/archives/sample_large.csv         # ~10k rows, performance baseline
tests/fixtures/baseline_kpis.json            # Expected KPI values (tolerance ±5%)

# Mock services
Mock HTTP servers for Figma, Notion, Meta (pytest-httpserver)
Local OTLP collector (jaeger-all-in-one or lightweight test double)

# Environment toggle
ANALYTICS_ENABLE_FIGMA=true/false
ANALYTICS_ENABLE_NOTION=true/false
ANALYTICS_ENABLE_META=true/false
ANALYTICS_ENABLE_TRACING=true/false
FIGMA_TOKEN, NOTION_API_KEY, META_ACCESS_TOKEN (set/unset to test secret gating)
```

### CI Environment

**Job: `ci-analytics-tests`** (runs on PRs)
- Unit + integration tests (mocked externals)
- mypy type-check
- Coverage threshold ≥90%
- Runtime <5 minutes

**Job: `nightly-analytics-e2e`** (scheduled, runs on develop/main)
- Full E2E with sample_large.csv
- Real (mocked) integrations
- Performance profiling
- Artifact upload to workflow artifacts
- Runtime <30 minutes

### Fixtures

```yaml
Datasets:
  - sample_small.csv: 100 rows, dates 2024-01-01 to 2024-12-31
  - sample_large.csv: 10k rows, same date range
  - baseline_kpis.json: expected values for sample_small
    example: { "total_revenue": 1250000.50, "avg_deal_size": 15234.20, ... }

Mock Responses:
  - mock_responses/figma.json: success response
  - mock_responses/notion.json: page_id response
  - mock_responses/meta.json: event_id response

Environment Fixtures (pytest):
  - mock_figma_server: pytest fixture, HTTP server on :5000
  - mock_notion_server: pytest fixture, HTTP server on :5001
  - mock_meta_server: pytest fixture, HTTP server on :5002
  - mock_otel_collector: pytest fixture, OTLP receiver on :4317
  - analytics_env: pytest fixture, sets/unsets secret tokens and integration flags

Test Helpers:
  - assert_artifacts_exist(path, schema_file)
  - assert_kpis_within_tolerance(computed, baseline, tolerance=0.05)
  - assert_no_secrets_in_logs(log_stream, secrets_list)
  - capture_trace_spans(otel_mock) → list of spans with attributes
```

## Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| **External integrations fail unpredictably** | Pipeline abort, no KPI export | Medium | Mock all externals; test graceful degradation; implement retry logic with exponential backoff |
| **KPI calculation regressions** | Silent data corruption, wrong metrics | Medium | Baseline snapshot testing; unit tests >90% coverage; hypothesis property-based tests for edge cases |
| **Secrets leak in logs or artifacts** | Credential exposure, security incident | Medium | Regex audit of log output; sanitization function in place; secrets stored in GitHub Secrets, not repo |
| **Performance SLA miss (>20 min)** | Pipeline timeout in scheduled job; missed reporting window | Medium | Benchmark on every PR; set alerts for >15 min runtime; profile CPU/memory; optimize top-K slow paths |
| **Tracing context lost in async batches** | Observability blind spots, harder to debug | Low | Inject context before async tasks; verify span attributes in integration tests; fallback logging if tracing unavailable |
| **Concurrency/idempotency bugs (same run_id twice)** | Duplicate KPIs, corrupted state | Low | Atomic file writes; test idempotent re-run; ensure artifact paths include run_id; validate final state deterministic |

## Key Checklist Items

**Pre-Test**:
- [ ] Test data files present in `tests/data/archives/`
- [ ] `baseline_kpis.json` and tolerance values reviewed and approved
- [ ] Mock services configured and tested
- [ ] CI job templates created (`ci-analytics-tests`, `nightly-analytics-e2e`)
- [ ] GitHub Secrets for test tokens (`FIGMA_TOKEN`, `NOTION_API_KEY`, `META_ACCESS_TOKEN`) set

**Test Execution**:
- [ ] All unit tests pass (A-01 to H-02)
- [ ] Integration tests pass (mocked externals)
- [ ] E2E test passes on sample_small and sample_large
- [ ] Performance benchmark passes (runtime <20 min)
- [ ] Security audit (no secrets in logs) passes
- [ ] mypy and coverage thresholds met

**Post-Test**:
- [ ] Test results and artifacts uploaded to workflow artifacts
- [ ] Coverage report reviewed (target >90%)
- [ ] Performance trends analyzed (no regression)
- [ ] Issues documented in GitHub Issues with `ci/test` label
- [ ] Test documentation updated if new patterns discovered

## Test Exit Criteria

**Must Have** (Gate PR merge):
- All smoke tests pass (A-01, A-02)
- All KPI correctness tests pass (B-01)
- All security tests pass (F-01)
- All CI/config tests pass (H-01, H-02)
- Coverage ≥90%
- mypy clean (no new errors)
- Pylint ≥8.0

**Should Have** (Nightly gating):
- All integration tests pass (C-01 to C-04)
- All tracing tests pass (D-01, D-02)
- E2E test passes (I-01)
- Performance SLA met (<20 min for sample_small)
- No secrets in logs (F-01 audit)

**Nice to Have** (Future sprints):
- Robustness/retry tests (E-01, E-02)
- Edge case coverage (B-02, B-03)
- Concurrency tests (G-02)
- Performance benchmarking on larger datasets
- Historical trend analysis and alerts

---

**Approved By**: QA Lead  
**Test Environment**: Local + CI/CD  
**Estimated Effort**: 40 hours (planning + implementation + automation)  
**Sprint Schedule**: Sprint 0 (2 days) → Sprint 1 (5 days) → Sprint 2 (1 week) + Ongoing
