-- Source file: data/abaco_portfolio_calculations_fixed.csv
CREATE TABLE IF NOT EXISTS public.abaco_portfolio_calculations_fixed (
    "period" TEXT,
    "measurement_date" TEXT,
    "total_receivable_usd" NUMERIC,
    "total_eligible_usd" NUMERIC,
    "discounted_balance_usd" NUMERIC,
    "dpd_0_7_usd" NUMERIC,
    "dpd_7_30_usd" NUMERIC,
    "dpd_30_60_usd" NUMERIC,
    "dpd_60_90_usd" NUMERIC,
    "dpd_120_plus_usd" NUMERIC,
    "collateralization_pct" NUMERIC,
    "surplus_usd" NUMERIC,
    "par7_pct" NUMERIC,
    "par30_pct" NUMERIC,
    "par60_pct" NUMERIC,
    "par90_pct" NUMERIC,
    "default_ratio_30dpd_pct" NUMERIC,
    "collection_rate_pct" NUMERIC,
    "cdr_pct" NUMERIC,
    "smm_pct" NUMERIC,
    "cpp_pct" NUMERIC,
    "avg_apr_pct" NUMERIC,
    "active_clients" BIGINT,
    "loans_count" BIGINT,
    "principal_outstanding_usd" BIGINT,
    "next_payment_usd" BIGINT,
    "next_payment_date" TEXT,
    "cash_available_usd" NUMERIC,
    "debt_equity_ratio" NUMERIC,
    "de_limit" NUMERIC,
    "dpd_90_plus_usd" NUMERIC,
    "loan_amount" NUMERIC,
    "appraised_value" NUMERIC,
    "borrower_income" NUMERIC,
    "monthly_debt" NUMERIC,
    "loan_status" TEXT,
    "interest_rate" NUMERIC,
    "principal_balance" NUMERIC
);


-- Source file: data/abaco_portfolio_calculations.csv
CREATE TABLE IF NOT EXISTS public.abaco_portfolio_calculations (
    "period" TEXT,
    "measurement_date" TEXT,
    "total_receivable_usd" NUMERIC,
    "total_eligible_usd" NUMERIC,
    "discounted_balance_usd" NUMERIC,
    "dpd_0_7_usd" NUMERIC,
    "dpd_7_30_usd" NUMERIC,
    "dpd_30_60_usd" NUMERIC,
    "dpd_60_90_usd" NUMERIC,
    "dpd_120_plus_usd" NUMERIC,
    "collateralization_pct" NUMERIC,
    "surplus_usd" NUMERIC,
    "par7_pct" NUMERIC,
    "par30_pct" NUMERIC,
    "par60_pct" NUMERIC,
    "par90_pct" NUMERIC,
    "default_ratio_30dpd_pct" NUMERIC,
    "collection_rate_pct" NUMERIC,
    "cdr_pct" NUMERIC,
    "smm_pct" NUMERIC,
    "cpp_pct" NUMERIC,
    "avg_apr_pct" NUMERIC,
    "active_clients" BIGINT,
    "loans_count" BIGINT,
    "principal_outstanding_usd" BIGINT,
    "next_payment_usd" BIGINT,
    "next_payment_date" TEXT,
    "cash_available_usd" NUMERIC,
    "debt_equity_ratio" NUMERIC,
    "de_limit" NUMERIC,
    "dpd_90_plus_usd" NUMERIC
);


-- Source file: data/metrics/ingest_899ec35a5eff.csv
CREATE TABLE IF NOT EXISTS public.ingest_899ec35a5eff (
    "loan_id" TEXT,
    "total_receivable_usd" NUMERIC,
    "total_eligible_usd" NUMERIC,
    "discounted_balance_usd" NUMERIC,
    "cash_available_usd" NUMERIC,
    "dpd_0_7_usd" NUMERIC,
    "dpd_7_30_usd" NUMERIC,
    "dpd_30_60_usd" NUMERIC,
    "dpd_60_90_usd" NUMERIC,
    "dpd_90_plus_usd" NUMERIC,
    "measurement_date" TEXT,
    "period" TEXT,
    "dpd_120_plus_usd" NUMERIC,
    "collateralization_pct" NUMERIC,
    "surplus_usd" NUMERIC,
    "par7_pct" NUMERIC,
    "par30_pct" NUMERIC,
    "par60_pct" NUMERIC,
    "par90_pct" NUMERIC,
    "default_ratio_30dpd_pct" NUMERIC,
    "collection_rate_pct" NUMERIC,
    "cdr_pct" NUMERIC,
    "smm_pct" NUMERIC,
    "cpp_pct" NUMERIC,
    "avg_apr_pct" NUMERIC,
    "active_clients" BIGINT,
    "loans_count" BIGINT,
    "principal_outstanding_usd" BIGINT,
    "next_payment_usd" BIGINT,
    "next_payment_date" TEXT,
    "debt_equity_ratio" NUMERIC,
    "de_limit" NUMERIC,
    "loan_amount" NUMERIC,
    "appraised_value" NUMERIC,
    "borrower_income" NUMERIC,
    "monthly_debt" NUMERIC,
    "loan_status" TEXT,
    "interest_rate" NUMERIC,
    "principal_balance" NUMERIC,
    "tx_run_id" TEXT,
    "tx_timestamp" TEXT
);


-- Source file: data/metrics/ingest_20251212_041805.csv
CREATE TABLE IF NOT EXISTS public.ingest_20251212_041805 (
    "period" TEXT,
    "measurement_date" TEXT,
    "total_receivable_usd" NUMERIC,
    "total_eligible_usd" NUMERIC,
    "discounted_balance_usd" NUMERIC,
    "dpd_0_7_usd" NUMERIC,
    "dpd_7_30_usd" NUMERIC,
    "dpd_30_60_usd" NUMERIC,
    "dpd_60_90_usd" NUMERIC,
    "dpd_120_plus_usd" NUMERIC,
    "collateralization_pct" NUMERIC,
    "surplus_usd" NUMERIC,
    "par7_pct" NUMERIC,
    "par30_pct" NUMERIC,
    "par60_pct" NUMERIC,
    "par90_pct" NUMERIC,
    "default_ratio_30dpd_pct" NUMERIC,
    "collection_rate_pct" NUMERIC,
    "cdr_pct" NUMERIC,
    "smm_pct" NUMERIC,
    "cpp_pct" NUMERIC,
    "avg_apr_pct" NUMERIC,
    "active_clients" BIGINT,
    "loans_count" BIGINT,
    "principal_outstanding_usd" BIGINT,
    "next_payment_usd" BIGINT,
    "next_payment_date" TEXT,
    "cash_available_usd" NUMERIC,
    "debt_equity_ratio" NUMERIC,
    "de_limit" NUMERIC,
    "dpd_90_plus_usd" NUMERIC,
    "ingest_run_id" TEXT,
    "ingest_timestamp" TEXT,
    "validation_passed" TEXT,
    "receivable_amount" NUMERIC,
    "eligible_amount" NUMERIC,
    "discounted_amount" NUMERIC,
    "dpd_0_7_usd_pct" NUMERIC,
    "dpd_7_30_usd_pct" NUMERIC,
    "dpd_30_60_usd_pct" NUMERIC,
    "dpd_60_90_usd_pct" NUMERIC,
    "dpd_120_plus_usd_pct" NUMERIC,
    "dpd_90_plus_usd_pct" NUMERIC,
    "transform_run_id" TEXT,
    "transform_timestamp" TEXT
);


-- Source file: data/metrics/ingest_efe36db7b138.csv
CREATE TABLE IF NOT EXISTS public.ingest_efe36db7b138 (
    "loan_id" TEXT,
    "total_receivable_usd" NUMERIC,
    "total_eligible_usd" NUMERIC,
    "discounted_balance_usd" NUMERIC,
    "cash_available_usd" NUMERIC,
    "dpd_0_7_usd" NUMERIC,
    "dpd_7_30_usd" NUMERIC,
    "dpd_30_60_usd" NUMERIC,
    "dpd_60_90_usd" NUMERIC,
    "dpd_90_plus_usd" NUMERIC,
    "measurement_date" TEXT,
    "period" TEXT,
    "dpd_120_plus_usd" NUMERIC,
    "collateralization_pct" NUMERIC,
    "surplus_usd" NUMERIC,
    "par7_pct" NUMERIC,
    "par30_pct" NUMERIC,
    "par60_pct" NUMERIC,
    "par90_pct" NUMERIC,
    "default_ratio_30dpd_pct" NUMERIC,
    "collection_rate_pct" NUMERIC,
    "cdr_pct" NUMERIC,
    "smm_pct" NUMERIC,
    "cpp_pct" NUMERIC,
    "avg_apr_pct" NUMERIC,
    "active_clients" BIGINT,
    "loans_count" BIGINT,
    "principal_outstanding_usd" BIGINT,
    "next_payment_usd" BIGINT,
    "next_payment_date" TEXT,
    "debt_equity_ratio" NUMERIC,
    "de_limit" NUMERIC,
    "tx_run_id" TEXT,
    "tx_timestamp" TEXT
);


-- Source file: data/metrics/ingest_20251212_041806.csv
CREATE TABLE IF NOT EXISTS public.ingest_20251212_041806 (
    "period" TEXT,
    "measurement_date" TEXT,
    "total_receivable_usd" NUMERIC,
    "total_eligible_usd" NUMERIC,
    "discounted_balance_usd" NUMERIC,
    "dpd_0_7_usd" NUMERIC,
    "dpd_7_30_usd" NUMERIC,
    "dpd_30_60_usd" NUMERIC,
    "dpd_60_90_usd" NUMERIC,
    "dpd_120_plus_usd" NUMERIC,
    "collateralization_pct" NUMERIC,
    "surplus_usd" NUMERIC,
    "par7_pct" NUMERIC,
    "par30_pct" NUMERIC,
    "par60_pct" NUMERIC,
    "par90_pct" NUMERIC,
    "default_ratio_30dpd_pct" NUMERIC,
    "collection_rate_pct" NUMERIC,
    "cdr_pct" NUMERIC,
    "smm_pct" NUMERIC,
    "cpp_pct" NUMERIC,
    "avg_apr_pct" NUMERIC,
    "active_clients" BIGINT,
    "loans_count" BIGINT,
    "principal_outstanding_usd" BIGINT,
    "next_payment_usd" BIGINT,
    "next_payment_date" TEXT,
    "cash_available_usd" NUMERIC,
    "debt_equity_ratio" NUMERIC,
    "de_limit" NUMERIC,
    "dpd_90_plus_usd" NUMERIC,
    "ingest_run_id" TEXT,
    "ingest_timestamp" TEXT,
    "validation_passed" TEXT,
    "receivable_amount" NUMERIC,
    "eligible_amount" NUMERIC,
    "discounted_amount" NUMERIC,
    "dpd_0_7_usd_pct" NUMERIC,
    "dpd_7_30_usd_pct" NUMERIC,
    "dpd_30_60_usd_pct" NUMERIC,
    "dpd_60_90_usd_pct" NUMERIC,
    "dpd_120_plus_usd_pct" NUMERIC,
    "dpd_90_plus_usd_pct" NUMERIC,
    "transform_run_id" TEXT,
    "transform_timestamp" TEXT
);


-- Source file: data/abaco/real_payment.csv
CREATE TABLE IF NOT EXISTS public.real_payment (
    "company" TEXT,
    "customer_id" TEXT,
    "cliente" TEXT,
    "pagador" TEXT,
    "loan_id" TEXT,
    "true_payment_date" TEXT,
    "true_devolution" NUMERIC,
    "true_total_payment" NUMERIC,
    "true_payment_currency" TEXT,
    "true_principal_payment" NUMERIC,
    "true_interest_payment" NUMERIC,
    "true_fee_payment" NUMERIC,
    "true_other_payment" NUMERIC,
    "true_tax_payment" NUMERIC,
    "true_fee_tax_payment" NUMERIC,
    "true_rabates" BIGINT,
    "true_outstanding_loan_value" NUMERIC,
    "true_payment_status" TEXT
);


-- Source file: data/abaco/payment_schedule.csv
CREATE TABLE IF NOT EXISTS public.payment_schedule (
    "loan_id" TEXT,
    "date_due" TEXT,
    "principal" NUMERIC,
    "interest" NUMERIC,
    "other" NUMERIC,
    "fees" NUMERIC,
    "to_tax" NUMERIC,
    "add_balance" NUMERIC,
    "reduce_balance" NUMERIC,
    "currency" TEXT
);


-- Source file: data/abaco/customer_data.csv
CREATE TABLE IF NOT EXISTS public.customer_data (
    "company" TEXT,
    "customer_id" TEXT,
    "cliente" TEXT,
    "pagador" TEXT,
    "loan_id" TEXT,
    "date_of_application" TEXT,
    "application_status" TEXT,
    "application_id" TEXT,
    "product_type" TEXT,
    "sales_channel" NUMERIC,
    "location_city" TEXT,
    "location_state_province" TEXT,
    "location_country" TEXT,
    "internal_credit_score" NUMERIC,
    "client_type" TEXT,
    "product_use" TEXT,
    "sales_agent" TEXT,
    "external_credit_score" NUMERIC,
    "amount_requested" NUMERIC,
    "amount_requested_currency" TEXT,
    "term_requested" BIGINT,
    "term_requested_value" TEXT,
    "gender" NUMERIC,
    "birth_year" NUMERIC,
    "occupation" TEXT,
    "income" NUMERIC,
    "income_currency" TEXT,
    "number_of_dependents" NUMERIC,
    "industry" TEXT,
    "business_year_founded" NUMERIC,
    "business_revenue" NUMERIC,
    "business_revenue_currency" NUMERIC,
    "number_of_employees" NUMERIC,
    "equifax_score" NUMERIC,
    "categoria" TEXT,
    "categorialineacredito" TEXT,
    "subcategoria" TEXT,
    "subcategorialineacredito" TEXT,
    "segment" NUMERIC,
    "subcategoria_linea" NUMERIC,
    "kam_id" NUMERIC,
    "first_disbursement_date" TEXT
);


-- Source file: data/abaco/collateral.csv
CREATE TABLE IF NOT EXISTS public.collateral (
    "loan_id" TEXT,
    "collateral_id" TEXT,
    "asset_type" TEXT,
    "purchase_value" TEXT,
    "appraisal_value" TEXT,
    "purchase_date" TEXT,
    "appraisal_date" TEXT,
    "currency" TEXT
);


-- Source file: data/abaco/loan_data.csv
CREATE TABLE IF NOT EXISTS public.loan_data (
    "company" TEXT,
    "customer_id" TEXT,
    "cliente" TEXT,
    "pagador" TEXT,
    "application_id" TEXT,
    "loan_id" TEXT,
    "product_type" TEXT,
    "disbursement_date" TEXT,
    "tpv" NUMERIC,
    "disbursement_amount" NUMERIC,
    "origination_fee" NUMERIC,
    "origination_fee_taxes" NUMERIC,
    "loan_currency" TEXT,
    "interest_rate_apr" NUMERIC,
    "term" BIGINT,
    "term_unit" TEXT,
    "payment_frequency" TEXT,
    "days_in_default" BIGINT,
    "pledge_to" NUMERIC,
    "pledge_date" NUMERIC,
    "loan_status" TEXT,
    "outstanding_loan_value" NUMERIC,
    "other" NUMERIC,
    "new_loan_id" NUMERIC,
    "new_loan_date" NUMERIC,
    "old_loan_id" NUMERIC,
    "recovery_date" NUMERIC,
    "recovery_value" NUMERIC
);


-- Source file: data/support/marketing_spend.csv
CREATE TABLE IF NOT EXISTS public.marketing_spend (
    "month" TEXT,
    "channel" TEXT,
    "segment" TEXT,
    "spend" BIGINT,
    "kam_id" TEXT
);


-- Source file: data/support/payor_map.csv
CREATE TABLE IF NOT EXISTS public.payor_map (
    "customer_id" TEXT,
    "payor_id" TEXT,
    "payor_name" TEXT,
    "effective_date" TEXT
);


-- Source file: data/support/headcount.csv
CREATE TABLE IF NOT EXISTS public.headcount (
    "month" TEXT,
    "function" TEXT,
    "fte_count" BIGINT,
    "team" TEXT
);


-- Source file: data/support/risk_parameters.csv
CREATE TABLE IF NOT EXISTS public.risk_parameters (
    "segment" TEXT,
    "subcategoria_linea" TEXT,
    "pd" NUMERIC,
    "lgd" NUMERIC,
    "ead_factor" NUMERIC
);


-- Source file: data/support/targets.csv
CREATE TABLE IF NOT EXISTS public.targets (
    "year_month" TEXT,
    "customer_type" TEXT,
    "segment" TEXT,
    "target_disbursement" BIGINT,
    "target_customers" BIGINT
);


-- Source file: data/raw/looker_exports/Abaco-Loan-Tape_Customer-Data_Table-6.csv
CREATE TABLE IF NOT EXISTS public.abaco_loan_tape_customer_data_table_6 (
    "company" TEXT,
    "customer_id" TEXT,
    "cliente" TEXT,
    "pagador" TEXT,
    "loan_id" TEXT,
    "date_of_application" TEXT,
    "application_status" TEXT,
    "application_id" TEXT,
    "product_type" TEXT,
    "sales_channel" NUMERIC,
    "location_city" TEXT,
    "location_state_province" TEXT,
    "location_country" TEXT,
    "internal_credit_score" NUMERIC,
    "client_type" TEXT,
    "product_use" TEXT,
    "sales_agent" TEXT,
    "external_credit_score" NUMERIC,
    "amount_requested" NUMERIC,
    "amount_requested_currency" TEXT,
    "term_requested" BIGINT,
    "term_requested_value" TEXT,
    "gender" NUMERIC,
    "birth_year" NUMERIC,
    "occupation" TEXT,
    "income" NUMERIC,
    "income_currency" TEXT,
    "number_of_dependents" NUMERIC,
    "industry" TEXT,
    "business_year_founded" NUMERIC,
    "business_revenue" NUMERIC,
    "business_revenue_currency" NUMERIC,
    "number_of_employees" NUMERIC,
    "equifax_score" NUMERIC,
    "categoria" TEXT,
    "categorialineacredito" TEXT,
    "subcategoria" TEXT,
    "subcategorialineacredito" TEXT
);


-- Source file: data/raw/looker_exports/Abaco-Loan-Tape_Loan-Data_Table-6.csv
CREATE TABLE IF NOT EXISTS public.abaco_loan_tape_loan_data_table_6 (
    "company" TEXT,
    "customer_id" TEXT,
    "cliente" TEXT,
    "pagador" TEXT,
    "application_id" TEXT,
    "loan_id" TEXT,
    "product_type" TEXT,
    "disbursement_date" TEXT,
    "tpv" NUMERIC,
    "disbursement_amount" NUMERIC,
    "origination_fee" NUMERIC,
    "origination_fee_taxes" NUMERIC,
    "loan_currency" TEXT,
    "interest_rate_apr" NUMERIC,
    "term" BIGINT,
    "term_unit" TEXT,
    "payment_frequency" TEXT,
    "days_in_default" BIGINT,
    "pledge_to" NUMERIC,
    "pledge_date" NUMERIC,
    "loan_status" TEXT,
    "outstanding_loan_value" NUMERIC,
    "other" NUMERIC,
    "new_loan_id" NUMERIC,
    "new_loan_date" NUMERIC,
    "old_loan_id" NUMERIC,
    "recovery_date" NUMERIC,
    "recovery_value" NUMERIC
);


-- Source file: data/raw/looker_exports/loans.csv
CREATE TABLE IF NOT EXISTS public.loans (
    "loan_id" TEXT,
    "maturity_date" TEXT,
    "customer_id" TEXT,
    "application_date" NUMERIC,
    "disburse_date" TEXT,
    "pledge_date" NUMERIC,
    "product_type" TEXT,
    "loan_grade" NUMERIC,
    "lender" NUMERIC,
    "facility" NUMERIC,
    "total_fees" NUMERIC,
    "total_other" NUMERIC,
    "total_interest" NUMERIC,
    "credit_bureau_score" NUMERIC,
    "term" BIGINT,
    "frequency" TEXT,
    "interest_rate" NUMERIC,
    "disburse_principal" NUMERIC,
    "outstanding_balance" NUMERIC,
    "currency" TEXT,
    "dpd" BIGINT,
    "ratio_paid" NUMERIC,
    "loan_status" TEXT,
    "amount_buckets" TEXT,
    "company" TEXT,
    "loan_counts" TEXT,
    "term_buckets" TEXT,
    "location_state_province" TEXT
);


-- Source file: data/raw/looker_exports/schedules.csv
CREATE TABLE IF NOT EXISTS public.schedules (
    "loan_id" TEXT,
    "date_due" TEXT,
    "principal" NUMERIC,
    "interest" NUMERIC,
    "other" NUMERIC,
    "fees" NUMERIC,
    "to_tax" NUMERIC,
    "add_balance" NUMERIC,
    "reduce_balance" NUMERIC,
    "currency" TEXT
);


-- Source file: data/raw/looker_exports/transactions.csv
CREATE TABLE IF NOT EXISTS public.transactions (
    "loan_id" TEXT,
    "transaction_type" TEXT,
    "date_paid" TEXT,
    "principal" NUMERIC,
    "interest" NUMERIC,
    "other" NUMERIC,
    "fees" NUMERIC,
    "to_tax" NUMERIC,
    "add_balance" NUMERIC,
    "reduce_balance" NUMERIC,
    "currency" TEXT
);


-- Source file: data/raw/looker_exports/Abaco-Loan-Tape_Historic-Real-Payment_Table-6.csv
CREATE TABLE IF NOT EXISTS public.abaco_loan_tape_historic_real_payment_table_6 (
    "company" TEXT,
    "customer_id" TEXT,
    "cliente" TEXT,
    "pagador" TEXT,
    "loan_id" TEXT,
    "true_payment_date" TEXT,
    "true_devolution" NUMERIC,
    "true_total_payment" NUMERIC,
    "true_payment_currency" TEXT,
    "true_principal_payment" NUMERIC,
    "true_interest_payment" NUMERIC,
    "true_fee_payment" NUMERIC,
    "true_other_payment" NUMERIC,
    "true_tax_payment" NUMERIC,
    "true_fee_tax_payment" NUMERIC,
    "true_rabates" BIGINT,
    "true_outstanding_loan_value" NUMERIC,
    "true_payment_status" TEXT
);


-- Source file: data/raw/looker_exports/loan_par_balances.csv
CREATE TABLE IF NOT EXISTS public.loan_par_balances (
    "loan_id_raw" TEXT,
    "reporting_date" TEXT,
    "dpd" BIGINT,
    "dpd_date" NUMERIC,
    "is_writeoff" TEXT,
    "writeoff_type" NUMERIC,
    "loan_ccy" TEXT,
    "outstanding_balance" NUMERIC,
    "writeoff_outstanding_balance" NUMERIC,
    "xchg_rate_to_usd" BIGINT,
    "outstanding_balance_usd" NUMERIC,
    "writeoff_outstanding_balance_usd" NUMERIC,
    "par_7_balance_usd" NUMERIC,
    "par_30_balance_usd" NUMERIC,
    "par_60_balance_usd" NUMERIC,
    "par_90_balance_usd" NUMERIC
);

