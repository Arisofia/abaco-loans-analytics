import type { LoanRow, ProcessedAnalytics } from '@/types/analytics'

export function processedAnalyticsToCSV(analytics: ProcessedAnalytics): string {
  const rows = analytics.loans.map((loan) => ({
    ...loan,
    ltv: ((loan.loan_amount / Math.max(loan.appraised_value, 1)) * 100).toFixed(1),
  }))

  const headers: (keyof LoanRow | 'ltv')[] = [
    'loan_amount',
    'appraised_value',
    'borrower_income',
    'monthly_debt',
    'loan_status',
    'interest_rate',
    'principal_balance',
    'dpd_status',
    'ltv',
  ]

  if (rows.length === 0) {
    return headers.join(',')
  }

  const csvRows = rows.map((row) => headers.map((key) => row[key]).join(','))
  return [headers.join(','), ...csvRows].join('\n')
}

export function processedAnalyticsToJSON(analytics: ProcessedAnalytics): string {
  return JSON.stringify(
    {
      kpis: analytics.kpis,
      treemap: analytics.treemap,
      rollRates: analytics.rollRates,
      growthProjection: analytics.growthProjection,
    },
    null,
    2
  )
}
