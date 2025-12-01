import type { LoanRow, ProcessedAnalytics } from '@/types/analytics'

type LoanRowWithLtv = LoanRow & { ltv: string }

const loanHeaders: Array<keyof LoanRowWithLtv> = [
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

function escapeCsvValue(value: string): string {
  // Escape values containing quotes, commas, or any line breaks (CR, LF, or CRLF)
  if (/[",\r\n]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`
  }
  return value
}

export function processedAnalyticsToCSV(analytics: ProcessedAnalytics): string {
  const rows: LoanRowWithLtv[] = analytics.loans.map((loan) => ({
    ...loan,
    ltv: ((loan.loan_amount / Math.max(loan.appraised_value, 1)) * 100).toFixed(1),
  }))
  const headerRow = loanHeaders.join(',')
  if (!rows.length) {
    return headerRow
  }

  const csvRows = rows.map((row) =>
    loanHeaders
      .map((key) => {
        const value = row[key]
        return value === undefined ? '' : escapeCsvValue(String(value))
      })
      .join(',')
  )
  return [headerRow, ...csvRows].join('\n')
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
