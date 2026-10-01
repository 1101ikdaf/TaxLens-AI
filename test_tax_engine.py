import unittest

from tax_engine import (
    BRACKETS,
    TaxInputs,
    calculate_tax,
    progressive_tax,
    side_gig_impact,
    student_loan_interest_deduction,
)


class TaxEngineTests(unittest.TestCase):
    def test_single_first_bracket(self):
        tax, marginal = progressive_tax(10_000, BRACKETS["Single"])
        self.assertAlmostEqual(tax, 1_000)
        self.assertEqual(marginal, 0.10)

    def test_single_second_bracket(self):
        tax, marginal = progressive_tax(20_000, BRACKETS["Single"])
        self.assertAlmostEqual(tax, 1_240 + (7_600 * 0.12))
        self.assertEqual(marginal, 0.12)

    def test_no_income(self):
        result = calculate_tax(
            TaxInputs(
                ytd_wages=0,
                ytd_federal_withholding=0,
                remaining_paychecks=0,
                gross_pay_per_check=0,
                federal_withholding_per_check=0,
                projected_traditional_401k=0,
            )
        )
        self.assertEqual(result.projected_total_tax, 0)
        self.assertEqual(result.taxable_income, 0)

    def test_self_employment_tax(self):
        result = calculate_tax(
            TaxInputs(
                ytd_wages=40_000,
                ytd_federal_withholding=4_000,
                remaining_paychecks=0,
                gross_pay_per_check=0,
                federal_withholding_per_check=0,
                projected_traditional_401k=0,
                side_gig_gross=10_000,
                side_gig_expenses=2_000,
            )
        )
        expected = 8_000 * 0.9235 * 0.153
        self.assertAlmostEqual(result.self_employment_tax, expected, places=2)

    def test_side_gig_impact_is_positive(self):
        inputs = TaxInputs(side_gig_gross=8_000, side_gig_expenses=2_000)
        result = calculate_tax(inputs)
        impact = side_gig_impact(inputs, result)
        self.assertGreater(impact["incremental_tax"], 0)
        self.assertLess(impact["after_tax_profit"], result.side_gig_net_profit)

    def test_student_loan_interest_phaseout(self):
        self.assertEqual(
            student_loan_interest_deduction(2_500, 80_000, "Single"), 2_500
        )
        self.assertEqual(
            student_loan_interest_deduction(2_500, 100_000, "Single"), 0
        )
        self.assertEqual(
            student_loan_interest_deduction(
                2_500, 50_000, "Married filing separately"
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()

