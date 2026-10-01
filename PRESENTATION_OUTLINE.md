# TaxLens AI Presentation Outline (5–7 minutes)

## 0:00–0:45 — The problem

- Early-career workers may know their salary but not whether withholding is keeping pace.
- Side income often arrives without tax withholding.
- Finding a shortfall after year-end leaves less time to prepare.

## 0:45–1:15 — The solution

- Introduce TaxLens AI as a year-end tax forecast for students, recent graduates, and
  workers with more than one source of income.
- Explain the difference from tax-filing software: TaxLens helps users explore what may
  happen before the year ends; it does not prepare a return.
- Point out the four parts: forecast, tax weather, Scenario Lab, and AI Coach.

## 1:15–4:30 — Live demonstration

1. Start on **Home** and explain that no result appears until a forecast is built.
2. Open **My Forecast** and click **Load classroom example**.
3. Walk through all three steps instead of jumping to the result:
   - Single filer in Delaware County, Indiana.
   - $32,000 earned so far, eight remaining $2,000 paychecks.
   - $8,000 side-gig revenue, $2,000 of expenses, and $1,800 in traditional 401(k)
     contributions.
4. Reveal the forecast and point out the **Storm warning** tax weather, projected combined
   amount owed, tax mix, per-paycheck gap, and suggested side-gig reserve.
5. Open **Scenario Lab**. Increase federal withholding per remaining paycheck or change
   side income and show how the weather and comparison cards respond.
6. Save the scenario as the active forecast and briefly return to **Home** to show that the
   updated result persists.
7. Return to **My Forecast** and point out the downloadable one-page PDF summary.
8. Open **AI Coach**, load the classroom example if needed, and ask: “Why does my side gig
   change my forecast?” Show that it explains the supplied result and supports follow-up
   questions.

## 4:30–5:30 — How it works

- Briefly show `tax_engine.py` and explain that the numerical forecast is calculated from
  defined 2026 rules, so the same inputs produce the same result.
- Briefly show the instructions in `ai_coach.py`: the AI receives the completed calculation,
  explains it, and is told not to invent or recalculate numbers.
- Mention that automated tests check important calculation cases.

## 5:30–6:30 — Limitations and learning

- This is an educational forecast, not tax advice or a filing product.
- It covers common federal inputs and a simplified Indiana state/county estimate, but not
  every credit, deduction, penalty, or special situation.
- County tax rates may change, and other states are not calculated yet.
- Main lesson: a useful AI finance product needs both trustworthy calculations and clear
  communication. AI is strongest here as an explanation layer, not as the source of the
  tax numbers.

## Backup plan

- The classroom values and main calculations work without an internet connection.
- If the live AI response is unavailable, show the built-in explanation and describe where
  the conversational response normally appears.

## Classroom result checkpoints

- Projected wages: **$48,000**
- Net side-gig profit: **$6,000**
- Projected federal tax: **about $4,797**
- Projected combined amount owed: **about $265**
- Suggested side-gig reserve: **about 25%**
