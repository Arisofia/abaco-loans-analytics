# Analytics Governance & Traceability

Goal: every KPI, dashboard, and alert is auditable, reproducible, and mapped to accountable owners with clear decision rights.

## Roles and decision rights
- **Data Engineering (Integrator):** owns data contracts, lineage, SLAs, and PII controls; approves schema changes and incident closures related to data quality.
- **Risk & Collections (RiskAnalyst, Sentinel):** own credit/collections KPIs, accept/reject threshold changes, and sign off on playbooks tied to credit policy or outreach cadence.
- **Growth (GrowthCoach):** owns CAC/LTV economics, channel mix assumptions, and promotion guardrails; approves funnel KPI changes.
- **Platform (PlatformAgent):** owns decisioning uptime, latency, and auto-decision coverage; approves any logic/policy toggle impacting TAT and approval outcomes.
- **Analytics Enablement:** maintains dashboards, alert routing tables, drill-down coverage, and documentation; enforces review checklists and GitHub workflow standards.

## Traceability workflow (GitHub-first)
1. **Change ticket:** open an issue labelled `kpi-change` or `dashboard-change` with scope, owner, data sources, and expected KPI movement.
2. **Branch policy:** include ticket ID in branch name; enable required status checks (tests + Sonar + formatting) and code owners for affected domains.
3. **PR template:** document KPI impact, data sources touched, alert updates, and rollout/rollback steps. Link to runbooks and dashboards touched.
4. **Review gates:** at least one domain owner + Analytics Enablement approval; Sonar clean-as-you-go (no new smells, duplicated code, or coverage drops).
5. **Audit log:** merge commit references ticket and includes links to dashboards, drill-down tables, and alert routes. Post-merge runbook updates are part of the same PR.

## Measurement standards
- **Lineage:** every KPI card includes source tables/views, freshness timestamp, and last transformation commit SHA.
- **Thresholds:** stored in config with owner + rationale; changes require PR and alert update. Track MTTR/MTTD per KPI.
- **Drill-down coverage:** each chart has a linked table with segment filters, runbook link, and action buttons (e.g., outreach, rule tweak).
- **Versioning:** models, features, and KPI calculations are versioned; dashboards show the active version and changelog link.

## Compliance & security
- Enforce PII masking in drill-down tables; only role-based access can view unmasked identifiers.
- Retain alert/event logs for audit; ensure alert payloads avoid PII and include runbook URLs.
- Data export/download follows least-privilege and is logged; default exports are aggregated or tokenized.
- Secrets live in vault-backed CI/CD; .env files excluded from commits. Rotate keys after incidents.

## Continuous learning loop
- After breaches or incidents: publish a postmortem, add automated tests/monitors, and document permanent fixes.
- Quarterly: review KPI catalog for relevance, recalibrate thresholds, and archive deprecated metrics with rationale.
- Keep a "known gaps" section in dashboards to transparently show pending data sources or modeling work.

## Dashboard & alert playbooks
- Exec dashboard highlights NSM, NPL/PAR trend, book growth vs target, CAC/LTV, approval rate, and ECL vs plan, each with drill-down and owner tags.
- Risk Ops dashboard surfaces roll-rate matrix, PD/LGD calibration, exceptions aging, auto-decision rate, and TAT with runbook shortcuts.
- Collections dashboard tracks cure rate, promise-to-pay kept, agent productivity, and queue health with reassignment and cadence-change actions.
- Product funnel dashboard monitors ingest/parse success, drop-off by step, and schema drift; alerts route to Data Engineering + Platform.
- Data quality dashboard displays freshness, completeness, duplicates, schema drift, and PII checks; red alerts page Data Engineering.
