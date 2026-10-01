# TaxLens AI Presentation Outline (5-7 minutes)

## 0:00-0:45 - The problem

- New workers may track salary but not their projected year-end tax.
- Side-gig platforms often do not withhold federal income tax.
- A tax bill discovered after year-end is harder to prepare for.

## 0:45-1:15 - The solution

- Introduce TaxLens AI as a forward-looking federal tax surprise predictor.
- Clarify that it is educational planning software, not a filing product.
- Contrast it with tax-preparation software: TaxLens asks what may happen before the
  year ends rather than preparing a return after the year ends.

## 1:15-4:15 - Live demonstration

1. Open the app and click **Load classroom example**.
2. Explain the paycheck inputs: $32,000 earned so far, eight remaining paychecks,
   $2,000 gross pay per check, and $185 withheld per check.
3. Show the projected wages, federal tax, payments, and possible amount owed.
4. Highlight the per-paycheck shortfall warning.
5. Set side-gig revenue and expenses to zero and observe the difference.
6. Restore $8,000 of side-gig revenue and $2,000 of expenses.
7. Show net side-gig profit, incremental federal tax, after-tax profit, and reserve
   rate.
8. Click **Explain my projection** and show the AI explanation.

## 4:15-5:15 - How it works

- Show `tax_engine.py`: Python applies the 2026 brackets and tax rules.
- Show `ai_coach.py`: AI receives calculated results and explains them.
- Emphasize that AI does not perform or alter the core calculation.
- Mention the automated calculation tests.

## 5:15-6:15 - Limitations and learning

- The app currently covers a simplified federal estimate.
- It excludes state taxes, credits, dependents, itemized deductions, QBI, and some
  special rules.
- Future improvements could include pay-stub imports, state support, quarterly
  estimated-tax planning, and expanded scenario comparisons.
- Main lesson: combining deterministic Python calculations with AI explanations is
  more reliable than asking AI to invent a tax estimate directly.

## Backup plan

- The calculation engine and built-in explanation work without internet access.
- If the API is unavailable, demonstrate the same numbers and explain where the AI
  response normally appears.

