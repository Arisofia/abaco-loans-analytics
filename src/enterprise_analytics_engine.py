"""Portfolio analytics utilities for credit KPIs and risk metrics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple


@dataclass(frozen=True)
class LoanPosition:
    principal: float
    annual_interest_rate: float
    term_months: int
    default_probability: float = 0.0

    def __post_init__(self) -> None:
        if self.principal <= 0:
            raise ValueError("Principal must be greater than zero.")
        if self.annual_interest_rate < 0:
            raise ValueError("Annual interest rate cannot be negative.")
        if self.term_months <= 0:
            raise ValueError("Term months must be greater than zero.")
        if not 0 <= self.default_probability <= 1:
            raise ValueError("Default probability must be between 0 and 1.")


def calculate_monthly_payment(loan: LoanPosition) -> float:
    """Return the amortized monthly payment for a fixed-rate loan."""
    monthly_rate = loan.annual_interest_rate / 12
    if monthly_rate == 0:
        return loan.principal / loan.term_months

    numerator = monthly_rate * loan.principal
    denominator = 1 - (1 + monthly_rate) ** (-loan.term_months)
    return numerator / denominator


def expected_loss(loan: LoanPosition, loss_given_default: float) -> float:
    """Compute expected loss for a single loan position."""
    if not 0 <= loss_given_default <= 1:
        raise ValueError("Loss given default must be between 0 and 1.")

    exposure_at_default = loan.principal
    return exposure_at_default * loan.default_probability * loss_given_default


def portfolio_interest_and_risk(
    loans: Iterable[LoanPosition], loss_given_default: float
) -> Tuple[float, float]:
    """
    Aggregate expected monthly interest and expected loss across a portfolio.

    Returns:
        A tuple with (expected_monthly_interest, expected_loss_value).
    """
    expected_interest = 0.0
    aggregated_loss = 0.0

    for loan in loans:
        expected_interest += calculate_monthly_payment(loan) - loan.principal / loan.term_months
        aggregated_loss += expected_loss(loan, loss_given_default)

    return expected_interest, aggregated_loss
