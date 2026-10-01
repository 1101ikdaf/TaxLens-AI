# TaxLens AI: A Federal Tax Surprise Predictor

## Problem

Students and recent graduates often understand their salary but not how much federal
tax they may owe by the end of the year. The problem becomes harder when someone has
side-gig income because taxes may not be withheld automatically. People can discover
the shortfall only after the year ends, when there is less time to prepare for the bill.

## Solution

TaxLens AI is a forward-looking tax projection application built for early-career
workers. Users enter year-to-date wages and federal withholding, information from
their remaining paychecks, side-gig revenue and expenses, retirement contributions,
student-loan interest, and estimated tax payments. The application projects year-end
income, federal income tax, self-employment tax, total payments, and a possible refund
or balance due. It also estimates how much of a projected shortfall would need to be
covered across the remaining paychecks. Unlike tax-preparation software, TaxLens is
designed to help users understand a possible tax surprise before filing season.

## AI Use

Python performs the numerical calculations using defined 2026 federal tax parameters.
The calculated results are then provided to an AI coach, which explains the outlook in
plain language, identifies the main causes of the result, provides educational next
steps, and states important limitations. Separating the calculation engine from the AI
reduces the risk that the model will invent tax numbers. If the live AI connection is
unavailable, the application provides a built-in explanation so the core demonstration
continues to work.

## Intended Users

The primary users are students, recent graduates, early-career employees, and workers
who earn additional income through delivery services, freelancing, online sales, or
other independent work. The tool may also be useful as a basic financial-literacy
demonstration.

## Development

TaxLens was developed in Python using Streamlit for the interface, Plotly for the
visualization, pandas for result tables, and the OpenAI Responses API for the optional
AI explanation. The tax engine uses 2026 federal income-tax brackets, standard
deductions, and self-employment tax rules published by the Internal Revenue Service.
Automated unit tests check the progressive tax calculation, self-employment tax,
student-loan interest phaseout, zero-income case, and side-gig comparison.

## Limitations and Future Improvements

TaxLens is an educational estimate and does not prepare or file returns. It does not
currently include state and local taxes, tax credits, dependents, itemized deductions,
capital gains, the qualified business income deduction, insurance marketplace credits,
or underpayment penalties. Future versions could import pay-stub data, support state
taxes, add more life events, calculate quarterly estimated payments, and generate a
personalized year-end action report. Users should verify important decisions with
official IRS tools or a qualified tax professional.

