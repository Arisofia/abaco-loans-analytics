# KPI Catalog – Abaco Analytics

This catalog defines the core KPIs implemented in:

- **Python**: `python/analytics/kpi_catalog_processor.py`
- **SQL**: Postgres views under schema `analytics`

All consumers (Next.js APIs, BI, Python, ML) should rely on these as the **single source of truth**.

---

## 1. Base Views

### 1.1 `analytics.customer_segment`

**Purpose**  
Centralized customer segmentation:

- `sector_segment`: `Gob` vs `Private`
- `business_segment`: `OC`, `CCF`, `DTE`, `Nimal`, `Top`, `Other`
- `industry_segment`: macro industry buckets

**Source**  
- `public.customer_data`

**Key Fields**

- `customer_id`
- `segment_source`
- `sector_segment`
- `business_segment`
- `industry_segment`
- `subcategoria_linea`
- `kam_id`

---

### 1.2 `analytics.loan_month`

**Purpose**  
Monthly loan-level snapshot with:

- Outstanding principal at month-end
- Days past due (DPD)
- Pricing fields (APR, fees)

**Source**

- `public.loan_data`
- `public.real_payment`

**Key Fields**

- `month_end`
- `loan_id`
- `customer_id`
- `disbursement_date`
- `disbursement_amount`
- `interest_rate_apr`
- `origination_fee`
- `origination_fee_taxes`
- `outstanding`
- `days_past_due`

---

## 2. Pricing & Revenue KPIs

### 2.1 `analytics.kpi_monthly_pricing`

**Purpose**  
Monthly portfolio pricing metrics:

- Weighted APR
- Weighted origination fee rate
- Weighted other income rate
- Weighted effective rate (all-in)

**Source**

- `analytics.loan_month`
- `public.real_payment`

**KPIs**

- `weighted_apr`
  - APR weighted by outstanding

- `weighted_fee_rate`
  - `(origination_fee + origination_fee_taxes) / disbursement_amount`, weighted by outstanding

- `weighted_other_income_rate`
  - `(fee + other + tax + fee_tax – rebates) / disbursement_amount`, weighted by outstanding

- `weighted_effective_rate`
  - `weighted_apr + weighted_fee_rate + weighted_other_income_rate`

**Grain**

- One row per `year_month`

---

## 3. Risk & Delinquency KPIs

### 3.1 `analytics.kpi_monthly_risk`

**Purpose**  
Global monthly delinquency KPIs.

**Source**

- `analytics.loan_month`

**KPIs**

- `total_outstanding`
- `dpd7_amount`, `dpd7_pct`
- `dpd15_amount`, `dpd15_pct`
- `dpd30_amount`, `dpd30_pct`
- `dpd60_amount`, `dpd60_pct`
- `dpd90_amount`, `default_pct` (DPD ≥ 90)

**Grain**

- One row per `year_month`

---

## 4. Customer Model & Replines

### 4.1 `analytics.kpi_customer_types`

**Purpose**  
New / Recurrent / Reactivated customers and disbursements.

**Source**

- `public.loan_data`

**Logic**

- Window: `2024-01-01` onwards
- **New**: First-ever disbursement in window
- **Reactivated**: Customer with previous history and gap > 180 days before first disbursement in window
- **Recurrent**: All other cases in window

**KPIs**

- `unique_customers`
- `disbursement_amount`

**Dimensions**

- `year_month`
- `customer_type` (`New`, `Recurrent`, `Reactivated`)
