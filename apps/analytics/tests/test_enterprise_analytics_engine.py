import numpy as np
import pandas as pd

from apps.analytics.src.enterprise_analytics_engine import LoanAnalyticsEngine


def _sample_portfolio():
    return pd.DataFrame(
        {
            'loan_amount': [250000, 450000, 150000, 600000],
            'appraised_value': [300000, 500000, 160000, 750000],
            'borrower_income': [80000, 120000, 60000, 150000],
            'monthly_debt': [1500, 2500, 1000, 3000],
            'loan_status': ['current', '30-59 days past due', 'current', 'current'],
            'interest_rate': [0.035, 0.042, 0.038, 0.045],
            'principal_balance': [240000, 440000, 145000, 590000],
        }
    )


def test_run_full_analysis_returns_expected_kpis():
    engine = LoanAnalyticsEngine(_sample_portfolio())

    kpis = engine.run_full_analysis()

    assert kpis['portfolio_delinquency_rate_percent'] == 25.0
    assert round(kpis['portfolio_yield_percent'], 4) == 4.1654
    assert round(kpis['average_ltv_ratio_percent'], 2) == 86.77
    assert round(kpis['average_dti_ratio_percent'], 2) == 22.88


def test_dashboard_view_includes_risk_segments_and_ratios():
    engine = LoanAnalyticsEngine(_sample_portfolio())

    dashboard = engine.generate_dashboard_view()

    assert {'ltv_ratio', 'dti_ratio', 'risk_segment'}.issubset(dashboard.columns)
    assert dashboard['risk_segment'].value_counts().to_dict() == {'low': 2, 'moderate': 2}


def test_zero_appraised_value_sets_ltv_to_nan():
    portfolio = _sample_portfolio()
    portfolio.loc[0, 'appraised_value'] = 0

    engine = LoanAnalyticsEngine(portfolio)
    ltv = engine.compute_loan_to_value()

    assert np.isnan(ltv.iloc[0])
