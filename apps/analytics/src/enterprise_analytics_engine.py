from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PortfolioKPIs:
    """Container for portfolio-level KPIs to maintain auditability."""

    portfolio_delinquency_rate_percent: float
    portfolio_yield_percent: float
    average_ltv_ratio_percent: float
    average_dti_ratio_percent: float

    def to_dict(self) -> Dict[str, float]:
        """Provide a traceable mapping representation for dashboards and logs."""

        return {
            "portfolio_delinquency_rate_percent": self.portfolio_delinquency_rate_percent,
            "portfolio_yield_percent": self.portfolio_yield_percent,
            "average_ltv_ratio_percent": self.average_ltv_ratio_percent,
            "average_dti_ratio_percent": self.average_dti_ratio_percent,
        }

class LoanAnalyticsEngine:
    """
    A robust engine for computing critical KPIs for a loan portfolio.
    This system is designed for scalability and provides traceable, actionable insights
    to drive financial intelligence and commercial growth.
    """

    def __init__(self, loan_data: pd.DataFrame):
        """
        Initializes the engine with loan portfolio data.

        Args:
            loan_data (pd.DataFrame): A DataFrame containing loan records.
                Expected columns: 'loan_amount', 'appraised_value', 'borrower_income',
                                  'monthly_debt', 'loan_status', 'interest_rate', 'principal_balance'.
        """
        if not isinstance(loan_data, pd.DataFrame) or loan_data.empty:
            raise ValueError("Input loan_data must be a non-empty pandas DataFrame.")

        self.loan_data = loan_data.copy()
        self._validate_columns()
        self._validate_numeric_columns()

    def _validate_columns(self):
        """Ensures the DataFrame contains the necessary columns for KPI computation."""
        required_cols = [
            'loan_amount', 'appraised_value', 'borrower_income', 'monthly_debt',
            'loan_status', 'interest_rate', 'principal_balance'
        ]
        missing_cols = [col for col in required_cols if col not in self.loan_data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in loan_data: {', '.join(missing_cols)}")

    def compute_loan_to_value(self) -> pd.Series:
        """Computes the Loan-to-Value (LTV) ratio for each loan."""
        appraised_value = self.loan_data['appraised_value']
        ltv = pd.Series(
            np.where(
                appraised_value > 0,
                (self.loan_data['loan_amount'] / appraised_value) * 100,
                np.nan,
            ),
            index=self.loan_data.index,
            name='ltv_ratio',
        )
        return ltv

    def compute_debt_to_income(self) -> pd.Series:
        """Computes the Debt-to-Income (DTI) ratio for each borrower."""
        monthly_income = self.loan_data['borrower_income'] / 12
        dti = pd.Series(
            np.where(
                monthly_income > 0,
                (self.loan_data['monthly_debt'] / monthly_income) * 100,
                np.nan,
            ),
            index=self.loan_data.index,
            name='dti_ratio',
        )
        return dti

    def compute_delinquency_rate(self) -> float:
        """Computes the overall portfolio delinquency rate."""
        delinquent_statuses = ['30-59 days past due', '60-89 days past due', '90+ days past due']
        delinquent_count = self.loan_data['loan_status'].isin(delinquent_statuses).sum()
        total_loans = len(self.loan_data)
        return (delinquent_count / total_loans) * 100 if total_loans > 0 else 0.0

    def compute_portfolio_yield(self) -> float:
        """Computes the weighted average portfolio yield."""
        total_principal = self.loan_data['principal_balance'].sum()
        if total_principal == 0:
            return 0.0

        weighted_interest = (
            self.loan_data['interest_rate'] * self.loan_data['principal_balance']
        ).sum()
        return (weighted_interest / total_principal) * 100

    def generate_dashboard_view(self) -> pd.DataFrame:
        """Creates a loan-level dashboard-ready DataFrame with risk flags."""

        ltv_ratio = self.compute_loan_to_value()
        dti_ratio = self.compute_debt_to_income()
        risk_segments = self._classify_risk(ltv_ratio=ltv_ratio, dti_ratio=dti_ratio)

        return self.loan_data.assign(
            ltv_ratio=ltv_ratio,
            dti_ratio=dti_ratio,
            risk_segment=risk_segments,
        )

    def run_full_analysis(self) -> Dict[str, float]:
        """
        Runs a comprehensive analysis and returns a dictionary of portfolio-level KPIs.
        """
        ltv_ratio = self.compute_loan_to_value()
        dti_ratio = self.compute_debt_to_income()

        kpi_summary = PortfolioKPIs(
            portfolio_delinquency_rate_percent=self.compute_delinquency_rate(),
            portfolio_yield_percent=self.compute_portfolio_yield(),
            average_ltv_ratio_percent=ltv_ratio.mean(),
            average_dti_ratio_percent=dti_ratio.mean(),
        )

        self.loan_data = self.loan_data.assign(
            ltv_ratio=ltv_ratio,
            dti_ratio=dti_ratio,
        )

        return kpi_summary.to_dict()

    def _classify_risk(self, ltv_ratio: pd.Series, dti_ratio: pd.Series) -> pd.Series:
        """Generates an interpretable risk segment per loan for dashboards."""

        risk_labels = np.select(
            condlist=[
                (ltv_ratio >= 95) | (dti_ratio >= 50),
                (ltv_ratio >= 85) | (dti_ratio >= 40),
            ],
            choicelist=['high', 'moderate'],
            default='low',
        )
        return pd.Series(risk_labels, index=self.loan_data.index, name='risk_segment')

    def _validate_numeric_columns(self):
        """Validates numeric columns to enforce data quality and prevent silent errors."""

        numeric_columns = [
            'loan_amount',
            'appraised_value',
            'borrower_income',
            'monthly_debt',
            'interest_rate',
            'principal_balance',
        ]

        for column in numeric_columns:
            if not pd.api.types.is_numeric_dtype(self.loan_data[column]):
                raise TypeError(f"Column '{column}' must contain numeric values.")

            negative_values = self.loan_data[column] < 0
            if negative_values.any():
                raise ValueError(
                    f"Column '{column}' contains negative values at rows: "
                    f"{negative_values[negative_values].index.tolist()}"
                )

if __name__ == '__main__':
    # Example usage demonstrating the engine's capabilities
    # This simulates a data-driven workflow for generating actionable insights.

    # Sample data representing a loan portfolio
    data = {
        'loan_amount': [250000, 450000, 150000, 600000],
        'appraised_value': [300000, 500000, 160000, 750000],
        'borrower_income': [80000, 120000, 60000, 150000],
        'monthly_debt': [1500, 2500, 1000, 3000],
        'loan_status': ['current', '30-59 days past due', 'current', 'current'],
        'interest_rate': [0.035, 0.042, 0.038, 0.045],
        'principal_balance': [240000, 440000, 145000, 590000]
    }
    portfolio_df = pd.DataFrame(data)

    # Initialize and run the analytics engine
    engine = LoanAnalyticsEngine(portfolio_df)
    kpi_dashboard = engine.run_full_analysis()
    dashboard_view = engine.generate_dashboard_view()

    # Output the KPI dashboard - ready for visualization or reporting
    print("--- Loan Portfolio KPI Dashboard ---")
    for kpi, value in kpi_dashboard.items():
        print(f"{kpi.replace('_', ' ').title()}: {value:.2f}")
    print("------------------------------------")

    # Summarize risk segments to inform targeted portfolio actions
    print("Risk Segment Distribution:")
    for segment, count in dashboard_view['risk_segment'].value_counts().items():
        print(f"  {segment.title()}: {count}")
