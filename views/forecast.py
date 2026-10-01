"""Guided, progressive forecast experience."""

import plotly.graph_objects as go
import streamlit as st

from forecast_report import build_forecast_pdf
from state_tax_engine import indiana_counties
from taxlens_ui import US_STATES, calculate_current, money, page_header


page_header(
    "A FORECAST, NOT A TAX RETURN",
    "Build your outlook",
    "A short guided path from where you are now to what may be waiting at year-end.",
    "forecast",
)

step = int(st.session_state.forecast_step)
progress = min(max(step, 1), 4) * 25
st.markdown(
    f'<div class="progress-track"><div class="progress-fill" style="width:{progress}%"></div></div>',
    unsafe_allow_html=True,
)

if step == 1:
    st.markdown(
        '<div class="step-shell"><div class="step-count">Step 1 of 3</div>'
        '<div class="step-title">Start with your situation.</div>'
        '<div class="step-copy">We’ll only show the questions that matter to your forecast.</div></div>',
        unsafe_allow_html=True,
    )
    income_choices = ["Job only", "Job + side income"]
    if st.session_state.income_profile not in income_choices:
        st.session_state.income_profile = "Job + side income"
    st.radio(
        "Which best describes your income?",
        income_choices,
        horizontal=True,
        key="income_profile",
        help="Choose “Job + side income” for freelance, delivery, resale, or other work outside your regular job.",
    )
    identity = st.columns(3)
    identity[0].selectbox(
        "Filing status",
        ["Single", "Married filing jointly", "Head of household", "Married filing separately"],
        key="filing_status",
        help="Choose the status you expect to use on your 2026 federal return.",
    )
    identity[1].selectbox(
        "State of residence",
        US_STATES,
        key="state",
        help="Indiana estimates are available now. Other states receive a federal-only forecast.",
    )
    if st.session_state.state == "Indiana":
        identity[2].selectbox(
            "County on January 1",
            indiana_counties(),
            key="county",
            help="Indiana generally uses the county where you lived on January 1 for the resident county tax.",
        )
        st.number_input(
            "Dependents for the Indiana estimate",
            min_value=0,
            max_value=20,
            step=1,
            key="dependent_count",
            help="Used only for the simplified Indiana exemption estimate.",
        )
    else:
        identity[2].info("State calculations currently support Indiana. Federal forecasting remains available.")
    if st.button("Continue to paycheck →", type="primary"):
        if st.session_state.income_profile == "Job only":
            st.session_state.side_gig_gross = 0.0
            st.session_state.side_gig_expenses = 0.0
        st.session_state.forecast_step = 2
        st.rerun()

elif step == 2:
    st.markdown(
        '<div class="step-shell"><div class="step-count">Step 2 of 3</div>'
        '<div class="step-title">Tell us what your paycheck is doing.</div>'
        '<div class="step-copy">Use year-to-date amounts from a recent paystub when possible.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="path-summary"><strong>Your path</strong><span>{st.session_state.income_profile}</span>'
        f'<span>{st.session_state.filing_status}</span><span>{st.session_state.state}</span></div>',
        unsafe_allow_html=True,
    )
    left, right = st.columns(2, gap="large")
    with left:
        st.number_input(
            "Wages earned so far",
            min_value=0.0,
            step=500.0,
            key="ytd_wages",
            help="Use year-to-date taxable wages from your most recent paystub.",
        )
        st.number_input(
            "Federal tax withheld so far",
            min_value=0.0,
            step=100.0,
            key="ytd_withholding",
            help="Use federal income tax withheld—not Social Security or Medicare.",
        )
        st.number_input(
            "Paychecks remaining",
            min_value=0,
            max_value=53,
            step=1,
            key="remaining_paychecks",
            help="Count the paychecks you expect to receive before December 31.",
        )
    with right:
        st.number_input(
            "Gross pay per remaining check",
            min_value=0.0,
            step=100.0,
            key="gross_per_check",
            help="Enter pay before taxes and deductions for a typical remaining paycheck.",
        )
        st.number_input(
            "Federal withholding per remaining check",
            min_value=0.0,
            step=25.0,
            key="withholding_per_check",
            help="Use the federal income-tax withholding shown on a typical paycheck.",
        )
        st.markdown(
            '<div class="profile-note">Tip: federal withholding is the income-tax amount, not Social Security or Medicare.</div>',
            unsafe_allow_html=True,
        )
    if st.session_state.state == "Indiana":
        with st.expander("Add Indiana and county withholding", expanded=True):
            state_col, county_col = st.columns(2)
            state_col.number_input(
                "Indiana tax withheld so far", min_value=0.0, step=50.0, key="ytd_state_withholding"
            )
            state_col.number_input(
                "Indiana withholding per remaining check", min_value=0.0, step=10.0,
                key="state_withholding_per_check"
            )
            county_col.number_input(
                f"{st.session_state.county} County withheld so far", min_value=0.0, step=25.0,
                key="ytd_county_withholding"
            )
            county_col.number_input(
                f"{st.session_state.county} County per remaining check", min_value=0.0, step=5.0,
                key="county_withholding_per_check"
            )
    paycheck_errors = []
    if st.session_state.ytd_withholding > st.session_state.ytd_wages:
        paycheck_errors.append("Federal tax withheld so far cannot be greater than wages earned so far.")
    if st.session_state.withholding_per_check > st.session_state.gross_per_check:
        paycheck_errors.append("Federal withholding per check cannot be greater than gross pay per check.")
    if st.session_state.remaining_paychecks > 0 and st.session_state.gross_per_check <= 0:
        paycheck_errors.append("Add the gross pay expected on each remaining paycheck.")
    for message in paycheck_errors:
        st.error(message)

    nav = st.columns([1, 1, 4])
    if nav[0].button("← Back"):
        st.session_state.forecast_step = 1
        st.rerun()
    if nav[1].button("Continue →", type="primary", disabled=bool(paycheck_errors)):
        st.session_state.forecast_step = 3
        st.rerun()

elif step == 3:
    has_side_income = st.session_state.income_profile == "Job + side income"
    step_title = (
        "Add side income and final details."
        if has_side_income
        else "Add the final details."
    )
    step_copy = (
        "Side income and a few common early-career adjustments can shift the forecast."
        if has_side_income
        else "A few common early-career adjustments can shift the forecast."
    )
    st.markdown(
        '<div class="step-shell"><div class="step-count">Step 3 of 3</div>'
        f'<div class="step-title">{step_title}</div>'
        f'<div class="step-copy">{step_copy}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="path-summary"><strong>Your path</strong><span>{st.session_state.income_profile}</span>'
        f'<span>{st.session_state.filing_status}</span><span>{st.session_state.state}</span></div>',
        unsafe_allow_html=True,
    )

    if has_side_income:
        side, adjustments = st.columns(2, gap="large")
    else:
        st.session_state.side_gig_gross = 0.0
        st.session_state.side_gig_expenses = 0.0
        _, adjustments, _ = st.columns([0.25, 1, 0.25])

    if has_side_income:
        with side:
            st.markdown("### Side income")
            st.number_input(
                "Projected side-gig revenue",
                min_value=0.0,
                step=250.0,
                key="side_gig_gross",
                help="Enter total side-income payments expected for the year before expenses.",
            )
            st.number_input(
                "Projected business expenses",
                min_value=0.0,
                step=100.0,
                key="side_gig_expenses",
                help="Include ordinary business costs you expect to be deductible. Keep receipts and records.",
            )
    with adjustments:
        st.markdown("### Final details" if not has_side_income else "### Adjustments")
        st.number_input(
            "Traditional 401(k) contributions",
            min_value=0.0,
            step=250.0,
            key="traditional_401k",
            help="Use projected pre-tax traditional 401(k) contributions—not Roth contributions.",
        )
        st.number_input(
            "Student-loan interest paid", min_value=0.0, max_value=2500.0, step=100.0,
            key="student_loan_interest",
            help="Enter interest paid, not your total student-loan payment.",
        )
        st.number_input(
            "Federal estimated payments",
            min_value=0.0,
            step=100.0,
            key="estimated_payments",
            help="Include federal estimated tax payments made outside payroll withholding.",
        )
    detail_errors = []
    if st.session_state.side_gig_expenses > st.session_state.side_gig_gross:
        detail_errors.append("Projected business expenses cannot be greater than projected side-gig revenue in this forecast.")
    projected_wages = st.session_state.ytd_wages + (
        st.session_state.remaining_paychecks * st.session_state.gross_per_check
    )
    if st.session_state.traditional_401k > projected_wages:
        detail_errors.append("Traditional 401(k) contributions cannot be greater than projected wages.")
    for message in detail_errors:
        st.error(message)
    nav = st.columns([1, 1.25, 4])
    if nav[0].button("← Back"):
        st.session_state.forecast_step = 2
        st.rerun()
    if nav[1].button("Reveal my forecast →", type="primary", disabled=bool(detail_errors)):
        st.session_state.forecast_ready = True
        st.session_state.forecast_step = 4
        st.rerun()

else:
    inputs, result, impact, indiana_result = calculate_current()
    local_balance = (
        indiana_result.combined_refund_or_amount_owed if indiana_result is not None else 0.0
    )
    combined_balance = result.refund_or_amount_owed + local_balance
    is_refund = combined_balance >= 0
    outlook = "Clear skies" if combined_balance > 250 else "Cloudy" if combined_balance >= -250 else "Storm warning"
    weather_icon = "☀️" if combined_balance > 250 else "☁️" if combined_balance >= -250 else "⛈️"
    balance_label = "projected combined cushion" if is_refund else "projected combined amount owed"

    st.markdown(
        f"""
        <div class="result-hero">
          <div>
            <div class="result-kicker">Your 2026 tax weather · {outlook}</div>
            <div class="result-amount">{money(abs(combined_balance))}</div>
            <div>{balance_label}</div>
            <p style="opacity:.7;margin-top:1.5rem;max-width:520px;">Based on the information entered today. Use Scenario Lab to test a different path.</p>
          </div>
          <div class="weather-orb">{weather_icon}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    state_tax = indiana_result.estimated_state_tax if indiana_result is not None else 0.0
    county_tax = indiana_result.estimated_county_tax if indiana_result is not None else 0.0
    st.markdown(
        f"""
        <div class="story-row">
          <div class="story-card"><small>Projected wages</small><strong>{money(result.projected_wages)}</strong></div>
          <div class="story-card"><small>Total federal tax</small><strong>{money(result.projected_total_tax)}</strong></div>
          <div class="story-card"><small>Side-gig reserve</small><strong>{impact['reserve_rate']:.0%}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    visual, explanation = st.columns([.85, 1.15], gap="large")
    with visual:
        labels = ["Federal income", "Self-employment"]
        values = [result.federal_income_tax + result.additional_medicare_tax, result.self_employment_tax]
        colors = ["#5278A5", "#F47C6C"]
        if indiana_result is not None:
            labels.extend(["Indiana", st.session_state.county])
            values.extend([state_tax, county_tax])
            colors.extend(["#8C79C6", "#E8B85C"])
        fig = go.Figure(
            go.Pie(labels=labels, values=values, hole=.68, marker_colors=colors, sort=False)
        )
        fig.update_layout(
            showlegend=True, paper_bgcolor="rgba(0,0,0,0)", font_color="#17233B",
            margin=dict(l=10, r=10, t=20, b=20), height=360,
            annotations=[dict(text="Tax mix", x=.5, y=.5, font_size=18, showarrow=False)],
        )
        st.plotly_chart(fig, width="stretch")
    with explanation:
        st.markdown("### What this means")
        if combined_balance < 0 and inputs.remaining_paychecks > 0:
            amount_per_check = abs(combined_balance) / inputs.remaining_paychecks
            st.write(
                f"The combined estimate shows an amount owed. Spreading that gap across your remaining "
                f"paychecks would equal approximately **{money(amount_per_check)} per paycheck**."
            )
        elif combined_balance < 0:
            st.write("The combined estimate currently shows an amount owed at year-end.")
        else:
            st.write(
                "Your projected payments currently exceed the simplified combined tax estimate. "
                "That creates the cushion shown above."
            )
        if result.side_gig_net_profit > 0:
            st.write(
                f"Your side gig produces about **{money(result.side_gig_net_profit)} of net profit**. "
                f"The federal model suggests reserving approximately **{impact['reserve_rate']:.0%}** of it."
            )
        if indiana_result is not None:
            st.write(
                f"The location estimate includes **{money(state_tax)} for Indiana** and "
                f"**{money(county_tax)} for {st.session_state.county} County**."
            )
        links = st.columns(2)
        if links[0].button("Test a scenario", type="primary", width="stretch"):
            st.switch_page("views/scenario_lab.py")
        if links[1].button("Ask the AI coach", width="stretch"):
            st.switch_page("views/ai_coach_page.py")

    report_pdf = build_forecast_pdf(
        inputs=inputs,
        result=result,
        impact=impact,
        indiana_result=indiana_result,
        state=st.session_state.state,
        county=st.session_state.county,
        income_profile=st.session_state.income_profile,
    )
    edit = st.columns([1.55, 1, 1, 3.45])
    edit[0].download_button(
        "Download forecast PDF",
        data=report_pdf,
        file_name="TaxLens_2026_Forecast.pdf",
        mime="application/pdf",
        type="primary",
        width="stretch",
    )
    if edit[1].button("Edit details"):
        st.session_state.forecast_step = 1
        st.rerun()
    if edit[2].button("Edit paycheck"):
        st.session_state.forecast_step = 2
        st.rerun()

    with st.expander("About this forecast"):
        st.write(
            f"Federal taxable income: {money(result.taxable_income)} · Federal payments: "
            f"{money(result.projected_payments)} · Effective federal rate: {result.effective_tax_rate:.1%}."
        )
        about_left, about_right = st.columns(2)
        with about_left:
            st.markdown(
                "**Included in this estimate**\n\n"
                "- 2026 federal brackets and standard deduction\n"
                "- Federal self-employment tax\n"
                "- Traditional 401(k) and student-loan interest inputs\n"
                "- Simplified Indiana state and resident-county tax, when selected"
            )
        with about_right:
            st.markdown(
                "**Not included**\n\n"
                "- Tax credits and itemized deductions\n"
                "- Capital gains, QBI, penalties, or special situations\n"
                "- State calculations outside Indiana\n"
                "- Return preparation or filing"
            )
        st.caption(
            "2026 classroom estimate · Assumptions reviewed September 30, 2026 · "
            "Indiana county-rate table effective October 1, 2026 · Educational use only, not tax advice."
        )
        st.markdown(
            "Sources: [IRS 2026 inflation adjustments](https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill) · "
            "[Indiana rates, fees and penalties](https://www.in.gov/dor/resources/tax-rates-and-reports/rates-fees-and-penalties/)"
        )
