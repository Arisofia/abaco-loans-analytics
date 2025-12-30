import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class KPICatalogProcessor:
    """Processor for the unified KPI command catalog for ABACO."""
    
    def __init__(self, loans_df: pd.DataFrame, payments_df: pd.DataFrame, customers_df: pd.DataFrame):
        self.loans = self._clean_df(loans_df)
        self.payments = self._clean_df(payments_df)
        self.customers = self._clean_df(customers_df)
        
        # Filter orphaned loans (matching SQL loader logic)
        if "customer_id" in self.loans.columns and "customer_id" in self.customers.columns:
            loan_cust_pre = self.loans["customer_id"].nunique()
            valid_cust = set(self.customers["customer_id"])
            self.loans = self.loans[self.loans["customer_id"].isin(valid_cust)].copy()
            loan_cust_post = self.loans["customer_id"].nunique()
            print(f"[DEBUG] KPICatalogProcessor: customers in loans before filter: {loan_cust_pre}, after: {loan_cust_post}, total valid customers: {len(valid_cust)}")
            
        # Filter orphaned payments
        if "loan_id" in self.payments.columns and "loan_id" in self.loans.columns:
            self.payments = self.payments[self.payments["loan_id"].isin(set(self.loans["loan_id"]))].copy()

        self.loan_month = pd.DataFrame()
        
    def _clean_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Normalize column names
        df.columns = [c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "") for c in df.columns]

        # Candidate columns for key fields (aligned with actual CSV headers)
        # Disbursement date: 'disburse_date', 'disbursement_date', 'Disbursement Date'
        # Payment date: 'true_payment_date', 'payment_date', 'True Payment Date'
        # Payment amount: 'true_total_payment', 'payment_amount', 'True Total Payment', 'amount'
        # Disbursement amount: 'disburse_principal', 'disbursement_amount', 'Disbursement Amount'

        mapping = {
            # Disbursement date
            "disburse_date": "disbursement_date",
            "disbursement date": "disbursement_date",
            # Disbursement amount
            "disburse_principal": "disbursement_amount",
            "disbursement amount": "disbursement_amount",
            # Payment date
            "true payment date": "true_payment_date",
            "payment_date": "true_payment_date",
            # Payment amount
            "true_total_payment": "true_total_payment",
            "payment_amount": "true_total_payment",
            "true total payment": "true_total_payment",
            "amount": "true_total_payment",
            # Principal mapping
            "principal_payment": "true_principal_payment",
            "true principal payment": "true_principal_payment",
            "true_principal_payment": "true_principal_payment",
            # Rebates
            "true_rebates": "true_rebates",
            "true rebates": "true_rebates",
            "true rabates": "true_rebates",
            # Other mappings
            "outstanding_balance": "outstanding_loan_value",
            "interest_rate": "interest_rate_apr",
            "interest_rate_apr": "interest_rate_apr",
            "maturity_date": "loan_end_date",
            "days_in_default": "days_past_due",
            "dpd": "days_past_due"
        }
        for old, new in mapping.items():
            if old in df.columns:
                df[new] = df[old]

        # If true_principal_payment is missing, estimate it from total payment (synthetic fallback)
        if "true_total_payment" in df.columns and "true_principal_payment" not in df.columns:
            df["true_principal_payment"] = df["true_total_payment"] * 0.9

        # Date conversion for all columns containing 'date' or 'fecha'
        date_cols = [col for col in df.columns if any(x in col for x in ["date", "fecha"])]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        return df

    # 0. Base extracts (building blocks)
    def build_loan_month(self, start_date: str = "2024-01-01", end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Builds a monthly loan snapshot with outstanding principal and days past due.
        Aggregates multiple disbursements per loan_id correctly.
        """
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")
            
        # Create month-end series
        month_ends = pd.date_range(start=start_date, end=end_date, freq="ME")
        
        if "true_payment_date" not in self.payments.columns:
            self.loan_month = pd.DataFrame()
            return self.loan_month
            
        # 1. Representative metadata per loan_id
        loan_meta = self.loans.groupby("loan_id").agg({
            "customer_id": "max",
            "interest_rate_apr": "max",
            "origination_fee": "max",
            "origination_fee_taxes": "max",
            "days_past_due": "max"
        }).reset_index()

        # 2. Cumulative disbursements per loan_id and month_end
        disbursements = self.loans[["loan_id", "disbursement_date", "disbursement_amount"]].copy()
        
        grid_disb = []
        for me in month_ends:
            temp = disbursements[disbursements["disbursement_date"] <= me].copy()
            if not temp.empty:
                agg = temp.groupby("loan_id")["disbursement_amount"].sum().reset_index()
                agg["month_end"] = me
                grid_disb.append(agg)
        
        if not grid_disb:
            self.loan_month = pd.DataFrame()
            return self.loan_month
            
        df_disb = pd.concat(grid_disb)
        
        # 3. Cumulative payments per loan_id and month_end
        payments = self.payments[["loan_id", "true_payment_date", "true_principal_payment"]].copy()
        
        grid_pay = []
        for me in month_ends:
            temp = payments[payments["true_payment_date"] <= me].copy()
            if not temp.empty:
                agg = temp.groupby("loan_id")["true_principal_payment"].sum().reset_index(name="cum_principal")
                agg["month_end"] = me
                grid_pay.append(agg)
        
        df_pay = pd.concat(grid_pay) if grid_pay else pd.DataFrame(columns=["loan_id", "month_end", "cum_principal"])
        
        # 4. Final Merge
        df_final = df_disb.merge(df_pay, on=["loan_id", "month_end"], how="left")
        df_final["cum_principal"] = df_final["cum_principal"].fillna(0)
        df_final["outstanding"] = (df_final["disbursement_amount"] - df_final["cum_principal"]).clip(lower=0)
        
        # Add metadata
        df_final = df_final.merge(loan_meta, on="loan_id", how="left")
        
        self.loan_month = df_final
        return self.loan_month

    # 1. Customer Model & Growth
    def get_active_unique_customers(self) -> pd.DataFrame:
        """Count distinct active customers per month."""
        if self.loan_month.empty:
            self.build_loan_month()
        if self.loan_month.empty:
            return pd.DataFrame()
        
        active = self.loan_month[self.loan_month["outstanding"] > 1e-4]
        return active.groupby("month_end")["customer_id"].nunique().reset_index(name="active_customers")

    def get_customer_classification(self) -> pd.DataFrame:
        """Classify customers as New, Recurrent, or Reactivated."""
        loans = self.loans.sort_values(["customer_id", "disbursement_date", "loan_id"])
        loans["rn"] = loans.groupby("customer_id").cumcount() + 1
        loans["prev_disb"] = loans.groupby("customer_id")["disbursement_date"].shift(1)
        
        def classify(row):
            if row["rn"] == 1:
                return "New"
            if pd.notnull(row["prev_disb"]) and (row["disbursement_date"] - row["prev_disb"]).days > 180:
                return "Reactivated"
            return "Recurrent"
            
        loans["customer_type"] = loans.apply(classify, axis=1)
        loans["year_month"] = loans["disbursement_date"].dt.to_period("M").dt.to_timestamp() + pd.offsets.MonthEnd(0)
        
        return loans.groupby(["year_month", "customer_type"])["customer_id"].nunique().reset_index(name="unique_customers")

    def get_intensity_segmentation(self) -> pd.DataFrame:
        """Classify customers into Low / Medium / Heavy users."""
        loans_per_cust = self.loans.groupby("customer_id")["loan_id"].nunique().reset_index(name="loans_count")
        
        def intensity(count):
            if count <= 1:
                return "Low"
            if count <= 3:
                return "Medium"
            return "Heavy"
            
        loans_per_cust["use_intensity"] = loans_per_cust["loans_count"].apply(intensity)
        
        # Merge back with monthly disbursement
        df = self.loans.copy()
        df["year_month"] = df["disbursement_date"].dt.to_period("M").dt.to_timestamp() + pd.offsets.MonthEnd(0)
        df = df.merge(loans_per_cust[["customer_id", "use_intensity"]], on="customer_id", how="left")
        
        summary = df.groupby(["year_month", "use_intensity"]).agg(
            customers=("customer_id", "nunique"),
            disbursement_amount=("disbursement_amount", "sum")
        ).reset_index()
        
        return summary

    # 2. Portfolio & Pricing
    def get_weighted_apr(self) -> pd.DataFrame:
        """Calculate portfolio-weighted APR per month."""
        if self.loan_month.empty:
            self.build_loan_month()
        if self.loan_month.empty:
            return pd.DataFrame()
            
        df = self.loan_month[self.loan_month["outstanding"] > 1e-4].copy()
        df["weighted_apr_part"] = df["interest_rate_apr"] * df["outstanding"]
        
        result = df.groupby("month_end", as_index=False).agg({
            "weighted_apr_part": "sum",
            "outstanding": "sum"
        })
        result["weighted_apr"] = result["weighted_apr_part"] / result["outstanding"].replace(0, np.nan)
        
        return result[["month_end", "weighted_apr"]]

    def get_monthly_pricing(self) -> pd.DataFrame:
        """Combined pricing metrics per month (weighted APR, fee rate, etc.)."""
        if self.loan_month.empty:
            self.build_loan_month()
        if self.loan_month.empty:
            return pd.DataFrame()
            
        df = self.loan_month[self.loan_month["outstanding"] > 1e-4].copy()
        
        # Weighted APR
        df["apr_part"] = df["interest_rate_apr"] * df["outstanding"]
        
        # Fee Rate
        df["fee_rate"] = (df["origination_fee"] + df["origination_fee_taxes"]) / df["disbursement_amount"].replace(0, np.nan)
        df["fee_part"] = df["fee_rate"] * df["outstanding"]
        
        # Other Income Rate - matching SQL logic
        other_cols = ["true_fee_payment", "true_other_payment", "true_tax_payment", "true_fee_tax_payment", "true_rebates"]
        for c in other_cols:
            if c not in self.payments.columns:
                self.payments[c] = 0
        
        # Aggregate income per loan from payments
        income_per_loan = self.payments.groupby("loan_id").agg({
            "true_fee_payment": "sum",
            "true_other_payment": "sum",
            "true_tax_payment": "sum",
            "true_fee_tax_payment": "sum",
            "true_rebates": "sum"
        }).reset_index()
        
        df = df.merge(income_per_loan, on="loan_id", how="left")
        for c in other_cols:
            df[c] = df[c].fillna(0)
            
        df["other_income_rate"] = (df["true_fee_payment"] + df["true_other_payment"] + 
                                   df["true_tax_payment"] + df["true_fee_tax_payment"] - 
                                   df["true_rebates"]) / df["disbursement_amount"].replace(0, np.nan)
        df["other_part"] = df["other_income_rate"] * df["outstanding"]
        
        result = df.groupby("month_end", as_index=False).agg({
            "apr_part": "sum",
            "fee_part": "sum",
            "other_part": "sum",
            "outstanding": "sum"
        })
        
        result["weighted_apr"] = result["apr_part"] / result["outstanding"].replace(0, np.nan)
        result["weighted_fee_rate"] = result["fee_part"] / result["outstanding"].replace(0, np.nan)
        result["weighted_other_income_rate"] = result["other_part"] / result["outstanding"].replace(0, np.nan)
        result["weighted_effective_rate"] = (result["weighted_apr"] + result["weighted_fee_rate"] + 
                                             result["weighted_other_income_rate"]).fillna(0.0)
        
        result = result[["month_end", "weighted_apr", "weighted_fee_rate", 
                        "weighted_other_income_rate", "weighted_effective_rate"]]
        result.rename(columns={"month_end": "year_month"}, inplace=True)
        return result

    def get_monthly_risk(self) -> pd.DataFrame:
        """Combined risk metrics per month (amounts and percentages)."""
        df = self.get_dpd_buckets()
        if df.empty:
            return df
        
        # Match SQL column names exactly
        df.rename(columns={"month_end": "year_month"}, inplace=True)
        # Calculate percentages matching SQL
        for days in [7, 15, 30, 60]:
            df[f"dpd{days}_pct"] = df[f"dpd{days}_amount"] / df["total_outstanding"].replace(0, np.nan)
        df["default_pct"] = df["dpd90_amount"] / df["total_outstanding"].replace(0, np.nan)
        
        return df

    def get_customer_types(self) -> pd.DataFrame:
        """Customer types summary (New, Recurrent, Reactivated)."""
        df = self.get_customer_classification()
        if df.empty:
            return df
        
        # Need to add disbursement_amount per customer type
        loans = self.loans.copy()
        loans["year_month"] = loans["disbursement_date"].dt.to_period("M").dt.to_timestamp() + pd.offsets.MonthEnd(0)
        
        # Use the same classification logic as get_customer_classification
        loans = loans.sort_values(["customer_id", "disbursement_date", "loan_id"])
        loans["rn"] = loans.groupby("customer_id").cumcount() + 1
        loans["prev_disb"] = loans.groupby("customer_id")["disbursement_date"].shift(1)
        
        def classify(row):
            if row["rn"] == 1:
                return "New"
            if pd.notnull(row["prev_disb"]) and (row["disbursement_date"] - row["prev_disb"]).days > 180:
                return "Reactivated"
            return "Recurrent"
            
        loans["customer_type"] = loans.apply(classify, axis=1)
        
        summary = loans.groupby(["year_month", "customer_type"]).agg({
            "customer_id": "nunique",
            "disbursement_amount": "sum"
        }).reset_index()
        
        summary.rename(columns={"customer_id": "unique_customers"}, inplace=True)
        return summary

    def get_weighted_fee_rate(self) -> pd.DataFrame:
        """Compute origination fee weighted average per month."""
        if self.loan_month.empty:
            self.build_loan_month()
        if self.loan_month.empty:
            return pd.DataFrame()
            
        df = self.loan_month[self.loan_month["outstanding"] > 1e-4].copy()
        df["fee_rate"] = (df["origination_fee"] + df["origination_fee_taxes"]) / df["disbursement_amount"].replace(0, np.nan)
        df["weighted_fee_part"] = df["fee_rate"] * df["outstanding"]
        
        result = df.groupby("month_end", as_index=False).agg({
            "weighted_fee_part": "sum",
            "outstanding": "sum"
        })
        result["weighted_fee_rate"] = result["weighted_fee_part"] / result["outstanding"].replace(0, np.nan)
        
        return result[["month_end", "weighted_fee_rate"]]

    def get_concentration(self) -> pd.DataFrame:
        """Compute portfolio concentration for top x% of loans."""
        if self.loan_month.empty:
            self.build_loan_month()
        if self.loan_month.empty:
            return pd.DataFrame()
            
        df = self.loan_month[self.loan_month["outstanding"] > 1e-4].copy()
        df = df.sort_values("outstanding", ascending=False)
        
        results = []
        for month_end, group in df.groupby("month_end", as_index=False):
            total = group["outstanding"].sum()
            n = len(group)
            
            top10_n = max(1, int(np.ceil(0.10 * n)))
            top3_n = max(1, int(np.ceil(0.03 * n)))
            top1_n = max(1, int(np.ceil(0.01 * n)))
            
            results.append({
                "month_end": month_end,
                "total_outstanding": total,
                "top10_concentration": group.head(top10_n)["outstanding"].sum() / total if total > 0 else 0,
                "top3_concentration": group.head(top3_n)["outstanding"].sum() / total if total > 0 else 0,
                "top1_concentration": group.head(top1_n)["outstanding"].sum() / total if total > 0 else 0
            })
        
        return pd.DataFrame(results)

    def get_average_ticket(self) -> pd.DataFrame:
        """Compute average disbursement ticket and distribution by band."""
        df = self.loans.copy()
        df["year_month"] = df["disbursement_date"].dt.to_period("M").dt.to_timestamp() + pd.offsets.MonthEnd(0)
        
        def ticket_band(amount):
            if amount < 10000:
                return "< 10K"
            if amount <= 25000:
                return "10-25K"
            if amount <= 50000:
                return "25-50K"
            if amount <= 100000:
                return "50-100K"
            return "> 100K"
            
        df["ticket_band"] = df["disbursement_amount"].apply(ticket_band)
        
        summary = df.groupby(["year_month", "ticket_band"]).agg(
            num_loans=("loan_id", "count"),
            avg_ticket=("disbursement_amount", "mean"),
            total_disbursement=("disbursement_amount", "sum")
        ).reset_index()
        
        return summary

    def get_line_size_segmentation(self) -> pd.DataFrame:
        """Segment customers by approved credit line bands."""
        df = self.loans.copy()
        # Fallback to disbursement if approved_line_amount not found
        line_col = "approved_line_amount" if "approved_line_amount" in df.columns else "disbursement_amount"
        
        df["year_month"] = df["disbursement_date"].dt.to_period("M").dt.to_timestamp() + pd.offsets.MonthEnd(0)
        
        def line_band(amount):
            if amount < 10000:
                return "< 10K"
            if amount <= 25000:
                return "10-25K"
            if amount <= 50000:
                return "25-50K"
            return "> 50K"
            
        df["line_band"] = df[line_col].apply(line_band)
        
        summary = df.groupby(["year_month", "line_band"]).agg(
            customers=("customer_id", "nunique"),
            disbursement_amount=("disbursement_amount", "sum")
        ).reset_index()
        
        return summary

    # 3. Replines Model
    def get_replines_metrics(self) -> pd.DataFrame:
        """Measure % of customers whose line/loan is renewed within 90 days after closing."""
        loans = self.loans.sort_values(["customer_id", "disbursement_date"])
        loans["next_disb_date"] = loans.groupby("customer_id")["disbursement_date"].shift(-1)
        
        # We need an estimate of "close_date".
        end_col = "loan_end_date" if "loan_end_date" in self.loans.columns else "disbursement_date"
        
        loans["is_replined"] = (pd.notnull(loans["next_disb_date"])) & \
                               ((loans["next_disb_date"] - loans[end_col]).dt.days <= 90)
                               
        loans["year_month"] = loans[end_col].dt.to_period("M").dt.to_timestamp() + pd.offsets.MonthEnd(0)
        
        summary = loans.groupby("year_month").agg(
            closed_customers=("customer_id", "nunique"),
            replined_customers=("is_replined", "sum")
        ).reset_index()
        
        summary["replines_pct_90d"] = summary["replined_customers"] / summary["closed_customers"].replace(0, np.nan)
        
        return summary

    # 4. Risk & DPD Buckets
    def get_dpd_buckets(self) -> pd.DataFrame:
        """Compute monthly delinquency by DPD thresholds."""
        if self.loan_month.empty:
            self.build_loan_month()
        if self.loan_month.empty:
            return pd.DataFrame()
            
        df = self.loan_month.copy()
        
        result = df.groupby("month_end", as_index=False).agg({
            "outstanding": "sum"
        }).rename(columns={"outstanding": "total_outstanding"})
        
        for threshold in [7, 15, 30, 60, 90]:
            col_name = f"dpd{threshold}_amount"
            dpd_sum = df[(df["days_past_due"] >= threshold) & (df["outstanding"] > 1e-4)].groupby("month_end", as_index=False)["outstanding"].sum()
            dpd_sum.columns = ["month_end", col_name]
            result = result.merge(dpd_sum, on="month_end", how="left")
            result[col_name] = result[col_name].fillna(0)
        
        result["dpd30_pct"] = result["dpd30_amount"] / result["total_outstanding"].replace(0, np.nan)
        result["dpd90_pct"] = result["dpd90_amount"] / result["total_outstanding"].replace(0, np.nan)
        
        return result

    # 5. Payor, LTV & CAC
    def get_payor_concentration(self) -> pd.DataFrame:
        """Measure portfolio concentration and risk per payor."""
        if self.loan_month.empty:
            self.build_loan_month()
        if self.loan_month.empty:
            return pd.DataFrame()
            
        # Join with payor info
        pagador_col = "pagador" if "pagador" in self.loans.columns else "customer_id"
        df = self.loan_month.merge(
            self.loans[["loan_id", pagador_col]],
            on="loan_id",
            how="left"
        )
        
        summary = df.groupby(["month_end", pagador_col]).agg(
            outstanding=("outstanding", "sum"),
            dpd30_amount=("outstanding", lambda x: df.loc[x.index, "outstanding"][df.loc[x.index, "days_past_due"] >= 30].sum()),
            dpd90_amount=("outstanding", lambda x: df.loc[x.index, "outstanding"][df.loc[x.index, "days_past_due"] >= 90].sum())
        ).reset_index()
        
        return summary

    def get_all_kpis(self) -> Dict:
        """Run all calculations and return a consolidated dictionary."""
        kpis = {}
        # Core aggregated views for parity tests
        try:
            kpis["monthly_pricing"] = self.get_monthly_pricing().to_dict("records")
        except Exception:
            pass
        try:
            kpis["monthly_risk"] = self.get_monthly_risk().to_dict("records")
        except Exception:
            pass
        try:
            kpis["customer_types"] = self.get_customer_types().to_dict("records")
        except Exception:
            pass

        # Detailed/Granular views
        try:
            kpis["active_unique_customers"] = self.get_active_unique_customers().to_dict("records")
        except Exception:
            pass
        try:
            kpis["customer_classification"] = self.get_customer_classification().to_dict("records")
        except Exception:
            pass
        try:
            kpis["intensity_segmentation"] = self.get_intensity_segmentation().to_dict("records")
        except Exception:
            pass
        try:
            kpis["weighted_apr"] = self.get_weighted_apr().to_dict("records")
        except Exception:
            pass
        try:
            kpis["weighted_fee_rate"] = self.get_weighted_fee_rate().to_dict("records")
        except Exception:
            pass
        try:
            kpis["concentration"] = self.get_concentration().to_dict("records")
        except Exception:
            pass
        try:
            kpis["average_ticket"] = self.get_average_ticket().to_dict("records")
        except Exception:
            pass
        try:
            kpis["line_size_segmentation"] = self.get_line_size_segmentation().to_dict("records")
        except Exception:
            pass
        try:
            kpis["replines_metrics"] = self.get_replines_metrics().to_dict("records")
        except Exception:
            pass
        try:
            kpis["dpd_buckets"] = self.get_dpd_buckets().to_dict("records")
        except Exception:
            pass
        try:
            kpis["payor_concentration"] = self.get_payor_concentration().to_dict("records")
        except Exception:
            pass
        return kpis
