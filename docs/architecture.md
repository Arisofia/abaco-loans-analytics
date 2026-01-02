# ABACO LOANS ANALYTICS - SYSTEM ARCHITECTURE

**Status**: 🟡 IN DISCOVERY (Updated January 1, 2026)
**Owner**: DevOps / Platform Engineering
**Last Updated**: 2026-01-01

---

## 1. DATA ARCHITECTURE (CRITICAL - NEEDS COMPLETION)

### Current State
🔴 **CRITICAL GAP**: Production database storage location is NOT DOCUMENTED

**Evidence Collected**:
- No Azure SQL Database in resource group
- No PostgreSQL/MySQL managed services detected
- No connection strings in App Service configuration
- Blob Storage accounts exist but unclear if used for structured data

### Questions to Answer
- [ ] Where are production loan records stored? (Database? Blob Storage files? External API?)
- [ ] What is the connection string for production data?
- [ ] How do data pipelines write transformed data?
- [ ] How does dashboard query KPIs for display?
- [ ] What is the data retention policy?

### Data Sources (Known)
| Source | Type | Purpose | Integration |
|--------|------|---------|-------------|
| Cascade API | External API | Loan origination data | Via `cascade_client.py` |
| HubSpot | External API | Customer/marketing data | Via `segment_manager.py` |
| Manual CSV uploads | File uploads | Financial statements, payment schedules | Via `data/raw/` folders |

### Data Storage Layers (To Be Determined)

#### Layer 1: Raw Data Storage
```
Status: ❌ UNKNOWN
Question: Where does raw Cascade/HubSpot data land?
  Option A: Azure Blob Storage (ADLS) - File-based
  Option B: PostgreSQL database - Structured
  Option C: Cosmos DB - NoSQL
  Option D: External (keep in APIs)
```

#### Layer 2: Processed Data Storage
```
Status: ❌ UNKNOWN
Question: Where are transformed KPIs stored?
  Option A: Same database as raw data
  Option B: Separate analytical database
  Option C: Blob Storage (Parquet files)
  Option D: Supabase (mentioned in code but not configured)
```

#### Layer 3: Cache/Query Layer
```
Status: ❌ UNKNOWN
Question: How does dashboard query data?
  Option A: Direct database queries
  Option B: API endpoints
  Option C: Pre-computed exports
  Option D: Real-time calculation from raw data
```

---

## 2. COMPUTE ARCHITECTURE

### Frontend (Dashboard)

**Type**: Streamlit/React Application
**Location**: Azure App Service - `abaco-analytics-dashboard`
**Status**: 🔴 OFFLINE (DNS_PROBE_FINISHED_NXDOMAIN)

**Configuration**:
```yaml
App Service Plan: ASP-AIMultiAgentEcosystemRG-b676
Tier: Basic B1 (🔴 SEVERELY UNDER-PROVISIONED for production)
Instance: LW1SDLWK0006XP (Status: Desconocido → restart pending)
Python: 3.12
Region: Canada Central
Health Check Path: /?page=health
Startup Command: bash startup.sh
```

**Environment Variables Configured**:
- HUBSPOT_API_KEY ✅
- OPENAI_API_KEY ✅
- SCM_DO_BUILD_DURING_DEPLOYMENT=1 ✅

**Missing Configuration**:
- DATABASE_URL / database connection string ❌
- SUPABASE_URL / SUPABASE_KEY ❌
- Storage account connection strings ❌

### Data Pipelines

**Orchestration**: GitHub Actions (Scheduled workflows)

**Pipeline Jobs**:
| Pipeline | Schedule | Status | Duration | Purpose |
|----------|----------|--------|----------|---------|
| `cascade_ingest.yml` | Daily 06:00 CET | 🔴 FAILING | 11s | Cascade loan data ingestion |
| `daily-ingest.yml` | Daily 07:00 CET | 🔴 FAILING | 16s | Daily data refresh |
| `kpi-daily.yml` | Daily 07:30 CET | 🔴 FAILING | 14s | KPI calculation |
| `meta_ingest.yaml` | Daily 08:00 CET | 🔴 FAILING | 19s | Meta marketing data |

**Pipeline Code Locations**:
- Orchestration: `src/pipeline/orchestrator.py`
- Ingestion: `src/abaco_pipeline/ingestion/`
- Transformation: `src/abaco_pipeline/transform/`
- Output: `src/abaco_pipeline/output/`

**Current Issues**:
- Very short runtimes (11-19 seconds) suggest immediate failures
- Likely root causes: authentication error, missing dependency, data validation failure

---

## 3. INTEGRATION ARCHITECTURE

### External Services

**Active Integrations**:
| Service | Type | Purpose | Key | Status |
|---------|------|---------|-----|--------|
| HubSpot | CRM API | Customer data, segments | HUBSPOT_API_KEY | ✅ Configured |
| OpenAI | LLM API | AI insights generation | OPENAI_API_KEY | ✅ Configured |
| Azure Key Vault | Secrets | Central secret management | aiagent-secrets-kv | ✅ Active |
| Application Insights | Monitoring | Logging & telemetry | abaco-insights | ✅ Deployed but minimal logging |

**Inactive Integrations** (referenced but not configured):
| Service | Purpose | Evidence | Status |
|---------|---------|----------|--------|
| Supabase | Database | Mentioned in code | ❌ No connection string |
| Slack | Notifications | Discussed in planning | ❌ No webhook |
| Notion | Documentation | Discussed in planning | ❌ No API key |
| Figma | Design sync | `.exports/` folder exists | ❌ Unknown status |
| Vercel | Hosting | `.vercel` folder exists | ⚠️ Unknown if active |

### Secrets Management

**Implemented**: Azure Key Vault (`aiagent-secrets-kv`)
**Issues**:
- GitHub Actions can't access Key Vault properly (requires proper authentication fix)
- Some secrets in App Service config instead of Key Vault
- CI/CD syntax error prevented credential passing

---

## 4. DEPLOYMENT ARCHITECTURE

### CI/CD Pipeline

**Status**: 🔴 BROKEN (Now Fixed - PROD-002)

**Tool**: GitHub Actions
**Issue**: Invalid secrets context syntax in `deploy-dashboard.yml`
**Fix Applied**: Replaced `if: ${{ secrets.AZURE_CREDENTIALS != '' }}` with proper output check

**Deployment Flow**:
```
1. Code push to main branch
2. GitHub Actions trigger (on dashboard/* or workflow changes)
3. Build: Install Python dependencies
4. Deploy: Push to Azure App Service
5. Health Check: Verify app responds on health endpoint
6. Notify: Comment on PR if failure
```

**Deployment Method**: Azure Deployment Center (GitHub integration)
**Publish Profile**: `secrets.AZURE_WEBAPP_PUBLISH_PROFILE`

---

## 5. INFRASTRUCTURE AS CODE

**Current State**: Bicep (Azure's IaC language)
**Main Template**: `infra/azure/main.bicep`
**Monitoring Config**: `infra/azure/monitoring-alerts.yaml`
**Deployment Script**: `scripts/deploy-monitoring-alerts.sh`

**Resources Managed**:
- App Service & App Service Plan
- Key Vault
- Application Insights
- Storage Accounts
- Managed Identities
- Function Apps

---

## 6. MONITORING & OBSERVABILITY

### Current Setup
- **Monitoring**: Azure Monitor + Application Insights
- **Dashboards**: None currently configured
- **Alerts**: None currently configured (PLANNED)
- **Logging**: Application Insights (minimal telemetry)

### Planned Setup (Week 1-2)
- [ ] Response time alerts (> 5 seconds)
- [ ] Error rate alerts (> 1% 5xx errors)
- [ ] Availability alerts (< 99%)
- [ ] Pipeline failure alerts
- [ ] Data quality alerts (row counts, schema validation)

### Audit & Compliance Logging
- **Audit Hooks Module**: `src/pipeline/audit_hooks.py` (IMPLEMENTED)
- **Features**:
  - Immutable audit logging (JSONL format)
  - Data lineage tracking
  - Access control audit trails
  - Compliance reporting

---

## 7. SECURITY & ACCESS CONTROL

### Azure RBAC
- **Key Vault Access**: Managed Identity (oidc-msi-*)
- **App Service**: System-assigned managed identity
- **Storage**: Azure RBAC roles

### Secrets Management
- **Location**: Azure Key Vault (`aiagent-secrets-kv`)
- **Rotation**: Manual (should be automated)
- **Access**: GitHub Actions (via secrets context - NOW FIXED)

### Branch Protection
- **Current**: ❌ None (main branch unprotected)
- **Recommended**:
  - Require pull requests
  - Require status checks to pass
  - Dismiss stale pull request approvals
  - Require code review from code owners

---

## 8. DISASTER RECOVERY & BACKUP

### Current State
- **Data Backup**: ❌ NOT DOCUMENTED
- **RTO Target**: 4 hours (per runbook)
- **RPO Target**: 4 hours (per runbook)
- **DR Plan**: 📄 See `docs/runbooks/data-loss.md`

### Backup Strategy (To Be Implemented)
- [ ] Daily database backups (automated)
- [ ] Cross-region blob storage replication
- [ ] Backup validation tests
- [ ] Recovery procedure runbooks

---

## 9. CAPACITY & SCALING

### Current State
- **App Service Tier**: Basic B1 (1 core, 1.75 GB RAM, $13/month)
- **Status**: 🔴 SEVERELY UNDER-PROVISIONED

### Scaling Plan
| Phase | Timeline | Tier | Cores | RAM | Est. Cost |
|-------|----------|------|-------|-----|-----------|
| Emergency | Now | Basic B1 | 1 | 1.75 GB | $13/mo |
| Stabilization | Week 1 | Standard S1 | 1 | 1.75 GB | $70/mo |
| Production | Week 2 | Premium P1V2 | 2 | 3.5 GB | $200/mo |
| High Availability | Week 4 | Premium P1V2 x 2 | 4 | 7 GB | $400/mo |

### Pipeline Parallelization
- **Current**: Sequential execution
- **Target**: Parallel ingestion (Cascade + HubSpot + Meta simultaneously)
- **Tools**: Azure Data Factory or GitHub Actions matrix builds

---

## 10. COMPLIANCE & GOVERNANCE

### Regulatory Requirements
- **Primary**: Fintech/Financial Services (loan data)
- **Frameworks**: ISO 27001, SOX, GDPR (if EU customers)

### Implemented Controls
- ✅ Data classification module (`src/data_classification.py`)
- ✅ Audit logging module (`src/pipeline/audit_hooks.py`)
- ✅ RBAC access control
- ✅ Secrets in Key Vault
- ✅ Risk register and runbooks

### Outstanding Controls
- [ ] Automated backups
- [ ] Encryption at rest verification
- [ ] Data retention policies
- [ ] Access audit reports
- [ ] Incident response automation

---

## 11. KNOWN ISSUES & ACTION ITEMS

### P0 - CRITICAL (Fix Today)
- [ ] Dashboard offline - DNS error (awaiting Azure instance restart)
- [ ] Data pipelines failing - root cause unknown (awaiting log review)
- [ ] Production database location unknown (awaiting clarification)

### P1 - HIGH (Fix This Week)
- [ ] App Service tier under-provisioned (upgrade to Standard S1)
- [ ] No monitoring/alerting configured
- [ ] No branch protection on main
- [ ] CI/CD secrets handling needs improvement
- [ ] Database connection configuration missing

### P2 - MEDIUM (Address in Phase 2)
- [ ] Geographic resource distribution inconsistent
- [ ] No disaster recovery plan
- [ ] No high availability (single instance)
- [ ] Integration documentation incomplete

---

## 12. NEXT STEPS

**Immediate (Next 2 Hours)**:
1. ✅ Deploy CI/CD fix (DONE)
2. Verify dashboard service restore (Azure Portal)
3. Review pipeline failure logs (GitHub Actions)
4. Provide production database connection details

**Short Term (This Week)**:
1. Document data architecture (this file - COMPLETE SECTION 1)
2. Set up monitoring and alerts
3. Enable branch protection
4. Configure automated backups
5. Upgrade App Service tier to Standard S1

**Medium Term (Weeks 2-4)**:
1. Implement high availability setup
2. Configure automated disaster recovery tests
3. Optimize pipeline performance with parallelization
4. Complete compliance control implementation
5. Create comprehensive runbooks for all failure scenarios

---

## References

- 📄 Risk Register: `docs/RISK_REGISTER.md`
- 📄 Emergency Response Plan: `EMERGENCY_RESPONSE_PLAN.md`
- 📄 Runbooks: `docs/runbooks/`
- 📄 Audit Integration Guide: `src/pipeline/AUDIT_INTEGRATION_GUIDE.md`
