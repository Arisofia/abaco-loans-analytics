'use client'

import { useMemo, useState } from 'react'
import styles from './analytics.module.css'
import type { LoanRow } from '@/types/analytics'
import { processLoanRows } from '@/lib/analyticsProcessor'
import { LoanUploader } from './LoanUploader'
import { PortfolioHealthKPIs } from './PortfolioHealthKPIs'
import { TreemapVisualization } from './TreemapVisualization'
import { GrowthPathChart } from './GrowthPathChart'
import { RollRateMatrix } from './RollRateMatrix'
import { ExportControls } from './ExportControls'

const DEFAULT_SAMPLE: LoanRow[] = [
  {
    loan_amount: 120000,
    appraised_value: 200000,
    borrower_income: 90000,
    monthly_debt: 1200,
    loan_status: 'current',
    interest_rate: 5.2,
    principal_balance: 115000,
    dpd_status: 'current',
  },
  {
    loan_amount: 250000,
    appraised_value: 320000,
    borrower_income: 140000,
    monthly_debt: 2500,
    loan_status: '30-59 days past due',
    interest_rate: 6.4,
    principal_balance: 230000,
    dpd_status: 'bucket_30',
  },
]

export function AnalyticsDashboard() {
  const [loanData, setLoanData] = useState<LoanRow[]>(DEFAULT_SAMPLE)

  const analytics = useMemo(() => processLoanRows(loanData), [loanData])

  return (
    <div className={styles.container}>
      <LoanUploader onData={setLoanData} />
      <PortfolioHealthKPIs kpis={analytics.kpis} />
      <TreemapVisualization entries={analytics.treemap} />
      <GrowthPathChart projection={analytics.growthProjection} />
      <RollRateMatrix rows={analytics.rollRates} />
      <ExportControls analytics={analytics} />
    </div>
  )
}
