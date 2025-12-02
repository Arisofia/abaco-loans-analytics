# ABACO — Loan Analytics Platform

## Arquitectura

- **apps/web**: Next.js dashboard corporativo.
- **apps/analytics**: pipelines de Python para riesgo, scoring y KPIs.
- **infra/azure**: scripts de despliegue Azure.
- **data_samples**: datasets anonimizados para desarrollo.
## Integraciones disponibles

- Azure SQL / Cosmos / Storage
- Supabase
- Vercel
- OpenAI / Gemini / Claude
- SonarCloud
- GitHub Actions
Consulta `docs/integration-readiness.md` para verificar el estado de cada integración y las comprobaciones previas que
debes ejecutar antes de usarlas.

## ContosoTeamStats

Este repositorio contiene ContosoTeamStats, una API Web de .NET 6 para gestionar equipos deportivos que incluye Docker,
scripts de despliegue en Azure, integraciones con SendGrid/Twilio y migraciones de SQL Server. Sigue
`docs/ContosoTeamStats-setup.md` para la configuración local, secretos, aprovisionamiento de base de datos y validación
de contenedores.

Consulta `docs/Analytics-Vision.md` para la visión analítica, el plano de Streamlit y la narrativa preparada para
agentes que mantiene cada KPI, escenario y prompt de IA alineados con nuestra entrega de nivel fintech.

Para gobernanza, trazabilidad y flujos de revisión GitHub-first en KPIs y dashboards, sigue
`docs/analytics/governance.md`.

## Catálogo de KPIs y runbooks

Consulta `docs/analytics/KPIs.md` para la taxonomía de KPIs, propietarios, orígenes de datos, umbrales y enlaces a
dashboards, tablas de drill-down y runbooks (`docs/analytics/runbooks`). Usa `docs/analytics/dashboards.md` como guía de
visualizaciones y alertas.

### Variables de entorno (alertas y drill-down)

- `NEXT_PUBLIC_ALERT_SLACK_WEBHOOK`: webhook de Slack para alertas (red/amber).
- `NEXT_PUBLIC_ALERT_EMAIL`: correo de alertas si Slack no está disponible.
- `NEXT_PUBLIC_DRILLDOWN_BASE_URL`: base URL para tablas de drill-down (cola de cobranzas, cohortes de mora, errores de ingesta).
Configura estas variables en tu despliegue (Vercel/Azure) y en `.env.local` durante desarrollo.

## Copilot Enterprise workflow

Usa `docs/Copilot-Team-Workflow.md` cuando invites a tu equipo a Copilot, documentes los flujos de validación y
seguridad, y mantengas alineada la checklist de Azure, GitHub Actions y KPIs durante tu prueba de 30 días de Enterprise
(App Service F1, ACR Basic y tiers de seguridad gratuitos de Azure). El documento incluye prompts reutilizables cuando
Copilot guíe los cambios.

## Fitten Code AI 编程助手

Para integrar Fitten Code AI en este monorepo (local y GitHub), consulta `docs/Fitten-Code-AI-Manual.md`, que cubre la
introducción al producto, instalación, integración, preguntas frecuentes y pruebas de inferencia local.

## MCP configuration

Usa `docs/MCP_CONFIGURATION.md` para agregar servidores MCP mediante la CLI de Codex o editando `config.toml`, con
ejemplos para Context7, Figma, Chrome DevTools y cómo ejecutar Codex como servidor MCP.

## Deno helper

El repositorio expone un helper ligero en `main.ts` que verifica los directorios esperados antes de ejecutar
herramientas como Fitten o scripts analíticos. Ejecútalo con:

```sh
deno run --allow-all main.ts
```

`--unstable` ya no es necesario en Deno 2.0; solo incluye los flags `--unstable-*` cuando dependas de APIs inestables.

## Solución de problemas con la extensión VS Code Zencoder

Si observas `Failed to spawn Zencoder process: ... zencoder-cli ENOENT` en VS Code, sigue la checklist de remediación en
`docs/Zencoder-Troubleshooting.md` para reinstalar la extensión y restaurar el binario faltante.

## Java & Gradle

La build de Gradle está configurada para JDK **21** mediante la toolchain en `build.gradle`. Ejecutar Gradle con JDKs en
versión preliminar (por ejemplo, JDK 25) no es compatible con el wrapper actual (8.10) y fallará durante la
sincronización del proyecto. Si tu IDE selecciona un JDK más reciente por defecto, cambia la JVM de Gradle a JDK 21 (u
otra versión LTS soportada) y asegúrate de que `JAVA_HOME` apunte a esa instalación. Para entornos que respetan
`.java-version`, el archivo raíz fija automáticamente el uso de JDK 21.
