import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.enterprise_analytics_engine import (  # noqa: E402
    LoanPosition,
    calculate_monthly_payment,
    expected_loss,
    portfolio_interest_and_risk,
)


def test_monthly_payment_matches_finance_formula():
    loan = LoanPosition(principal=100_000, annual_interest_rate=0.12, term_months=36)
    payment = calculate_monthly_payment(loan)

    monthly_rate = loan.annual_interest_rate / 12
    expected_payment = (monthly_rate * loan.principal) / (1 - math.pow(1 + monthly_rate, -loan.term_months))

    assert payment == pytest.approx(expected_payment, rel=1e-8)


def test_portfolio_interest_and_risk_tracks_defaults():
    prime = LoanPosition(principal=50_000, annual_interest_rate=0.08, term_months=24, default_probability=0.01)
    near_prime = LoanPosition(principal=75_000, annual_interest_rate=0.14, term_months=36, default_probability=0.05)
    subprime = LoanPosition(principal=40_000, annual_interest_rate=0.2, term_months=18, default_probability=0.12)

    monthly_interest, portfolio_loss = portfolio_interest_and_risk(
        loans=[prime, near_prime, subprime], loss_given_default=0.45
    )

    assert monthly_interest > 0
    assert portfolio_loss == pytest.approx(
        expected_loss(prime, 0.45) + expected_loss(near_prime, 0.45) + expected_loss(subprime, 0.45)
    )


def test_invalid_inputs_raise_value_errors():
    with pytest.raises(ValueError):
        LoanPosition(principal=0, annual_interest_rate=0.05, term_months=12)

    with pytest.raises(ValueError):
        LoanPosition(principal=10_000, annual_interest_rate=-0.01, term_months=12)

    with pytest.raises(ValueError):
        LoanPosition(principal=10_000, annual_interest_rate=0.05, term_months=0)

    with pytest.raises(ValueError):
        LoanPosition(principal=10_000, annual_interest_rate=0.05, term_months=12, default_probability=1.5)

    valid_loan = LoanPosition(principal=10_000, annual_interest_rate=0.05, term_months=12)
    with pytest.raises(ValueError):
        expected_loss(valid_loan, loss_given_default=1.2)
