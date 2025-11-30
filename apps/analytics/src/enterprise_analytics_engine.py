import pandas as pd
from typing import Dict

from metrics_utils import (
    debt_to_income_ratio,
    loan_to_value,
    portfolio_delinquency_rate,
    portfolio_kpis,
    validate_kpi_columns,
    weighted_portfolio_yield,
)


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

    def _validate_columns(self):
        """Ensures the DataFrame contains the necessary columns for KPI computation."""
        validate_kpi_columns(self.loan_data)

    def compute_loan_to_value(self) -> pd.Series:
        """Computes the Loan-to-Value (LTV) ratio for each loan."""
        return loan_to_value(self.loan_data['loan_amount'], self.loan_data['appraised_value'])

    def compute_debt_to_income(self) -> pd.Series:
        """Computes the Debt-to-Income (DTI) ratio for each borrower."""
        return debt_to_income_ratio(self.loan_data['monthly_debt'], self.loan_data['borrower_income'])

    def compute_delinquency_rate(self) -> float:
        """Computes the overall portfolio delinquency rate."""
        return portfolio_delinquency_rate(self.loan_data['loan_status'])

    def compute_portfolio_yield(self) -> float:
        """Computes the weighted average portfolio yield."""
        return weighted_portfolio_yield(self.loan_data['interest_rate'], self.loan_data['principal_balance'])

    def run_full_analysis(self) -> Dict[str, float]:
        """
        Runs a comprehensive analysis and returns a dictionary of portfolio-level KPIs.
        """
        self.loan_data['ltv_ratio'] = self.compute_loan_to_value()
        self.loan_data['dti_ratio'] = self.compute_debt_to_income()

        return portfolio_kpis(self.loan_data)


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

    # Output the KPI dashboard - ready for visualization or reporting
    print("--- Loan Portfolio KPI Dashboard ---")
    for kpi, value in kpi_dashboard.items():
        print(f"{kpi.replace('_', ' ').title()}: {value:.2f}")
    print("------------------------------------")
