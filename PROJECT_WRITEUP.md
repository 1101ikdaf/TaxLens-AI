# TaxLens AI: A Year-End Tax Forecast for Early-Career Workers

## Problem

Students and recent graduates may understand their salary without knowing whether their
withholding is keeping pace with their year-end tax. The problem becomes harder when a
person also earns freelance, delivery, resale, or other side income because taxes may not
be withheld automatically. A shortfall discovered after the year ends leaves less time to
prepare.

## Solution

TaxLens AI is a forward-looking educational forecast for early-career workers. A guided
three-step flow combines year-to-date pay, remaining paychecks, withholding, side-income
revenue and expenses, retirement contributions, student-loan interest, and estimated
payments. The result is presented as simple “tax weather”—clear, cloudy, or stormy—along
with a projected refund cushion or amount owed. Indiana users can also include a simplified
state and resident-county estimate. The Scenario Lab lets users change side income,
expenses, retirement savings, or withholding and compare the result before saving a new
forecast. Unlike tax-filing software, TaxLens focuses on what may happen before year-end.
Users can also download a one-page PDF summary of the active forecast.

## AI Use

The app first calculates the forecast from defined tax rules. Those results are then sent
to an AI coach that explains the outlook in plain language and answers follow-up questions.
The coach is instructed to use only the supplied results, avoid inventing numbers, keep its
answers concise, and remind users that the forecast is educational. Keeping calculation
and explanation separate makes the numerical result repeatable while using AI where it is
most useful: translating tax concepts into understandable guidance. A built-in explanation
is available if the live AI connection is unavailable.

## Intended Users

The primary users are students, recent graduates, early-career employees, and people who
combine a regular job with freelance or gig income. The guided language and classroom
example also make the product useful for financial-literacy demonstrations.

## Development

TaxLens was developed with Python and Streamlit, with Plotly visualizations and the OpenAI
Responses API. The federal calculation uses 2026 brackets and standard deductions,
self-employment tax, and a limited set of common adjustments. The Indiana estimate uses the
2026 state rate and county-rate data. Automated tests cover progressive brackets,
self-employment tax, the student-loan interest phaseout, zero-income behavior, and the
side-gig comparison. The interface was refined into four focused pages: Home, My Forecast,
Scenario Lab, and AI Coach.

## Limitations and Future Improvements

TaxLens is an educational estimate; it does not prepare or file a return. It does not model
every credit, itemized deduction, capital gain, qualified business income deduction,
insurance subsidy, penalty, or special tax situation. State calculations are currently
limited to a simplified Indiana estimate, and county rates can change. Future versions
could securely import paystub data, support more states, and add quarterly
estimated-payment planning. Important decisions should be
verified with official tax resources or a qualified professional.

## Sources

- IRS, “Tax year 2026 annual inflation adjustments,” October 9, 2025.
- Indiana Department of Revenue, “Rates, Fees & Penalties,” accessed September 30, 2026.
