"""Simplified 2026 Indiana state and county tax estimates for TaxLens AI."""

from __future__ import annotations

from dataclasses import asdict, dataclass


INDIANA_STATE_RATE = 0.0295
COUNTY_RATE_EFFECTIVE_DATE = "2026-10-01"

INDIANA_COUNTY_RATES = {
    "Adams": 0.016,
    "Allen": 0.0159,
    "Bartholomew": 0.0175,
    "Benton": 0.0179,
    "Blackford": 0.025,
    "Boone": 0.0171,
    "Brown": 0.025234,
    "Carroll": 0.024733,
    "Cass": 0.0295,
    "Clark": 0.02,
    "Clay": 0.0235,
    "Clinton": 0.0265,
    "Crawford": 0.0165,
    "Daviess": 0.015,
    "Dearborn": 0.014,
    "Decatur": 0.0245,
    "DeKalb": 0.0213,
    "Delaware": 0.015,
    "Dubois": 0.012,
    "Elkhart": 0.02,
    "Fayette": 0.0282,
    "Floyd": 0.0189,
    "Fountain": 0.021,
    "Franklin": 0.017,
    "Fulton": 0.0288,
    "Gibson": 0.013,
    "Grant": 0.0275,
    "Greene": 0.0235,
    "Hamilton": 0.011,
    "Hancock": 0.0194,
    "Harrison": 0.01,
    "Hendricks": 0.017,
    "Henry": 0.0202,
    "Howard": 0.0235,
    "Huntington": 0.0195,
    "Jackson": 0.021,
    "Jasper": 0.02864,
    "Jay": 0.025,
    "Jefferson": 0.0103,
    "Jennings": 0.025,
    "Johnson": 0.014,
    "Knox": 0.017,
    "Kosciusko": 0.01,
    "LaGrange": 0.0165,
    "Lake": 0.015,
    "LaPorte": 0.0145,
    "Lawrence": 0.0175,
    "Madison": 0.0225,
    "Marion": 0.0202,
    "Marshall": 0.0125,
    "Martin": 0.025,
    "Miami": 0.0254,
    "Monroe": 0.0214,
    "Montgomery": 0.0265,
    "Morgan": 0.0272,
    "Newton": 0.01,
    "Noble": 0.0175,
    "Ohio": 0.02,
    "Orange": 0.0175,
    "Owen": 0.025,
    "Parke": 0.0265,
    "Perry": 0.014,
    "Pike": 0.012,
    "Porter": 0.005,
    "Posey": 0.0145,
    "Pulaski": 0.0285,
    "Putnam": 0.023,
    "Randolph": 0.03,
    "Ripley": 0.0238,
    "Rush": 0.0215,
    "St. Joseph": 0.0175,
    "Scott": 0.0216,
    "Shelby": 0.017,
    "Spencer": 0.008,
    "Starke": 0.0171,
    "Steuben": 0.0199,
    "Sullivan": 0.017,
    "Switzerland": 0.0145,
    "Tippecanoe": 0.0128,
    "Tipton": 0.026,
    "Union": 0.0275,
    "Vanderburgh": 0.0125,
    "Vermillion": 0.015,
    "Vigo": 0.02,
    "Wabash": 0.029,
    "Warren": 0.0212,
    "Warrick": 0.01,
    "Washington": 0.02,
    "Wayne": 0.0125,
    "Wells": 0.021,
    "White": 0.0232,
    "Whitley": 0.016829,
}


@dataclass(frozen=True)
class IndianaTaxResult:
    estimated_indiana_taxable_income: float
    personal_exemption_amount: float
    dependent_exemption_amount: float
    state_rate: float
    county_rate: float
    estimated_state_tax: float
    estimated_county_tax: float
    projected_state_withholding: float
    projected_county_withholding: float
    state_refund_or_amount_owed: float
    county_refund_or_amount_owed: float
    combined_refund_or_amount_owed: float
    additional_per_remaining_paycheck: float

    def to_dict(self) -> dict:
        return asdict(self)


def indiana_counties() -> list[str]:
    """Return Indiana county names alphabetically."""
    return sorted(INDIANA_COUNTY_RATES)


def calculate_indiana_tax(
    federal_adjusted_gross_income: float,
    filing_status: str,
    county: str,
    remaining_paychecks: int = 0,
    ytd_state_withholding: float = 0.0,
    state_withholding_per_check: float = 0.0,
    ytd_county_withholding: float = 0.0,
    county_withholding_per_check: float = 0.0,
    dependent_count: int = 0,
) -> IndianaTaxResult:
    """Estimate Indiana state and resident-county income taxes.

    This classroom model begins with federal AGI and subtracts basic Indiana
    personal and dependent exemptions. It does not model every Indiana
    adjustment, deduction, or credit.
    """
    if county not in INDIANA_COUNTY_RATES:
        raise ValueError(f"Unsupported Indiana county: {county}")

    federal_agi = max(float(federal_adjusted_gross_income), 0.0)
    remaining = max(int(remaining_paychecks), 0)
    dependents = max(int(dependent_count), 0)

    personal_exemption_count = 2 if filing_status == "Married filing jointly" else 1
    personal_exemption_amount = personal_exemption_count * 1_000.0
    dependent_exemption_amount = dependents * 1_500.0
    estimated_indiana_taxable_income = max(
        federal_agi - personal_exemption_amount - dependent_exemption_amount,
        0.0,
    )

    county_rate = INDIANA_COUNTY_RATES[county]
    estimated_state_tax = estimated_indiana_taxable_income * INDIANA_STATE_RATE
    estimated_county_tax = estimated_indiana_taxable_income * county_rate
    projected_state_withholding = max(float(ytd_state_withholding), 0.0) + (
        remaining * max(float(state_withholding_per_check), 0.0)
    )
    projected_county_withholding = max(float(ytd_county_withholding), 0.0) + (
        remaining * max(float(county_withholding_per_check), 0.0)
    )
    state_refund_or_amount_owed = projected_state_withholding - estimated_state_tax
    county_refund_or_amount_owed = projected_county_withholding - estimated_county_tax
    combined_refund_or_amount_owed = (
        state_refund_or_amount_owed + county_refund_or_amount_owed
    )
    additional_per_remaining_paycheck = (
        max(-combined_refund_or_amount_owed, 0.0) / remaining
        if remaining > 0
        else 0.0
    )

    return IndianaTaxResult(
        estimated_indiana_taxable_income=estimated_indiana_taxable_income,
        personal_exemption_amount=personal_exemption_amount,
        dependent_exemption_amount=dependent_exemption_amount,
        state_rate=INDIANA_STATE_RATE,
        county_rate=county_rate,
        estimated_state_tax=estimated_state_tax,
        estimated_county_tax=estimated_county_tax,
        projected_state_withholding=projected_state_withholding,
        projected_county_withholding=projected_county_withholding,
        state_refund_or_amount_owed=state_refund_or_amount_owed,
        county_refund_or_amount_owed=county_refund_or_amount_owed,
        combined_refund_or_amount_owed=combined_refund_or_amount_owed,
        additional_per_remaining_paycheck=additional_per_remaining_paycheck,
    )
