# ABACO — Loan Analytics Platform

## Architecture

- **apps/web**: Next.js corporate dashboard.
- **apps/analytics**: Python pipelines for risk, scoring, and KPIs.
- **infra/azure**: Azure deployment scripts.
- **data_samples**: anonymized datasets for development.
## Available integrations

- Azure SQL / Cosmos / Storage
- Supabase
- Vercel
- OpenAI / Gemini / Claude
- SonarCloud
- GitHub Actions
See `docs/integration-readiness.md` to verify the status of each integration and the pre-flight checks you should run
before using them.

## ContosoTeamStats

This repository includes ContosoTeamStats, a .NET 6 Web API for managing sports teams that ships with Docker, Azure
deployment scripts, SendGrid/Twilio integrations, and SQL Server migrations. Follow `docs/ContosoTeamStats-setup.md`
for local setup, secrets, database provisioning, and container validation.

See `docs/Analytics-Vision.md` for the analytics vision, Streamlit blueprint, and agent-ready narrative that keeps each
KPI, scenario, and AI prompt aligned with our fintech-grade delivery.

For governance, traceability, and GitHub-first review flows on KPIs and dashboards, follow
`docs/analytics/governance.md`.

## KPI catalog and runbooks

See `docs/analytics/KPIs.md` for the KPI taxonomy, owners, data sources, thresholds, and links to dashboards, drill-down
tables, and runbooks (`docs/analytics/runbooks`). Use `docs/analytics/dashboards.md` as a guide for visualizations and
alerts.

### Environment variables (alerts and drill-down)

- `NEXT_PUBLIC_ALERT_SLACK_WEBHOOK`: Slack webhook for red/amber alerts.
- `NEXT_PUBLIC_ALERT_EMAIL`: alert email if Slack is unavailable.
- `NEXT_PUBLIC_DRILLDOWN_BASE_URL`: base URL for drill-down tables (collections queue, delinquency cohorts, ingestion errors).
Set these variables in your deployment (Vercel/Azure) and in `.env.local` during development.

## Copilot Enterprise workflow

Use `docs/Copilot-Team-Workflow.md` when inviting your team to Copilot, documenting validation and security flows, and
keeping the Azure, GitHub Actions, and KPI checklists aligned during the 30-day Enterprise trial (App Service F1, ACR
Basic, and Azure’s free security tiers). The document includes reusable prompts for Copilot-guided changes.

## Fitten Code AI assistant

To integrate Fitten Code AI in this monorepo (local and GitHub), see `docs/Fitten-Code-AI-Manual.md`, which covers the
product introduction, installation, integration, FAQs, and local inference tests.

## MCP configuration

Use `docs/MCP_CONFIGURATION.md` to add MCP servers via the Codex CLI or by editing `config.toml`, with examples for
Context7, Figma, Chrome DevTools, and how to run Codex as an MCP server.

## Deno helper

The repo includes a lightweight helper in `main.ts` that verifies expected directories before running tools like Fitten
or analytics scripts. Run it with:

```sh
deno run --allow-all main.ts
```

`--unstable` is no longer required in Deno 2.0; include `--unstable-*` flags only when you rely on unstable APIs.

## VS Code Zencoder extension troubleshooting

If you see `Failed to spawn Zencoder process: ... zencoder-cli ENOENT` in VS Code, follow the remediation checklist in
`docs/Zencoder-Troubleshooting.md` to reinstall the extension and restore the missing binary.

## Java & Gradle

The Gradle build is configured for JDK **21** via the toolchain in `build.gradle`. Running Gradle with preview JDKs
(e.g., JDK 25) is not compatible with the current wrapper (8.10) and will fail during project sync. If your IDE picks a
newer JDK by default, switch the Gradle JVM to JDK 21 (or another supported LTS) and ensure `JAVA_HOME` points to that
installation.
