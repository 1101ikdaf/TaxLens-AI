"""Shared interface, state, and calculation helpers for TaxLens AI."""

from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from state_tax_engine import calculate_indiana_tax
from tax_engine import TaxInputs, calculate_tax, side_gig_impact


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
    "filing_status": "Single", "state": "Indiana", "county": "Delaware",
    "dependent_count": 0, "ytd_wages": 30000.0, "ytd_withholding": 2800.0,
    "remaining_paychecks": 8, "gross_per_check": 2000.0,
    "withholding_per_check": 200.0, "traditional_401k": 2000.0,
    "side_gig_gross": 0.0, "side_gig_expenses": 0.0,
    "student_loan_interest": 0.0, "estimated_payments": 0.0,
    "ytd_state_withholding": 0.0, "state_withholding_per_check": 0.0,
    "ytd_county_withholding": 0.0, "county_withholding_per_check": 0.0,
}

CLASSROOM_EXAMPLE = {
    "filing_status": "Single", "state": "Indiana", "county": "Delaware",
    "dependent_count": 0, "ytd_wages": 32000.0, "ytd_withholding": 2900.0,
    "remaining_paychecks": 8, "gross_per_check": 2000.0,
    "withholding_per_check": 185.0, "traditional_401k": 1800.0,
    "side_gig_gross": 8000.0, "side_gig_expenses": 2000.0,
    "student_loan_interest": 700.0, "estimated_payments": 0.0,
    "ytd_state_withholding": 900.0, "state_withholding_per_check": 90.0,
    "ytd_county_withholding": 400.0, "county_withholding_per_check": 45.0,
}


def initialize_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value
        else:
            # Keep shared forecast values alive when their widgets are not
            # rendered on the current page. This prevents Streamlit's widget
            # cleanup from restoring older/default values during navigation.
            st.session_state[key] = st.session_state[key]
    st.session_state.setdefault("forecast_step", 1)
    if "income_profile" not in st.session_state:
        st.session_state.income_profile = "Job + side income"
    else:
        # Keep the Step 1 choice when its radio button is no longer visible.
        st.session_state.income_profile = st.session_state.income_profile
    st.session_state.setdefault("forecast_ready", False)


def _clear_temporary_state() -> None:
    for key in list(st.session_state):
        if key.startswith("scenario_") or key == "coach_messages":
            del st.session_state[key]


def load_classroom_example() -> None:
    current_step = st.session_state.get("forecast_step", 1)
    _clear_temporary_state()
    st.session_state.update(CLASSROOM_EXAMPLE)
    st.session_state.forecast_step = current_step
    st.session_state.income_profile = "Job + side income"
    st.session_state.forecast_ready = True


def reset_inputs() -> None:
    _clear_temporary_state()
    st.session_state.update(DEFAULTS)
    st.session_state.forecast_step = 1
    st.session_state.income_profile = "Job only"
    st.session_state.forecast_ready = False


def money(value: float) -> str:
    return f"${value:,.0f}"


def calculate_current() -> tuple[TaxInputs, object, dict, object | None]:
    inputs = TaxInputs(
        filing_status=st.session_state.filing_status,
        ytd_wages=st.session_state.ytd_wages,
        ytd_federal_withholding=st.session_state.ytd_withholding,
        remaining_paychecks=int(st.session_state.remaining_paychecks),
        gross_pay_per_check=st.session_state.gross_per_check,
        federal_withholding_per_check=st.session_state.withholding_per_check,
        projected_traditional_401k=st.session_state.traditional_401k,
        side_gig_gross=st.session_state.side_gig_gross,
        side_gig_expenses=st.session_state.side_gig_expenses,
        student_loan_interest=st.session_state.student_loan_interest,
        estimated_tax_payments=st.session_state.estimated_payments,
    )
    result = calculate_tax(inputs)
    impact = side_gig_impact(inputs, result)
    indiana_result = None
    if st.session_state.state == "Indiana":
        indiana_result = calculate_indiana_tax(
            federal_adjusted_gross_income=result.adjusted_gross_income,
            filing_status=inputs.filing_status,
            county=st.session_state.county,
            remaining_paychecks=inputs.remaining_paychecks,
            ytd_state_withholding=st.session_state.ytd_state_withholding,
            state_withholding_per_check=st.session_state.state_withholding_per_check,
            ytd_county_withholding=st.session_state.ytd_county_withholding,
            county_withholding_per_check=st.session_state.county_withholding_per_check,
            dependent_count=int(st.session_state.dependent_count),
        )
    return inputs, result, impact, indiana_result


def coach_context(inputs, result, impact, indiana_result) -> tuple[dict, dict, dict]:
    result_context = result.to_dict()
    result_context["state"] = st.session_state.state
    if indiana_result is not None:
        result_context["county"] = st.session_state.county
        result_context["indiana_state_and_county_estimate"] = indiana_result.to_dict()
    return asdict(inputs), result_context, impact


def page_header(eyebrow: str, title: str, description: str, key: str) -> None:
    st.markdown(
        f'<div class="page-hero"><div class="eyebrow">{eyebrow}</div>'
        f'<h1>{title}</h1><p>{description}</p></div>',
        unsafe_allow_html=True,
    )
    actions = st.columns([1.2, 1, 3.8])
    if actions[0].button("Load classroom example", key=f"load_{key}",
                         type="primary", width="stretch"):
        load_classroom_example()
        st.rerun()
    if actions[1].button("Reset", key=f"reset_{key}", width="stretch"):
        reset_inputs()
        st.rerun()


def top_navigation() -> None:
    """Render a compact product-style navigation bar."""
    nav = st.container()
    with nav:
        columns = st.columns([3.7, 1.1, 1.25, 1.05, 1.15])
        columns[0].markdown(
            '<div class="brand-mark"><span>◒</span> TaxLens <b>AI</b></div>',
            unsafe_allow_html=True,
        )
        columns[1].page_link("views/home.py", label="Home")
        columns[2].page_link("views/forecast.py", label="My Forecast")
        columns[3].page_link("views/scenario_lab.py", label="Scenario Lab")
        columns[4].page_link("views/ai_coach_page.py", label="AI Coach")
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root{--cream:#F7F3EA;--paper:#FFFCF7;--navy:#17233B;--blue:#5278A5;
        --lavender:#DDD7F4;--coral:#F47C6C;--line:#DCD8D0;--muted:#667085;}
        .stApp,[data-testid="stAppViewContainer"]{background:var(--cream);color:var(--navy);}
        [data-testid="stHeader"]{background:rgba(247,243,234,.9);}
        [data-testid="stSidebar"]{background:#EAF0F7;border-right:1px solid #D5DFEA;}
        [data-testid="stSidebar"] *{color:var(--navy);}
        [data-testid="stSidebar"]{display:none;}
        [data-testid="collapsedControl"]{display:none;}
        [data-testid="stSidebarNav"] a{border-radius:12px;margin:.2rem .45rem;}
        [data-testid="stSidebarNav"] a[aria-current="page"]{background:#D9E4F1;}
        h1,h2,h3,p,label,.stMarkdown{color:var(--navy);}
        .page-hero{padding:1.55rem 1.8rem;border:1px solid #D4DCE8;border-radius:24px;
        background:linear-gradient(130deg,#FFFDF8 0%,#E6EEF8 58%,#E4DDF7 100%);
        margin-bottom:.85rem;box-shadow:0 10px 28px rgba(23,35,59,.07);}
        .page-hero h1{font-size:2.45rem;margin:.2rem 0 .35rem;color:var(--navy);}
        .page-hero p{max-width:800px;color:#43516A;margin:0;}
        .eyebrow{color:var(--coral);font-weight:800;letter-spacing:.1em;}
        .brand-mark{font-size:1.25rem;font-weight:750;letter-spacing:-.03em;padding:.4rem 0;color:var(--navy);}
        .brand-mark span{display:inline-flex;width:28px;height:28px;border-radius:9px;align-items:center;
        justify-content:center;background:var(--coral);color:#fff;margin-right:.4rem;}
        .brand-mark b{color:var(--coral);}
        [data-testid="stPageLink"] a{justify-content:center;text-decoration:none;color:var(--navy)!important;
        font-weight:650;border-radius:999px;padding:.45rem .7rem;}
        [data-testid="stPageLink"] a:hover{background:#E4EAF4;}
        .nav-divider{height:1px;background:#DED9D0;margin:-.25rem 0 1.2rem;}
        .landing-hero{min-height:500px;display:flex;flex-direction:column;justify-content:center;padding:3rem 1rem 3rem 0;}
        .landing-hero h1{font-size:clamp(3.2rem,6vw,6rem);line-height:.94;letter-spacing:-.065em;
        margin:.6rem 0 1.25rem;max-width:820px;color:var(--navy);}
        .landing-hero p{font-size:1.15rem;line-height:1.65;color:#536077;max-width:650px;}
        .hero-pill{display:inline-flex;width:max-content;padding:.45rem .8rem;background:#EEE9FA;color:#65549A;
        border-radius:999px;font-weight:750;font-size:.82rem;letter-spacing:.04em;}
        .forecast-preview{background:var(--navy);color:#fff;border-radius:32px;padding:2rem;min-height:430px;
        box-shadow:0 28px 60px rgba(23,35,59,.2);position:relative;overflow:hidden;margin-top:2rem;}
        .forecast-preview:after{content:"";position:absolute;width:260px;height:260px;border-radius:50%;
        background:linear-gradient(135deg,#F7B4AA,#C9BDF0);right:-70px;top:-70px;opacity:.9;}
        .forecast-preview *{color:#fff;position:relative;z-index:1;}
        .forecast-preview .preview-label{font-size:.78rem;text-transform:uppercase;letter-spacing:.11em;opacity:.68;}
        .forecast-preview .preview-value{font-size:3.25rem;line-height:1;margin:1.1rem 0 .5rem;letter-spacing:-.05em;}
        .empty-orb{width:150px;height:150px;border-radius:50%;margin:2.2rem auto 1.8rem;
        background:linear-gradient(135deg,#F7B4AA,#C9BDF0);box-shadow:0 0 60px rgba(221,215,244,.28);
        display:flex;align-items:center;justify-content:center;font-size:3rem;}
        .empty-title{text-align:center;font-size:1.55rem;font-weight:750;letter-spacing:-.03em;}
        .empty-copy{text-align:center;opacity:.68;max-width:320px;margin:.55rem auto 0;line-height:1.55;}
        .preview-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:4.5rem;}
        .preview-cell{padding:1rem;border-top:1px solid rgba(255,255,255,.2);}
        .preview-cell small{display:block;opacity:.6;margin-bottom:.35rem;}
        .feature-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1.5rem 0 3rem;}
        .feature-card{background:var(--paper);border:1px solid var(--line);border-radius:24px;padding:1.5rem;
        min-height:190px;transition:transform .2s ease,box-shadow .2s ease;}
        .feature-card:hover{transform:translateY(-4px);box-shadow:0 16px 35px rgba(23,35,59,.09);}
        .feature-number{font-size:.78rem;color:var(--coral);font-weight:800;letter-spacing:.08em;}
        .feature-card h3{font-size:1.35rem;margin:2.25rem 0 .5rem;}
        .feature-card p{color:#667085;line-height:1.55;margin:0;}
        .step-shell{max-width:920px;margin:1rem auto 3rem;}
        .step-count{color:var(--coral);font-weight:800;letter-spacing:.08em;font-size:.8rem;text-transform:uppercase;}
        .step-title{font-size:2.4rem;letter-spacing:-.04em;margin:.35rem 0 .4rem;}
        .step-copy{color:#667085;font-size:1.03rem;margin-bottom:1.5rem;}
        .progress-track{height:7px;background:#E4E0D9;border-radius:20px;overflow:hidden;margin:.8rem 0 2rem;}
        .progress-fill{height:100%;background:linear-gradient(90deg,var(--coral),#A697DA);border-radius:20px;}
        .profile-note{background:#EEF2F8;border-radius:16px;padding:1rem 1.1rem;color:#526078;margin:.75rem 0;}
        .path-summary{display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin:-1.4rem auto 1.5rem;
        max-width:920px;color:#667085;font-size:.9rem;}
        .path-summary strong{color:var(--navy);margin-right:.15rem;}
        .path-summary span{background:#EEE9FA;color:#65549A;border-radius:999px;padding:.35rem .65rem;font-weight:650;}
        .result-hero{background:var(--navy);border-radius:30px;padding:2.1rem;color:#fff;margin:1rem 0 1.5rem;
        display:grid;grid-template-columns:1.2fr .8fr;gap:2rem;box-shadow:0 24px 55px rgba(23,35,59,.16);}
        .result-hero *{color:#fff;}.result-kicker{opacity:.65;text-transform:uppercase;letter-spacing:.1em;font-size:.78rem;}
        .result-amount{font-size:4rem;letter-spacing:-.06em;line-height:1;margin:.65rem 0;}
        .weather-orb{width:190px;height:190px;border-radius:50%;display:flex;align-items:center;justify-content:center;
        font-size:4.5rem;margin:auto;background:linear-gradient(135deg,#F7B4AA,#C9BDF0);box-shadow:0 0 60px rgba(221,215,244,.3);}
        .story-row{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1rem 0 1.5rem;}
        .story-card{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:1.25rem;}
        .story-card small{color:#7A8495;display:block;margin-bottom:.5rem}.story-card strong{font-size:1.5rem;color:var(--navy);}
        @keyframes riseIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
        .landing-hero,.forecast-preview,.page-hero,.step-shell,.result-hero{animation:riseIn .45s ease both;}
        @media(max-width:800px){.feature-grid,.story-row,.result-hero{grid-template-columns:1fr}.landing-hero{min-height:auto}
        .landing-hero h1{font-size:3.2rem}.forecast-preview{min-height:360px}.weather-orb{width:150px;height:150px}}
        div[data-testid="stMetric"]{background:var(--paper);border:1px solid var(--line);
        border-radius:18px;padding:16px 18px;box-shadow:0 6px 22px rgba(23,35,59,.05);}
        div[data-testid="stMetric"] label{color:var(--muted)!important;}
        div[data-testid="stMetricValue"]{color:var(--navy);}
        [data-testid="stForm"],[data-testid="stExpander"]{background:rgba(255,252,247,.78);
        border-color:var(--line);border-radius:16px;}
        input,textarea,[data-baseweb="select"]>div,[data-baseweb="input"]>div{
        background:#FFF!important;color:var(--navy)!important;-webkit-text-fill-color:var(--navy)!important;
        border-color:#B8C7D9!important;}
        input::placeholder,textarea::placeholder{color:#7A8799!important;
        -webkit-text-fill-color:#7A8799!important;}
        [data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"],[role="option"]{
        background:#FFF!important;color:var(--navy)!important;}
        [role="option"]:hover{background:#EAF0F7!important;}
        [data-testid="stChatMessage"]{background:var(--paper);border:1px solid var(--line);
        border-radius:18px;padding:.45rem .75rem;box-shadow:0 4px 16px rgba(23,35,59,.04);}
        .coach-intro,.action-card{background:linear-gradient(120deg,#FFF9F3,#EEEAFB);
        border:1px solid #DDD5EE;border-radius:18px;padding:1rem 1.2rem;margin:.75rem 0;color:#43516A;}
        .weather-clear{background:#E4F2EC;border-left:6px solid #4E9C78;}
        .weather-cloudy{background:#FFF4D8;border-left:6px solid #D2A33A;}
        .weather-storm{background:#FCE4E1;border-left:6px solid var(--coral);}
        .weather-clear,.weather-cloudy,.weather-storm{padding:1rem 1.2rem;border-radius:14px;margin:.6rem 0 1rem;}
        .stButton>button,[data-testid="stFormSubmitButton"]>button{border-radius:12px;}
        .stButton>button[kind="primary"],[data-testid="stFormSubmitButton"]>button{
        background:var(--coral)!important;border-color:var(--coral)!important;color:#FFF!important;}
        [data-testid="stSidebarCollapsedControl"] button,[data-testid="stSidebarCollapseButton"] button{
        background:var(--navy)!important;color:#FFF!important;border:2px solid #FFF!important;border-radius:999px!important;}
        [data-testid="stSidebarCollapsedControl"] svg,[data-testid="stSidebarCollapseButton"] svg{
        fill:#FFF!important;color:#FFF!important;}
        </style>
        """,
        unsafe_allow_html=True,
    )
