# ABACO — Loan Analytics Platform

Arquitectura:

- **apps/web**: Next.js dashboard corporativo.
- **apps/analytics**: pipelines de Python para riesgo, scoring y KPIs.
- **infra/azure**: scripts de despliegue Azure.
- **data_samples**: datasets anonimizados para desarrollo.

Integraciones disponibles:

- Azure SQL / Cosmos / Storage
- Supabase
- Vercel
- OpenAI / Gemini / Claude
- SonarCloud
- GitHub Actions

Consulta `docs/integration-readiness.md` para verificar el estado de cada integración y las comprobaciones previas que debes ejecutar antes de usarlas.

## ContosoTeamStats

This repository contains ContosoTeamStats, a .NET 6 Web API for managing sports teams that ships with Docker, Azure deployment scripts, SendGrid/Twilio integrations, and SQL Server migrations. Follow docs/ContosoTeamStats-setup.md for local setup, secrets, database provisioning, and container validation.

See docs/Analytics-Vision.md for the analytics vision, Streamlit blueprint, and the agent-ready narrative that keeps every KPI, scenario, and AI prompt aligned with our fintech-grade delivery.

Use `docs/analytics/kpi-traceability.md` to enforce KPI traceability, dashboard contracts, and GitHub workflows (assignee @codex;
reviewers @sonarqube, @coderabbit, and @sourcery) so every change remains auditable, actionable, and secure.

## KPI catalog and runbooks

Consulta `docs/analytics/KPIs.md` para la taxonomía de KPIs, propietarios, orígenes de datos, umbrales y enlaces a dashboards, tablas de drill-down y runbooks (`docs/analytics/runbooks`). Usa `docs/analytics/dashboards.md` para la guía de visualizaciones y alertas.

### Variables de entorno (alertas y drill-down)

- `NEXT_PUBLIC_ALERT_SLACK_WEBHOOK`: webhook de Slack para alertas (red/amber).
- `NEXT_PUBLIC_ALERT_EMAIL`: correo de alertas si Slack no está disponible.
- `NEXT_PUBLIC_DRILLDOWN_BASE_URL`: base URL para tablas de drill-down (cola de cobranzas, cohortes de mora, errores de ingesta).

Configura estas variables en tu despliegue (Vercel/Azure) y en `.env.local` durante desarrollo.

## Copilot Enterprise workflow

Use `docs/Copilot-Team-Workflow.md` when inviting your team to Copilot, documenting the validation and security workflows, and keeping the Azure, GitHub Actions, and KPI checklist aligned with your 30-day Enterprise trial (App Service F1, ACR Basic, and free Azure security tiers). The doc includes prompts you can reuse whenever Copilot is guiding changes.

## Fitten Code AI 编程助手

Para integrar Fitten Code AI en este monorepo (local y GitHub), consulta `docs/Fitten-Code-AI-Manual.md`, que cubre la introducción al producto, instalación, integración, preguntas frecuentes y pruebas de inferencia local.

## MCP configuration

Use `docs/MCP_CONFIGURATION.md` to add MCP servers via the Codex CLI or by editing `config.toml`, including examples for Context7, Figma, Chrome DevTools, and how to run Codex itself as an MCP server.

## Deno helper

The repository exposes a tiny Deno helper at `main.ts` that verifies the expected directories before you execute tooling such as Fitten or analytics scripts. Run it with:

```sh
deno run --allow-all main.ts
```

`--unstable` is no longer needed in Deno 2.0; only include the specific `--unstable-*` flags when you actually depend on unstable APIs.

## Troubleshooting VS Code Zencoder extension

If you see `Failed to spawn Zencoder process: ... zencoder-cli ENOENT` while working in VS Code, follow the remediation checklist in `docs/Zencoder-Troubleshooting.md` to reinstall the extension and restore the missing binary.
