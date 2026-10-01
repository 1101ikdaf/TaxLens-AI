"""Deterministic 2026 federal tax projection engine for TaxLens AI.

This educational model intentionally covers a limited set of common early-career
tax situations. It is not a return-preparation engine and is not tax advice.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterable, Tuple


TAX_YEAR = 2026
SOCIAL_SECURITY_WAGE_BASE = 184_500.0
STANDARD_DEDUCTIONS = {
    "Single": 16_100.0,
    "Married filing jointly": 32_200.0,
    "Head of household": 24_150.0,
    "Married filing separately": 16_100.0,
}

# Each tuple is (top of bracket, marginal rate). None means no upper limit.
BRACKETS: Dict[str, Tuple[Tuple[float | None, float], ...]] = {
    "Single": (
        (12_400, 0.10),
        (50_400, 0.12),
        (105_700, 0.22),
        (201_775, 0.24),
        (256_225, 0.32),
        (640_600, 0.35),
        (None, 0.37),
    ),
    "Married filing jointly": (
        (24_800, 0.10),
        (100_800, 0.12),
        (211_400, 0.22),
        (403_550, 0.24),
        (512_450, 0.32),
        (768_700, 0.35),
        (None, 0.37),
    ),
    "Head of household": (
        (17_700, 0.10),
        (67_450, 0.12),
        (105_700, 0.22),
        (201_750, 0.24),
        (256_200, 0.32),
        (640_600, 0.35),
        (None, 0.37),
    ),
    "Married filing separately": (
        (12_400, 0.10),
        (50_400, 0.12),
        (105_700, 0.22),
        (201_775, 0.24),
        (256_225, 0.32),
        (384_350, 0.35),
        (None, 0.37),
    ),
}


@dataclass(frozen=True)
class TaxInputs:
    filing_status: str = "Single"
    ytd_wages: float = 30_000.0
    ytd_federal_withholding: float = 2_800.0
    remaining_paychecks: int = 8
    gross_pay_per_check: float = 2_000.0
    federal_withholding_per_check: float = 200.0
    projected_traditional_401k: float = 2_000.0
    side_gig_gross: float = 0.0
    side_gig_expenses: float = 0.0
    student_loan_interest: float = 0.0
    estimated_tax_payments: float = 0.0


@dataclass(frozen=True)
class TaxResult:
    projected_wages: float
    projected_withholding: float
    side_gig_net_profit: float
    self_employment_tax: float
    deductible_half_se_tax: float
    student_loan_interest_deduction: float
    adjusted_gross_income: float
    standard_deduction: float
    taxable_income: float
    federal_income_tax: float
    additional_medicare_tax: float
    projected_total_tax: float
    projected_payments: float
    refund_or_amount_owed: float
    effective_tax_rate: float
    marginal_rate: float
    amount_per_remaining_paycheck: float

    def to_dict(self) -> dict:
        return asdict(self)


def _nonnegative(value: float) -> float:
    return max(float(value), 0.0)


def progressive_tax(
    taxable_income: float,
    brackets: Iterable[Tuple[float | None, float]],
) -> tuple[float, float]:
    """Return income tax and the marginal rate for a bracket schedule."""
    income = _nonnegative(taxable_income)
    tax = 0.0
    lower = 0.0
    marginal_rate = 0.0

    for upper, rate in brackets:
        if income <= lower:
            break
        taxable_layer = income - lower if upper is None else min(income, upper) - lower
        if taxable_layer > 0:
            tax += taxable_layer * rate
            marginal_rate = rate
        if upper is None or income <= upper:
            break
        lower = upper

    return tax, marginal_rate


def student_loan_interest_deduction(
    interest_paid: float,
    preliminary_magi: float,
    filing_status: str,
) -> float:
    """Estimate the 2026 student-loan interest deduction and its phaseout."""
    eligible_interest = min(_nonnegative(interest_paid), 2_500.0)
    magi = _nonnegative(preliminary_magi)

    if filing_status == "Married filing separately":
        return 0.0
    if filing_status == "Married filing jointly":
        phaseout_start, phaseout_end = 175_000.0, 205_000.0
    else:
        phaseout_start, phaseout_end = 85_000.0, 100_000.0

    if magi <= phaseout_start:
        return eligible_interest
    if magi >= phaseout_end:
        return 0.0

    phaseout_fraction = (magi - phaseout_start) / (phaseout_end - phaseout_start)
    return eligible_interest * (1.0 - phaseout_fraction)


def calculate_tax(inputs: TaxInputs) -> TaxResult:
    if inputs.filing_status not in BRACKETS:
        raise ValueError(f"Unsupported filing status: {inputs.filing_status}")

    projected_wages = _nonnegative(inputs.ytd_wages) + (
        max(int(inputs.remaining_paychecks), 0) * _nonnegative(inputs.gross_pay_per_check)
    )
    projected_withholding = _nonnegative(inputs.ytd_federal_withholding) + (
        max(int(inputs.remaining_paychecks), 0)
        * _nonnegative(inputs.federal_withholding_per_check)
    )
    traditional_401k = min(
        _nonnegative(inputs.projected_traditional_401k), projected_wages
    )

    side_gig_net_profit = max(
        _nonnegative(inputs.side_gig_gross) - _nonnegative(inputs.side_gig_expenses),
        0.0,
    )
    net_se_earnings = side_gig_net_profit * 0.9235

    if net_se_earnings >= 400.0:
        remaining_ss_base = max(SOCIAL_SECURITY_WAGE_BASE - projected_wages, 0.0)
        social_security_se_tax = min(net_se_earnings, remaining_ss_base) * 0.124
        medicare_se_tax = net_se_earnings * 0.029
        self_employment_tax = social_security_se_tax + medicare_se_tax
    else:
        self_employment_tax = 0.0

    deductible_half_se_tax = self_employment_tax / 2.0
    preliminary_magi = max(
        projected_wages
        - traditional_401k
        + side_gig_net_profit
        - deductible_half_se_tax,
        0.0,
    )
    loan_interest_deduction = student_loan_interest_deduction(
        inputs.student_loan_interest,
        preliminary_magi,
        inputs.filing_status,
    )
    adjusted_gross_income = max(preliminary_magi - loan_interest_deduction, 0.0)
    standard_deduction = STANDARD_DEDUCTIONS[inputs.filing_status]
    taxable_income = max(adjusted_gross_income - standard_deduction, 0.0)
    federal_income_tax, marginal_rate = progressive_tax(
        taxable_income, BRACKETS[inputs.filing_status]
    )

    additional_medicare_threshold = {
        "Married filing jointly": 250_000.0,
        "Married filing separately": 125_000.0,
        "Single": 200_000.0,
        "Head of household": 200_000.0,
    }[inputs.filing_status]
    combined_medicare_earnings = projected_wages + net_se_earnings
    additional_medicare_tax = max(
        combined_medicare_earnings - additional_medicare_threshold, 0.0
    ) * 0.009

    projected_total_tax = (
        federal_income_tax + self_employment_tax + additional_medicare_tax
    )
    projected_payments = projected_withholding + _nonnegative(
        inputs.estimated_tax_payments
    )
    refund_or_amount_owed = projected_payments - projected_total_tax
    total_income = projected_wages + side_gig_net_profit
    effective_tax_rate = projected_total_tax / total_income if total_income else 0.0
    amount_per_remaining_paycheck = (
        max(-refund_or_amount_owed, 0.0) / inputs.remaining_paychecks
        if inputs.remaining_paychecks > 0
        else 0.0
    )

    return TaxResult(
        projected_wages=projected_wages,
        projected_withholding=projected_withholding,
        side_gig_net_profit=side_gig_net_profit,
        self_employment_tax=self_employment_tax,
        deductible_half_se_tax=deductible_half_se_tax,
        student_loan_interest_deduction=loan_interest_deduction,
        adjusted_gross_income=adjusted_gross_income,
        standard_deduction=standard_deduction,
        taxable_income=taxable_income,
        federal_income_tax=federal_income_tax,
        additional_medicare_tax=additional_medicare_tax,
        projected_total_tax=projected_total_tax,
        projected_payments=projected_payments,
        refund_or_amount_owed=refund_or_amount_owed,
        effective_tax_rate=effective_tax_rate,
        marginal_rate=marginal_rate,
        amount_per_remaining_paycheck=amount_per_remaining_paycheck,
    )


def side_gig_impact(inputs: TaxInputs, result: TaxResult) -> dict:
    """Compare the current result with the same facts but no side-gig activity."""
    baseline_inputs = TaxInputs(
        **{
            **asdict(inputs),
            "side_gig_gross": 0.0,
            "side_gig_expenses": 0.0,
        }
    )
    baseline = calculate_tax(baseline_inputs)
    incremental_tax = max(result.projected_total_tax - baseline.projected_total_tax, 0.0)
    after_tax_profit = result.side_gig_net_profit - incremental_tax
    reserve_rate = (
        incremental_tax / result.side_gig_net_profit
        if result.side_gig_net_profit > 0
        else 0.0
    )
    return {
        "incremental_tax": incremental_tax,
        "after_tax_profit": after_tax_profit,
        "reserve_rate": reserve_rate,
        "baseline_total_tax": baseline.projected_total_tax,
    }

