import Link from 'next/link'
import { controls, metrics, products, steps } from './data'
import styles from './page.module.css'

export default function Home() {
  return (
    <div className={styles.page}>
      <header className={styles.hero}>
        <div className={styles.pill}>Growth & Risk Intelligence</div>
        <h1>Abaco Loans Analytics</h1>
        <p>
          A fintech-grade command center that blends underwriting precision, revenue acceleration,
          and regulatory confidence in one cohesive experience.
        </p>
        <div className={styles.actions}>
          <Link href="#demo" className={styles.primaryButton}>
            Schedule a demo
          </Link>
          <Link href="#products" className={styles.secondaryButton}>
            Explore products
          </Link>
        </div>
        <div className={styles.metrics}>
          {metrics.map((metric) => (
            <div key={metric.label} className={styles.metricCard}>
              <span className={styles.metricValue}>{metric.value}</span>
              <span className={styles.metricLabel}>{metric.label}</span>
            </div>
          ))}
        </div>
      </header>

      <section id="products" className={styles.section}>
        <div className={styles.sectionHeader}>
          <p className={styles.eyebrow}>Customer-centric growth</p>
          <h2>Build, fund, and protect every loan strategy</h2>
          <p className={styles.sectionCopy}>
            Abaco aligns acquisition, credit, collections, and treasury teams around shared KPIs
            with zero-friction visibility and auditable execution.
          </p>
        </div>
        <div className={styles.cardGrid}>
          {products.map((product) => (
            <div key={product.title} className={styles.card}>
              <h3>{product.title}</h3>
              <p>{product.detail}</p>
            </div>
          ))}
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <p className={styles.eyebrow}>Operational excellence</p>
          <h2>Compliance-first, automation-ready</h2>
          <p className={styles.sectionCopy}>
            Deploy with confidence using built-in governance, continuous monitoring, and clear
            accountabilities for every decision.
          </p>
        </div>
        <div className={styles.compliance}>
          <div className={styles.complianceList}>
            {controls.map((item) => (
              <div key={item} className={styles.checkItem}>
                <span className={styles.checkBullet} aria-hidden="true" />
                <span>{item}</span>
              </div>
            ))}
          </div>
          <div className={styles.auditBox}>
            <p className={styles.auditTitle}>Audit-ready by design</p>
            <ul>
              <li>Unified evidence across decisions, payments, and servicing.</li>
              <li>Exportable traces for regulators, investors, and partners.</li>
              <li>Service-level alerts with automated escalations.</li>
            </ul>
            <Link href="#demo" className={styles.primaryGhost}>
              Launch a pilot
            </Link>
          </div>
        </div>
      </section>

      <section id="demo" className={styles.section}>
        <div className={styles.sectionHeader}>
          <p className={styles.eyebrow}>Delivery playbook</p>
          <h2>From data to decisions in weeks</h2>
          <p className={styles.sectionCopy}>
            Guided onboarding, industrialized documentation, and observability to keep every sprint
            on budget and on time.
          </p>
        </div>
        <div className={styles.timeline}>
          {steps.map((step) => (
            <div key={step.label} className={styles.timelineStep}>
              <span className={styles.stepBadge}>{step.label}</span>
              <div>
                <h3>{step.title}</h3>
                <p>{step.copy}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
