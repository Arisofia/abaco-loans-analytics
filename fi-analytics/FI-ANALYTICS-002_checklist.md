# FI-ANALYTICS-002: Test Checklist

## Overview

**Total Test Cases**: 22  
**Critical**: 6  
**High**: 10  
**Medium**: 6  
**Automation Coverage**: 95% (21 automated, 1 partial)

---

## Test Cases

| ID | Title | Priority | Type | Automation Candidate | Pass |
|---|---|---|---|---|---|
| **SMOKE & SANITY** |
| A-01 | Pipeline smoke test: execute with sample_small.csv → completes successfully (exit 0) | Critical | Functional | Yes | ☐ |
| A-02 | Output artifacts existence and schema validation (kpi_results.json, metrics.csv) | Critical | Functional | Yes | ☐ |
| **KPI CORRECTNESS & EDGE CASES** |
| B-01 | KPI calculation baseline match: computed values within tolerance (±5%) of baseline_kpis.json | Critical | Functional | Yes | ☐ |
| B-02 | KPI boundary values & null handling: dataset with nulls/zeros processes without exception | High | Functional | Yes | ☐ |
| B-03 | Performance: sample_large.csv (10k rows) completes within SLA (20 minutes) | High | Performance | Yes | ☐ |
| **INTEGRATION (MOCKED)** |
| C-01 | Figma sync success: mocked endpoint returns OK, pipeline records success flag | High | Integration | Yes | ☐ |
| C-02 | Notion sync success: mocked endpoint creates page, pipeline logs success | High | Integration | Yes | ☐ |
| C-03 | Meta sync graceful degradation: mocked endpoint returns 500, pipeline logs error & continues | High | Integration | Yes | ☐ |
| C-04 | All integrations missing (no tokens set): pipeline runs, marks integrations as skipped | High | Integration | Yes | ☐ |
| **TRACING & OBSERVABILITY** |
| D-01 | Tracing spans emitted: test collector receives spans with job_name, run_id, client_id attributes | High | Integration | Yes | ☐ |
| D-02 | Tracing fallback: when tracing lib missing/misconfigured, pipeline logs mock messages & completes | Medium | Integration | Yes | ☐ |
| **ROBUSTNESS & RETRIES** |
| E-01 | External integration transient error + retry: mock responder fails 2x, succeeds 3rd request with backoff | High | Robustness | Yes | ☐ |
| E-02 | Rate limiting on artifact upload: pipeline retries rate-limited responses & succeeds eventually | High | Robustness | Yes | ☐ |
| **SECURITY & SECRETS** |
| F-01 | Secrets not leaked in logs: scan log output for secret substrings (FIGMA_TOKEN, etc.) | Critical | Security | Yes | ☐ |
| F-02 | Secret validation: missing required secrets triggers warnings, skips integration without crash | Medium | Security | Yes | ☐ |
| **FAILURE MODES / RESUMPTION / IDEMPOTENCY** |
| G-01 | Partial failure mid-run: exception during processing, re-run produces identical artifacts (no duplicates) | High | Robustness | Yes | ☐ |
| G-02 | Concurrent runs with same run_id: outputs remain deterministic (no corruption, no dups) | Medium | Robustness | Partial | ☐ |
| **CI & CONFIG CHECKS** |
| H-01 | Unit tests for KPI functions: >90% coverage, all regression tests pass | Critical | Regression | Yes | ☐ |
| H-02 | mypy type-check: analytics modules pass mypy strict mode, no new type errors on PR | Critical | Regression | Yes | ☐ |
| **END-TO-END ACCEPTANCE** |
| I-01 | Full E2E with sample dataset + mocked integrations: artifacts, traces, & notifications correct | High | Integration | Yes | ☐ |

---

## Priority Breakdown

### Critical (6)
Must pass to gate PR merge and block deployment.
- A-01: Smoke test
- A-02: Artifact schema
- B-01: KPI correctness baseline
- F-01: Secrets audit
- H-01: Unit test coverage
- H-02: mypy validation

### High (10)
Nightly gating; required for release candidate.
- B-02, B-03, C-01, C-02, C-03, C-04, D-01, E-01, E-02, G-01, I-01

### Medium (6)
Nice to have; tracked as tech debt.
- D-02, F-02, G-02

---

## Automation Coverage

| Category | Count | Automated | Partial | Manual |
|---|---|---|---|---|
| Smoke & Sanity | 2 | 2 | — | — |
| KPI & Correctness | 3 | 3 | — | — |
| Integration | 4 | 4 | — | — |
| Tracing | 2 | 2 | — | — |
| Robustness | 4 | 3 | 1 | — |
| Security | 2 | 2 | — | — |
| CI & Config | 2 | 2 | — | — |
| E2E | 1 | 1 | — | — |
| **TOTAL** | **22** | **21** | **1** | **0** |

**Coverage**: 95% (21 automated, 1 partial manual verification for G-02 concurrency)

---

## Execution Phases

### Sprint 0 (Days 1–2)
**Goal**: Baseline smoke, unit, and regression tests  
**Tests**: A-01, A-02, B-01, B-02, H-01, H-02  
**Effort**: 8 hours  
**Status**: Foundation for all subsequent phases

### Sprint 1 (Days 3–7)
**Goal**: Integration with mocked externals and tracing  
**Tests**: C-01, C-02, C-03, C-04, D-01, D-02, F-01, F-02  
**Effort**: 12 hours  
**Status**: Enables PR validation on integrations

### Sprint 2 (Week 2)
**Goal**: Robustness, retry, performance, and E2E  
**Tests**: B-03, E-01, E-02, G-01, G-02, I-01  
**Effort**: 16 hours  
**Status**: Full nightly E2E with performance tracking

### Ongoing
**Goal**: Maintenance, benchmarking, and optimization  
**Tasks**: Monitor CI success rate, benchmark trends, update baselines

---

## Notes

- **Tolerance**: KPI baseline tolerance set to ±5% (configurable per KPI type; review with data team)
- **SLA**: 20 minutes for sample_small; 60+ minutes acceptable for sample_large (nightly only)
- **Secrets**: Test with masked tokens in GitHub Actions; use local `.env.test` for local runs (never commit)
- **Mocking**: All external HTTP endpoints mocked in CI; option to run against sandbox endpoints in nightly job
- **Tracing**: OTLP collector test double (`tests/fixtures/mock_otel_collector.py`) sufficient; no Jaeger backend required
