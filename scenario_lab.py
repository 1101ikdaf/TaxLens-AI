"""Interactive what-if comparison page."""

from dataclasses import replace

import plotly.graph_objects as go
import streamlit as st

from state_tax_engine import calculate_indiana_tax
from tax_engine import calculate_tax, side_gig_impact
from taxlens_ui import calculate_current, money, page_header


page_header(
    "WHAT IF?",
    "Scenario Lab",
    "Move the controls to see how side income, retirement savings, and withholding may change the forecast.",
    "scenario",
)

base_inputs, base_result, base_impact, base_indiana = calculate_current()

st.session_state.setdefault("scenario_side_gig", float(base_inputs.side_gig_gross))
st.session_state.setdefault("scenario_expenses", float(base_inputs.side_gig_expenses))
st.session_state.setdefault("scenario_401k", float(base_inputs.projected_traditional_401k))
st.session_state.setdefault(
    "scenario_withholding", float(base_inputs.federal_withholding_per_check)
)

st.subheader("Adjust the scenario")
control_a, control_b = st.columns(2)
with control_a:
    st.slider(
        "Projected side-gig revenue",
        min_value=0.0,
        max_value=max(20000.0, float(base_inputs.side_gig_gross) * 2 + 5000.0),
        step=250.0,
        key="scenario_side_gig",
        format="$%.0f",
    )
    st.slider(
        "Side-gig expenses",
        min_value=0.0,
        max_value=max(10000.0, float(base_inputs.side_gig_expenses) * 2 + 2500.0),
        step=100.0,
        key="scenario_expenses",
        format="$%.0f",
    )
with control_b:
    st.slider(
        "Traditional 401(k) contributions",
        min_value=0.0,
        max_value=max(15000.0, float(base_inputs.projected_traditional_401k) * 2 + 5000.0),
        step=250.0,
        key="scenario_401k",
        format="$%.0f",
    )
    st.slider(
        "Federal withholding per remaining check",
        min_value=0.0,
        max_value=max(750.0, float(base_inputs.federal_withholding_per_check) * 2 + 200.0),
        step=5.0,
        key="scenario_withholding",
        format="$%.0f",
    )

scenario_inputs = replace(
    base_inputs,
    side_gig_gross=st.session_state.scenario_side_gig,
    side_gig_expenses=st.session_state.scenario_expenses,
    projected_traditional_401k=st.session_state.scenario_401k,
    federal_withholding_per_check=st.session_state.scenario_withholding,
)
scenario_result = calculate_tax(scenario_inputs)
scenario_impact = side_gig_impact(scenario_inputs, scenario_result)
scenario_indiana = None
if st.session_state.state == "Indiana":
    scenario_indiana = calculate_indiana_tax(
        federal_adjusted_gross_income=scenario_result.adjusted_gross_income,
        filing_status=scenario_inputs.filing_status,
        county=st.session_state.county,
        remaining_paychecks=scenario_inputs.remaining_paychecks,
        ytd_state_withholding=st.session_state.ytd_state_withholding,
        state_withholding_per_check=st.session_state.state_withholding_per_check,
        ytd_county_withholding=st.session_state.ytd_county_withholding,
        county_withholding_per_check=st.session_state.county_withholding_per_check,
        dependent_count=int(st.session_state.dependent_count),
    )

base_local_balance = (
    base_indiana.combined_refund_or_amount_owed if base_indiana is not None else 0.0
)
scenario_local_balance = (
    scenario_indiana.combined_refund_or_amount_owed if scenario_indiana is not None else 0.0
)
base_combined_balance = base_result.refund_or_amount_owed + base_local_balance
scenario_combined_balance = scenario_result.refund_or_amount_owed + scenario_local_balance

st.divider()
scenario_is_refund = scenario_combined_balance >= 0
scenario_outlook = (
    "Clear skies"
    if scenario_combined_balance > 250
    else "Cloudy"
    if scenario_combined_balance >= -250
    else "Storm warning"
)
scenario_icon = (
    "☀️"
    if scenario_combined_balance > 250
    else "☁️"
    if scenario_combined_balance >= -250
    else "⛈️"
)
scenario_label = (
    "projected combined cushion" if scenario_is_refund else "projected combined amount owed"
)
balance_change = scenario_combined_balance - base_combined_balance
change_description = (
    f"{money(abs(balance_change))} better than your current forecast"
    if balance_change >= 0
    else f"{money(abs(balance_change))} worse than your current forecast"
)

st.markdown(
    f"""
    <div class="result-hero">
      <div>
        <div class="result-kicker">Scenario tax weather · {scenario_outlook}</div>
        <div class="result-amount">{money(abs(scenario_combined_balance))}</div>
        <div>{scenario_label}</div>
        <p style="opacity:.7;margin-top:1.5rem;max-width:520px;">{change_description}.</p>
      </div>
      <div class="weather-orb">{scenario_icon}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

base_label = "refund cushion" if base_combined_balance >= 0 else "amount owed"
scenario_short_label = "refund cushion" if scenario_combined_balance >= 0 else "amount owed"
st.markdown(
    f"""
    <div class="story-row">
      <div class="story-card"><small>Current · {base_label}</small><strong>{money(abs(base_combined_balance))}</strong></div>
      <div class="story-card"><small>Scenario · {scenario_short_label}</small><strong>{money(abs(scenario_combined_balance))}</strong></div>
      <div class="story-card"><small>Overall change</small><strong>{'+' if balance_change >= 0 else '−'}{money(abs(balance_change))}</strong></div>
    </div>
    <div class="story-row">
      <div class="story-card"><small>Scenario federal tax</small><strong>{money(scenario_result.projected_total_tax)}</strong></div>
      <div class="story-card"><small>After-tax side-gig profit</small><strong>{money(scenario_impact['after_tax_profit'])}</strong></div>
      <div class="story-card"><small>Suggested side-gig reserve</small><strong>{scenario_impact['reserve_rate']:.0%}</strong></div>
    </div>
    """,
    unsafe_allow_html=True,
)

if scenario_combined_balance < 0:
    extra_per_check = (
        abs(scenario_combined_balance) / scenario_inputs.remaining_paychecks
        if scenario_inputs.remaining_paychecks > 0 else 0.0
    )
    st.markdown(
        f'<div class="action-card"><strong>Scenario action:</strong> This version shows about '
        f'{money(abs(scenario_combined_balance))} owed, or roughly {money(extra_per_check)} per '
        f'remaining paycheck.</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="action-card"><strong>Scenario result:</strong> Projected payments exceed the '
        f'combined estimate by about {money(scenario_combined_balance)}.</div>',
        unsafe_allow_html=True,
    )

with st.expander("See detailed comparison chart"):
    measures = ["Federal tax", "Projected payments", "After-tax side-gig profit"]
    current_values = [
        base_result.projected_total_tax,
        base_result.projected_payments,
        base_impact["after_tax_profit"],
    ]
    scenario_values = [
        scenario_result.projected_total_tax,
        scenario_result.projected_payments,
        scenario_impact["after_tax_profit"],
    ]
    fig = go.Figure()
    fig.add_bar(name="Current", x=measures, y=current_values, marker_color="#9BAEC5")
    fig.add_bar(name="Scenario", x=measures, y=scenario_values, marker_color="#F47C6C")
    fig.update_layout(
        barmode="group", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#17233B", margin=dict(l=10, r=10, t=30, b=10), yaxis_title="Dollars"
    )
    st.plotly_chart(fig, width="stretch")

if st.button("Use this scenario as my forecast", type="primary"):
    st.session_state.update(
        {
            "side_gig_gross": float(st.session_state.scenario_side_gig),
            "side_gig_expenses": float(st.session_state.scenario_expenses),
            "traditional_401k": float(st.session_state.scenario_401k),
            "withholding_per_check": float(st.session_state.scenario_withholding),
            "forecast_ready": True,
            "forecast_step": 4,
        }
    )
    st.session_state.pop("coach_messages", None)
    st.success("Scenario saved as your active forecast. The Home and My Forecast pages will now use it.")

st.caption(
    "The Scenario Lab changes only the selected inputs. It does not model every tax credit, deduction, or state rule."
)
