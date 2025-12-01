import {
  LoanRow,
  ProcessedAnalytics,
  RollRateEntry,
  TreemapEntry,
  GrowthPoint,
} from '@/types/analytics'

const currencyRegex = /[^\d.-]/g

function splitCsvLine(line: string): string[] {
  const values: string[] = []
  let current = ''
  let inQuotes = false

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i]

    if (char === '"') {
      const nextChar = line[i + 1]
      if (inQuotes && nextChar === '"') {
        current += '"'
        i += 1
        continue
      }
      inQuotes = !inQuotes
      continue
    }

    if (char === ',' && !inQuotes) {
      values.push(current.trim())
      current = ''
      continue
    }

    current += char
  }

  values.push(current.trim())
  return values
}

function toNumber(value: string | number): number {
  if (typeof value === 'number') {
    return value
  }
  const cleaned = value.replace(currencyRegex, '')
  return Number(cleaned) || 0
}

export function parseLoanCsv(content: string): LoanRow[] {
  const lines = content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0)

  if (lines.length === 0) return []

  const header = splitCsvLine(lines[0]).map((col) => col.toLowerCase())
  const rows = lines.slice(1).map((line) => splitCsvLine(line))

  const requiredColumns = new Set([
    'loan_amount',
    'appraised_value',
    'borrower_income',
    'monthly_debt',
    'loan_status',
    'interest_rate',
    'principal_balance',
    'dpd_status',
  ])

  const headerMap = header.reduce<Record<string, number>>((acc, key, index) => {
    acc[key] = index
    return acc
  }, {})

  const hasAllColumns = [...requiredColumns].every((key) => headerMap[key] !== undefined)
  if (!hasAllColumns) return []

  return rows.map((parts) => {
    const record = header.reduce<Record<string, string>>((acc, key, index) => {
      acc[key] = parts[index]?.trim() ?? ''
      return acc
    }, {})

    return {
      loan_amount: toNumber(record.loan_amount),
      appraised_value: toNumber(record.appraised_value),
      borrower_income: toNumber(record.borrower_income),
      monthly_debt: toNumber(record.monthly_debt),
      loan_status: record.loan_status || 'unknown',
      interest_rate: toNumber(record.interest_rate),
      principal_balance: toNumber(record.principal_balance),
      dpd_status: record.dpd_status || '',
    }
  })
}

export function processLoanRows(rows: LoanRow[]): ProcessedAnalytics {
  const kpis = computeKPIs(rows)
  const treemap = buildTreemap(rows)
  const rollRates = buildRollRates(rows)
  const growthProjection = buildGrowthProjection(kpis.portfolioYield, kpis.loanCount)

  return {
    kpis,
    treemap,
    rollRates,
    growthProjection,
    loans: rows,
  }
}

function computeKPIs(rows: LoanRow[]) {
  const totalLoans = rows.length
  const delinquentStatuses = ['30-59 days past due', '60-89 days past due', '90+ days past due']
  const delinquentCount = rows.filter((row) => delinquentStatuses.includes(row.loan_status)).length
  const riskRate = totalLoans ? (delinquentCount / totalLoans) * 100 : 0

  const totalPrincipal = rows.reduce((sum, row) => sum + row.principal_balance, 0)
  const weightedInterest = rows.reduce(
    (sum, row) => sum + row.interest_rate * row.principal_balance,
    0
  )
  const portfolioYield = totalPrincipal ? (weightedInterest / totalPrincipal) * 100 : 0

  const averageLTV = rows.reduce(
    (sum, row) => sum + row.loan_amount / Math.max(row.appraised_value, 1),
    0
  )
  const averageDTI = rows.reduce((sum, row) => {
    const income = row.borrower_income / 12
    if (income <= 0) return sum
    return sum + row.monthly_debt / income
  }, 0)

  return {
    delinquencyRate: Number(riskRate.toFixed(2)),
    portfolioYield: Number(portfolioYield.toFixed(2)),
    averageLTV: Number(((averageLTV / Math.max(totalLoans, 1)) * 100).toFixed(1)),
    averageDTI: Number(((averageDTI / Math.max(totalLoans, 1)) * 100).toFixed(1)),
    loanCount: totalLoans,
  }
}

function buildTreemap(rows: LoanRow[]): TreemapEntry[] {
  const map: Record<string, number> = {}
  rows.forEach((row) => {
    map[row.loan_status] = (map[row.loan_status] || 0) + row.principal_balance
  })
  const colors = ['#C1A6FF', '#5F4896', '#22c55e', '#2563eb', '#0C2742']
  return Object.entries(map).map(([label, value], index) => ({
    label,
    value,
    color: colors[index % colors.length],
  }))
}

function buildRollRates(rows: LoanRow[]): RollRateEntry[] {
  const counts: Record<string, Record<string, number>> = {}
  rows.forEach((row) => {
    if (!row.dpd_status) return
    const target = row.loan_status || 'current'
    counts[row.dpd_status] = counts[row.dpd_status] || {}
    counts[row.dpd_status][target] = (counts[row.dpd_status][target] || 0) + 1
  })
  const entries: RollRateEntry[] = []
  Object.entries(counts).forEach(([from, destinations]) => {
    const sum = Object.values(destinations).reduce((sum, value) => sum + value, 0)
    Object.entries(destinations).forEach(([to, value]) => {
      entries.push({
        from,
        to,
        percent: sum ? Number(((value / sum) * 100).toFixed(1)) : 0,
      })
    })
  })
  return entries
}

function buildGrowthProjection(baseYield: number, count: number): GrowthPoint[] {
  const start = baseYield || 1.2
  const loanBase = count || 100
  return Array.from({ length: 6 }).map((_, index) => ({
    label: new Date(Date.now() + index * 30 * 24 * 60 * 60 * 1000).toLocaleString('default', {
      month: 'short',
      year: 'numeric',
    }),
    yield: Number((start + index * 0.15).toFixed(2)),
    loanVolume: loanBase + index * 15,
  }))
}
