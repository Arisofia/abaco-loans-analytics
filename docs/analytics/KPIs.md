# KPI Catalog

Each KPI includes owner, source, refresh cadence, thresholds, drill-down, runbook, and next-best action.

| KPI | Definition | Owner | Source | Thresholds | Drill-down | Runbook |
| --- | --- | --- | --- | --- | --- | --- |
| NPL% / PAR30/60/90 | Outstanding balance 30/60/90+ days past due | Risk Ops | Loans fact + aging view | Amber >3%, Red >5% | Delinquent accounts table with cohort filters | `runbooks/kpi-breach.md` |
| LGD / ECL | Loss given default and expected credit loss | Risk Modeling | Models + write-off table | Red if variance >10% vs plan | Model version comparison, segment loss curves | `runbooks/kpi-breach.md` |
| Approval Rate | Approved apps / total apps | Credit Policy | Applications fact | Amber <40%, Red <35% | Funnel by channel/segment | `runbooks/ingestion-failure.md` |
| Auto-decision Rate | % auto-approved/-declined | Credit Ops | Decision engine logs | Amber <70% | Rule hit table, manual override queue | `runbooks/kpi-breach.md` |
| TAT (Decision) | Median time to decision | Credit Ops | Decision logs | Red > 60s | Latency by step | `runbooks/ingestion-failure.md` |
| Roll Rate Matrix | Transitions between delinquency buckets | Collections | Payments + aging | Red if roll-forward +5% vs baseline | Heatmap → loan list per cell | `runbooks/kpi-breach.md` |
| Cure Rate | % delinquent loans cured per period | Collections | Payments | Red < target by 3pp | Segment table (agent, bucket, cohort) | `runbooks/kpi-breach.md` |
| Promise-to-Pay Kept | Kept PTPT / total PTPT | Collections | Promise logs | Red <80% | Agent and borrower drill-down | `runbooks/kpi-breach.md` |
| CAC / LTV | Acquisition cost vs lifetime value | Growth | Marketing + repayment | Red if CAC/LTV >0.3 | Channel table, cohort profitability | `runbooks/kpi-breach.md` |
| Data Quality | Freshness, completeness, duplicates, schema drift | Data Engineering | Pipelines + monitors | Red if freshness >1h or null %>1% | Failed checks, offending rows | `runbooks/schema-drift.md` |

## Actionability rules
- Every chart links to a drill-down table and its runbook. Next-best action is documented per KPI (collections playbook, credit tweak, data fix).
- Owners approve KPI definition changes via PRs; PR template requires “KPI impact” and “data sources touched”.
- Alerts route to the owner’s channel with SLA and runbook link; MTTR/MTTD tracked in postmortems.

## Continuous learning
- For KPI breaches or model drift: open postmortem, capture cause/fix/prevention, add tests/alerts, and record MTTR/MTTD. Link postmortem to relevant runbook.
