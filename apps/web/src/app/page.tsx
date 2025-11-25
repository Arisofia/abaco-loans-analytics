import styles from './page.module.css'

type Metric = {
  title: string
  value: string
  delta: string
  detail: string
}

type Stage = {
  name: string
  volume: string
  conversion: number
  lift: string
}

type RiskItem = {
  name: string
  exposure: string
  trend: string
}

type Initiative = {
  name: string
  owner: string
  status: string
}

const metrics: Metric[] = [
  {
    title: 'Active portfolio',
    value: '$48.6M',
    delta: '+8.3% QoQ',
    detail: 'Low default exposure with disciplined origination',
  },
  {
    title: 'Net yield',
    value: '12.4%',
    delta: '+40 bps MoM',
    detail: 'After cost of funds and servicing efficiency',
  },
  {
    title: 'Collections efficiency',
    value: '96.1%',
    delta: '+1.2 pts',
    detail: 'Direct debit penetration and early-cure initiatives',
  },
  {
    title: 'Acquisition CAC / LTV',
    value: '1 : 5.8',
    delta: 'Target < 1 : 4',
    detail: 'Paid media optimized for risk-adjusted approvals',
  },
]

const stages: Stage[] = [
  { name: 'Applications', volume: '12,420', conversion: 100, lift: '+6.2%' },
  { name: 'Pre-approved', volume: '8,310', conversion: 67, lift: '+3.5%' },
  { name: 'Funded', volume: '5,120', conversion: 41, lift: '+2.1%' },
  { name: 'On-book M1+', volume: '4,910', conversion: 39, lift: '-0.4%' },
]

const riskHeat: RiskItem[] = [
  { name: 'SME working capital', exposure: '$22.4M', trend: 'Stable risk, monitor FX' },
  { name: 'Salary advance', exposure: '$11.8M', trend: 'Improving vintage curve' },
  { name: 'Auto loans', exposure: '$9.6M', trend: 'Watchlist dealers reduced 28%' },
]

const initiatives: Initiative[] = [
  { name: 'AI underwriting refresh', owner: 'Risk', status: 'Deploying' },
  { name: 'Collections digital playbook', owner: 'CX', status: 'Live' },
  { name: 'Treasury laddering', owner: 'Finance', status: 'In-flight' },
]

export default function Home() {
  return (
    <div className={styles.page}>
      <header className={styles.hero}>
        <div className={styles.heroText}>
          <p className={styles.tag}>ABACO — Loan Intelligence</p>
          <h1 className={styles.heading}>Precision growth with auditable, real-time insights.</h1>
          <p className={styles.subtitle}>
            Operational control, embedded risk discipline, and revenue clarity for digital lending
            teams across credit, product, finance, and collections.
          </p>
          <div className={styles.pills}>
            <span>Predictive risk</span>
            <span>Unit economics</span>
            <span>Collections</span>
            <span>Funding</span>
          </div>
        </div>
        <div className={styles.heroCard}>
          <div className={styles.heroRow}>
            <div>
              <p className={styles.label}>Run-rate revenue</p>
              <p className={styles.primaryValue}>$6.8M</p>
            </div>
            <div className={styles.pillPositive}>+14.6% QoQ</div>
          </div>
          <p className={styles.helper}>Risk-adjusted yield net of impairments and servicing.</p>
          <div className={styles.divider} />
          <div className={styles.heroGrid}>
            <div>
              <p className={styles.label}>Cost of risk</p>
              <p className={styles.secondaryValue}>2.9%</p>
            </div>
            <div>
              <p className={styles.label}>NPL 90</p>
              <p className={styles.secondaryValue}>1.3%</p>
            </div>
            <div>
              <p className={styles.label}>Capital buffer</p>
              <p className={styles.secondaryValue}>11.4%</p>
            </div>
          </div>
        </div>
      </header>

      <section className={styles.metrics} aria-label="Portfolio performance metrics">
        <h2 className={styles.srOnly}>Portfolio performance metrics</h2>
        {metrics.map((metric) => (
          <article key={metric.title} className={styles.card}>
            <div className={styles.cardHeader}>
              <p className={styles.label}>{metric.title}</p>
              <span className={styles.delta}>{metric.delta}</span>
            </div>
            <p className={styles.cardValue}>{metric.value}</p>
            <p className={styles.helper}>{metric.detail}</p>
          </article>
        ))}
      </section>

      <section className={styles.grid}>
        <article className={styles.panel}>
          <header className={styles.panelHeader}>
            <div>
              <p className={styles.label}>Acquisition to book</p>
              <h2>Risk-calibrated funnel</h2>
            </div>
            <span className={styles.pillNeutral}>SLA monitored</span>
          </header>
          <div className={styles.stageList}>
            {stages.map((stage) => {
              const conversionWidth = Math.min(100, Math.max(0, stage.conversion))

              return (
                <div key={stage.name} className={styles.stageRow}>
                  <div>
                    <p className={styles.stageName}>{stage.name}</p>
                    <p className={styles.helper}>{stage.volume} customers</p>
                  </div>
                  <div className={styles.stageMeta}>
                    <div className={styles.stageBar}>
                      <span style={{ width: `${conversionWidth}%` }} />
                    </div>
                    <div className={styles.stageNumbers}>
                      <span>{stage.conversion}%</span>
                      <span className={styles.delta}>{stage.lift}</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </article>

        <article className={styles.panel}>
          <header className={styles.panelHeader}>
            <div>
              <p className={styles.label}>Risk radar</p>
              <h2>Exposure and actions</h2>
            </div>
            <span className={styles.pillPositive}>Audit ready</span>
          </header>
          <div className={styles.riskList}>
            {riskHeat.map((item) => (
              <div key={item.name} className={styles.riskItem}>
                <div>
                  <p className={styles.stageName}>{item.name}</p>
                  <p className={styles.helper}>{item.exposure}</p>
                </div>
                <span className={styles.trend}>{item.trend}</span>
              </div>
            ))}
          </div>
          <div className={styles.divider} />
          <div className={styles.initiatives}>
            {initiatives.map((initiative) => (
              <div key={initiative.name} className={styles.initiative}>
                <div>
                  <p className={styles.stageName}>{initiative.name}</p>
                  <p className={styles.helper}>{initiative.owner} lead</p>
                </div>
                <span className={styles.pillNeutral}>{initiative.status}</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </div>
  )
}
