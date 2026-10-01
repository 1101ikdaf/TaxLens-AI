from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import plotly.express as px
import streamlit as st

from ai_coach import generate_ai_explanation, generate_chat_response
from state_tax_engine import calculate_indiana_tax, indiana_counties
from tax_engine import TaxInputs, calculate_tax, side_gig_impact


st.set_page_config(
    page_title="TaxLens AI",
    page_icon="🔎",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --cream: #F7F3EA;
        --paper: #FFFCF7;
        --navy: #17233B;
        --blue: #5278A5;
        --lavender: #DDD7F4;
        --coral: #F47C6C;
        --line: #DCD8D0;
        --muted: #667085;
    }
    .stApp {background: var(--cream); color: var(--navy);}
    [data-testid="stAppViewContainer"] {background: var(--cream);}
    [data-testid="stHeader"] {background: rgba(247, 243, 234, .88);}
    [data-testid="stSidebar"] {
        background: #EAF0F7;
        border-right: 1px solid #D5DFEA;
    }
    [data-testid="stSidebar"] * {color: var(--navy);}
    h1, h2, h3, p, label, .stMarkdown {color: var(--navy);}
    div[data-testid="stMetric"] {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 6px 22px rgba(23, 35, 59, .06);
    }
    div[data-testid="stMetric"] label {color: var(--muted) !important;}
    div[data-testid="stMetricValue"] {color: var(--navy);}
    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.1rem 2.3rem;
        border: 1px solid #D4DCE8;
        border-radius: 26px;
        background: linear-gradient(130deg, #FFFDF8 0%, #E6EEF8 55%, #E4DDF7 100%);
        margin-bottom: 1.4rem;
        box-shadow: 0 12px 35px rgba(23, 35, 59, .08);
    }
    .hero:after {
        content: "";
        position: absolute;
        width: 190px;
        height: 190px;
        right: -45px;
        top: -70px;
        border-radius: 50%;
        background: rgba(244, 124, 108, .23);
    }
    .hero h1 {font-size: 3rem; margin: .25rem 0 .45rem; color: var(--navy);}
    .hero p {max-width: 760px; color: #43516A; font-size: 1.06rem; margin: 0;}
    .eyebrow {color: var(--coral); font-weight: 800; letter-spacing: .10em;}
    .small-note {color: var(--muted); font-size: .88rem;}
    .coach-intro {
        background: linear-gradient(120deg, #FFF9F3, #EEEAFB);
        border: 1px solid #DDD5EE;
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin-bottom: .75rem;
        color: #43516A;
    }
    [data-testid="stChatMessage"] {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: .45rem .75rem;
        box-shadow: 0 4px 16px rgba(23, 35, 59, .04);
    }
    [data-testid="stChatInput"] {border-color: #B9C8DC;}
    .stButton > button[kind="primary"] {
        background: var(--coral);
        border-color: var(--coral);
        color: white;
        border-radius: 12px;
    }
    .stButton > button:not([kind="primary"]) {
        border-radius: 12px;
        border-color: #AFC0D4;
        color: var(--navy);
        background: #FFFDF9;
    }
    [data-testid="stExpander"] {
        background: rgba(255, 252, 247, .72);
        border-color: var(--line);
        border-radius: 14px;
    }
    hr {border-color: var(--line);}
    </style>
    """,
    unsafe_allow_html=True,
)


def money(value: float) -> str:
    return f"${value:,.0f}"


US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]


DEFAULTS = {
    "filing_status": "Single",
    "state": "Indiana",
    "county": "Delaware",
    "dependent_count": 0,
    "ytd_wages": 30000.0,
    "ytd_withholding": 2800.0,
    "remaining_paychecks": 8,
    "gross_per_check": 2000.0,
    "withholding_per_check": 200.0,
    "traditional_401k": 2000.0,
    "side_gig_gross": 0.0,
    "side_gig_expenses": 0.0,
    "student_loan_interest": 0.0,
    "estimated_payments": 0.0,
    "ytd_state_withholding": 0.0,
    "state_withholding_per_check": 0.0,
    "ytd_county_withholding": 0.0,
    "county_withholding_per_check": 0.0,
}
for state_key, default_value in DEFAULTS.items():
    st.session_state.setdefault(state_key, default_value)


st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">YOUR 2026 TAX WEATHER</div>
      <h1>TaxLens AI</h1>
      <p>A clearer forecast for your paycheck, side income, and taxes. See what
      may be ahead, understand why, and ask the AI coach what it means for you.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Your projection")
    if st.button("Load Indiana classroom example", width="stretch"):
        st.session_state.pop("coach_messages", None)
        st.session_state.update(
            {
                "filing_status": "Single",
                "state": "Indiana",
                "county": "Delaware",
                "dependent_count": 0,
                "ytd_wages": 32000.0,
                "ytd_withholding": 2900.0,
                "remaining_paychecks": 8,
                "gross_per_check": 2000.0,
                "withholding_per_check": 185.0,
                "traditional_401k": 1800.0,
                "side_gig_gross": 8000.0,
                "side_gig_expenses": 2000.0,
                "student_loan_interest": 700.0,
                "estimated_payments": 0.0,
                "ytd_state_withholding": 900.0,
                "state_withholding_per_check": 90.0,
                "ytd_county_withholding": 400.0,
                "county_withholding_per_check": 45.0,
            }
        )

    filing_status = st.selectbox(
        "Filing status",
        ["Single", "Married filing jointly", "Head of household", "Married filing separately"],
        key="filing_status",
    )
    state = st.selectbox("State of residence", US_STATES, key="state")
    if state == "Indiana":
        county = st.selectbox(
            "Indiana county of residence on January 1",
            indiana_counties(),
            key="county",
        )
        dependent_count = st.number_input(
            "Dependents for Indiana estimate",
            min_value=0,
            max_value=20,
            step=1,
            key="dependent_count",
        )
    else:
        county = None
        dependent_count = 0
        st.caption("State/local calculations currently support Indiana. Federal results still work.")

    st.subheader("Paycheck information")
    ytd_wages = st.number_input(
        "Wages earned so far", min_value=0.0, step=500.0, key="ytd_wages"
    )
    ytd_withholding = st.number_input(
        "Federal income tax withheld so far",
        min_value=0.0,
        step=100.0,
        key="ytd_withholding",
    )
    remaining_paychecks = st.number_input(
        "Paychecks remaining", min_value=0, max_value=53, step=1, key="remaining_paychecks"
    )
    gross_per_check = st.number_input(
        "Gross pay per remaining check",
        min_value=0.0,
        step=100.0,
        key="gross_per_check",
    )
    withholding_per_check = st.number_input(
        "Federal withholding per remaining check",
        min_value=0.0,
        step=25.0,
        key="withholding_per_check",
    )

    if state == "Indiana":
        with st.expander("Indiana and county withholding", expanded=True):
            ytd_state_withholding = st.number_input(
                "Indiana tax withheld so far",
                min_value=0.0,
                step=50.0,
                key="ytd_state_withholding",
            )
            state_withholding_per_check = st.number_input(
                "Indiana withholding per remaining check",
                min_value=0.0,
                step=10.0,
                key="state_withholding_per_check",
            )
            ytd_county_withholding = st.number_input(
                f"{county} County tax withheld so far",
                min_value=0.0,
                step=25.0,
                key="ytd_county_withholding",
            )
            county_withholding_per_check = st.number_input(
                f"{county} County withholding per remaining check",
                min_value=0.0,
                step=5.0,
                key="county_withholding_per_check",
            )
    else:
        ytd_state_withholding = 0.0
        state_withholding_per_check = 0.0
        ytd_county_withholding = 0.0
        county_withholding_per_check = 0.0

    with st.expander("Side gig and adjustments", expanded=True):
        side_gig_gross = st.number_input(
            "Projected side-gig revenue", min_value=0.0, step=250.0, key="side_gig_gross"
        )
        side_gig_expenses = st.number_input(
            "Projected side-gig expenses", min_value=0.0, step=100.0, key="side_gig_expenses"
        )
        traditional_401k = st.number_input(
            "Projected traditional 401(k) contributions",
            min_value=0.0,
            step=250.0,
            key="traditional_401k",
        )
        student_loan_interest = st.number_input(
            "Projected student-loan interest paid",
            min_value=0.0,
            max_value=2500.0,
            step=100.0,
            key="student_loan_interest",
        )
        estimated_payments = st.number_input(
            "Federal estimated tax payments",
            min_value=0.0,
            step=100.0,
            key="estimated_payments",
        )

inputs = TaxInputs(
    filing_status=filing_status,
    ytd_wages=ytd_wages,
    ytd_federal_withholding=ytd_withholding,
    remaining_paychecks=int(remaining_paychecks),
    gross_pay_per_check=gross_per_check,
    federal_withholding_per_check=withholding_per_check,
    projected_traditional_401k=traditional_401k,
    side_gig_gross=side_gig_gross,
    side_gig_expenses=side_gig_expenses,
    student_loan_interest=student_loan_interest,
    estimated_tax_payments=estimated_payments,
)
result = calculate_tax(inputs)
impact = side_gig_impact(inputs, result)
indiana_result = None
if state == "Indiana" and county is not None:
    indiana_result = calculate_indiana_tax(
        federal_adjusted_gross_income=result.adjusted_gross_income,
        filing_status=filing_status,
        county=county,
        remaining_paychecks=int(remaining_paychecks),
        ytd_state_withholding=ytd_state_withholding,
        state_withholding_per_check=state_withholding_per_check,
        ytd_county_withholding=ytd_county_withholding,
        county_withholding_per_check=county_withholding_per_check,
        dependent_count=int(dependent_count),
    )

status_label = "Projected refund" if result.refund_or_amount_owed >= 0 else "Projected amount owed"
status_value = abs(result.refund_or_amount_owed)

top = st.columns(4)
top[0].metric("Projected wages", money(result.projected_wages))
top[1].metric("Projected federal tax", money(result.projected_total_tax))
top[2].metric("Projected payments", money(result.projected_payments))
top[3].metric(status_label, money(status_value))

if result.refund_or_amount_owed < 0:
    st.error(
        f"Potential tax surprise: approximately {money(status_value)} owed. "
        f"That equals about {money(result.amount_per_remaining_paycheck)} across each remaining paycheck."
    )
else:
    st.success(
        f"Based on these simplified inputs, projected payments exceed projected tax by {money(status_value)}."
    )

st.subheader("State and county forecast")
if indiana_result is not None:
    local_balance = indiana_result.combined_refund_or_amount_owed
    local_label = "State/local refund" if local_balance >= 0 else "State/local amount owed"
    local_cols = st.columns(4)
    local_cols[0].metric("Indiana tax", money(indiana_result.estimated_state_tax))
    local_cols[1].metric(
        f"{county} County tax",
        money(indiana_result.estimated_county_tax),
    )
    local_cols[2].metric(
        "State/local withholding",
        money(
            indiana_result.projected_state_withholding
            + indiana_result.projected_county_withholding
        ),
    )
    local_cols[3].metric(local_label, money(abs(local_balance)))

    if local_balance < 0:
        st.warning(
            f"The Indiana and {county} County estimate shows approximately "
            f"{money(abs(local_balance))} owed. That is about "
            f"{money(indiana_result.additional_per_remaining_paycheck)} per remaining paycheck."
        )
    else:
        st.info(
            f"Projected Indiana and {county} County withholding exceeds the simplified "
            f"state/local estimate by {money(local_balance)}."
        )
else:
    st.info(
        f"{state} is available for location selection, but its state/local calculation "
        "has not been added yet. The federal forecast remains active."
    )

left, right = st.columns([1.15, 0.85])
with left:
    st.subheader("Where the money goes")
    categories = ["Federal income tax", "Self-employment tax"]
    amounts = [
        result.federal_income_tax + result.additional_medicare_tax,
        result.self_employment_tax,
    ]
    if indiana_result is not None:
        categories.extend(["Indiana tax", f"{county} County tax"])
        amounts.extend(
            [
                indiana_result.estimated_state_tax,
                indiana_result.estimated_county_tax,
            ]
        )
    chart_data = pd.DataFrame(
        {
            "Category": categories,
            "Amount": amounts,
        }
    )
    fig = px.bar(
        chart_data,
        x="Category",
        y="Amount",
        color="Category",
        color_discrete_sequence=["#5278A5", "#F47C6C", "#8C79C6", "#E8B85C"],
        text_auto="$.2s",
    )
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#17233B",
        margin=dict(l=10, r=10, t=15, b=10),
        yaxis_title="Dollars",
    )
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Tax snapshot")
    st.metric("Effective federal rate", f"{result.effective_tax_rate:.1%}")
    st.metric("Marginal income-tax rate", f"{result.marginal_rate:.0%}")
    st.metric("Taxable income", money(result.taxable_income))
    st.metric("Standard deduction", money(result.standard_deduction))

st.subheader("Side-gig impact")
if result.side_gig_net_profit > 0:
    side_cols = st.columns(4)
    side_cols[0].metric("Net side-gig profit", money(result.side_gig_net_profit))
    side_cols[1].metric("Incremental federal tax", money(impact["incremental_tax"]))
    side_cols[2].metric("Estimated after-tax profit", money(impact["after_tax_profit"]))
    side_cols[3].metric("Estimated reserve rate", f"{impact['reserve_rate']:.0%}")
else:
    st.info("Add projected side-gig revenue to see its estimated tax impact.")

st.subheader("Ask the AI tax coach")
st.markdown(
    '<div class="coach-intro">Ask about your projected balance, side-gig reserve, '
    'withholding, or what a tax term means. The coach uses the numbers calculated above.</div>',
    unsafe_allow_html=True,
)

coach_result = result.to_dict()
coach_result["state"] = state
if indiana_result is not None:
    coach_result["county"] = county
    coach_result["indiana_state_and_county_estimate"] = indiana_result.to_dict()

st.session_state.setdefault(
    "coach_messages",
    [
        {
            "role": "assistant",
            "content": (
                "Hi! I can explain your TaxLens forecast. Try asking: "
                "‘Why might I owe money?’ or ‘How much of my side-gig income should I save?’"
            ),
        }
    ],
)

coach_buttons = st.columns([1, 1, 3])
if coach_buttons[0].button("Quick summary", type="primary", width="stretch"):
    with st.spinner("Reading your forecast..."):
        explanation = generate_ai_explanation(asdict(inputs), coach_result, impact)
    st.session_state.coach_messages.append(
        {"role": "assistant", "content": explanation.replace("$", "USD ")}
    )
    st.rerun()

if coach_buttons[1].button("Clear chat", width="stretch"):
    st.session_state.coach_messages = [
        {
            "role": "assistant",
            "content": "Chat cleared. What would you like to know about your forecast?",
        }
    ]
    st.rerun()

for message in st.session_state.coach_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", r"\$"))

if question := st.chat_input("Ask a question about your tax forecast..."):
    st.session_state.coach_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking through your forecast..."):
            answer = generate_chat_response(
                st.session_state.coach_messages,
                asdict(inputs),
                coach_result,
                impact,
            )
        answer = answer.replace("$", "USD ")
        st.markdown(answer)
    st.session_state.coach_messages.append(
        {"role": "assistant", "content": answer}
    )

with st.expander("Calculation details and limitations"):
    details = pd.DataFrame(
        {
            "Item": [
                "Adjusted gross income",
                "Student-loan interest deduction",
                "Taxable income",
                "Federal income tax",
                "Self-employment tax",
                "Additional Medicare tax",
            ],
            "Amount": [
                result.adjusted_gross_income,
                result.student_loan_interest_deduction,
                result.taxable_income,
                result.federal_income_tax,
                result.self_employment_tax,
                result.additional_medicare_tax,
            ],
        }
    )
    if indiana_result is not None:
        state_details = pd.DataFrame(
            {
                "Item": [
                    "Estimated Indiana taxable income",
                    "Indiana income tax",
                    f"{county} County income tax",
                    "Projected Indiana withholding",
                    f"Projected {county} County withholding",
                ],
                "Amount": [
                    indiana_result.estimated_indiana_taxable_income,
                    indiana_result.estimated_state_tax,
                    indiana_result.estimated_county_tax,
                    indiana_result.projected_state_withholding,
                    indiana_result.projected_county_withholding,
                ],
            }
        )
        details = pd.concat([details, state_details], ignore_index=True)
    st.dataframe(details.style.format({"Amount": "${:,.2f}"}), hide_index=True, width="stretch")
    st.markdown(
        "This educational estimate uses 2026 federal brackets and the standard deduction. "
        "Indiana estimates use a simplified federal-AGI starting point, basic exemptions, the 2.95% "
        "state rate, and the selected county rate. Other states are not yet calculated. It does not "
        "calculate every state adjustment, tax credit, itemized deduction, QBI, capital gain, penalty, "
        "premium tax credit, or dependent rule. Verify decisions with "
        "official IRS resources or a qualified professional."
    )

st.markdown(
    '<p class="small-note">TaxLens AI is an educational classroom project and does not prepare or file tax returns.</p>',
    unsafe_allow_html=True,
)
