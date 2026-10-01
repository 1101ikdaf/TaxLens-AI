# TaxLens AI

**A 2026 year-end tax forecast for students, recent graduates, and side-gig workers.**

TaxLens projects year-end wages and withholding from paycheck information, estimates
federal income and self-employment taxes, and warns when the entered facts could lead
to a balance due. For Indiana users, it also adds a simplified state and resident-county
estimate. Scenario Lab supports what-if comparisons, and AI Coach explains the completed
forecast in plain language and answers follow-up questions.

## Why it is different from tax-preparation software

Tax-preparation software generally looks backward and prepares a return after the tax
year ends. TaxLens is a forward-looking educational planning tool. It lets users test
changes before year-end, such as adding side-gig income, changing withholding, or
making a traditional 401(k) contribution.

## Features

- Paycheck-based year-end wage and withholding projection
- 2026 federal income-tax brackets and standard deductions
- Self-employment tax estimate using net side-gig profit
- Student-loan interest phaseout estimate
- Projected refund or balance due
- Shortfall per remaining paycheck
- Side-gig incremental tax and after-tax profit comparison
- Simplified Indiana state and resident-county estimate
- Guided three-step forecast and visual Tax Weather result
- Scenario Lab with save-to-forecast behavior
- Conversational AI Coach when an OpenAI API key is configured
- Downloadable one-page PDF forecast
- Built-in explanation when an API connection is unavailable
- Classroom example button on each working page for a reliable demonstration

## Run the app

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Optional: configure an OpenAI API key for the AI coach:

   **macOS/Linux**

   ```bash
   export OPENAI_API_KEY="your-key"
   ```

   **Windows PowerShell**

   ```powershell
   $env:OPENAI_API_KEY="your-key"
   ```

   You can also set `OPENAI_MODEL`; the default in the project is `gpt-5-mini`.

5. Start the app:

   ```bash
   streamlit run app.py
   ```

The browser should open automatically. If it does not, use the local URL printed in
the terminal.

## Test the calculation engine

```bash
python -m unittest -v test_tax_engine.py
```

## Suggested 5-7 minute demonstration

1. Explain the problem: early-career workers may not know whether withholding and
   side-gig tax payments are keeping pace with their projected tax.
2. Open **My Forecast**, click **Load classroom example**, and walk through all three steps.
3. Reveal the Tax Weather result and show the combined balance, tax mix, and amount per
   remaining paycheck.
4. Open **Scenario Lab**, change withholding or side-gig income, and compare the new result.
5. Save the scenario and show that it becomes the active forecast.
6. Return to **My Forecast** and show the one-page PDF download.
7. Open **AI Coach** and ask why side income changed the forecast.
8. Briefly show `tax_engine.py` and `ai_coach.py` to explain that Python calculates
   the numbers while AI explains those calculations.
8. Close with limitations and possible future improvements.

## Model assumptions and limitations

This is an educational estimate, not tax advice and not tax-return preparation.
It uses the 2026 federal standard deduction and ordinary-income brackets. It includes
a simplified student-loan interest phaseout and common self-employment tax mechanics.
It includes a simplified 2026 Indiana state and resident-county estimate, but it does
not calculate other states. It does not include every tax credit, itemized deduction,
QBI calculation, capital gain, underpayment penalty, premium tax credit, or special rule.
Traditional 401(k) contributions are treated as reducing federal taxable wages for this
classroom projection.

## Primary sources

- IRS 2026 inflation adjustments and standard deductions:
  https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill
- IRS Revenue Procedure 2025-32 (2026 brackets and phaseouts):
  https://www.irs.gov/pub/irs-drop/rp-25-32.pdf
- IRS Topic 554, Self-Employment Tax:
  https://www.irs.gov/taxtopics/tc554
- IRS Topic 751, 2026 Social Security wage base:
  https://www.irs.gov/taxtopics/tc751
- Indiana DOR rates, fees, and penalties:
  https://www.in.gov/dor/resources/tax-rates-and-reports/rates-fees-and-penalties/
- OpenAI developer quickstart:
  https://developers.openai.com/api/docs/quickstart
