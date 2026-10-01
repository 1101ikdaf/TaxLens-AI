"""Dedicated conversational coaching page."""

import streamlit as st

from ai_coach import generate_ai_explanation, generate_chat_response
from taxlens_ui import calculate_current, coach_context, money, page_header


page_header(
    "ASK ABOUT YOUR NUMBERS",
    "AI Tax Coach",
    "Get a plain-language explanation of your forecast and what it could mean for you.",
    "coach",
)

inputs, result, impact, indiana_result = calculate_current()
input_context, result_context, impact_context = coach_context(
    inputs, result, impact, indiana_result
)

summary = st.columns(4)
summary[0].metric("Projected wages", money(result.projected_wages))
summary[1].metric("Federal tax", money(result.projected_total_tax))
summary[2].metric(
    "Federal refund" if result.refund_or_amount_owed >= 0 else "Federal amount owed",
    money(abs(result.refund_or_amount_owed)),
)
summary[3].metric("Side-gig reserve", f"{impact['reserve_rate']:.0%}")

st.markdown(
    '<div class="coach-intro">Ask about your forecast, side-gig taxes, withholding, or ways you '
    'could prepare for the rest of the year.</div>',
    unsafe_allow_html=True,
)

st.session_state.setdefault(
    "coach_messages",
    [
        {
            "role": "assistant",
            "content": (
                "Hi! I have your current TaxLens forecast. Ask me what the numbers mean, "
                "why you may owe money, or how side-gig income affects the estimate."
            ),
        }
    ],
)

button_cols = st.columns([1, 1, 1, 1])
quick_summary = button_cols[0].button("Summarize my forecast", type="primary", width="stretch")
why_owe = button_cols[1].button("Why might I owe?", width="stretch")
side_gig_question = button_cols[2].button("Explain side-gig tax", width="stretch")
clear_chat = button_cols[3].button("Clear chat", width="stretch")

if clear_chat:
    st.session_state.coach_messages = [
        {"role": "assistant", "content": "Chat cleared. What would you like to understand?"}
    ]
    st.rerun()

pending_question = None
if why_owe:
    pending_question = "Why might I owe money based on this forecast?"
elif side_gig_question:
    pending_question = "Explain how my side-gig income changes this tax forecast."

if quick_summary:
    with st.spinner("Reading your forecast..."):
        summary_text = generate_ai_explanation(input_context, result_context, impact_context)
    st.session_state.coach_messages.append(
        {"role": "assistant", "content": summary_text}
    )
    st.rerun()

for message in st.session_state.coach_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", r"\$"))

with st.form("dedicated_coach_form", clear_on_submit=True):
    typed_question = st.text_input(
        "Your question",
        placeholder="For example: What could I change to reduce the projected amount owed?",
    )
    submitted = st.form_submit_button("Ask the coach", type="primary", width="stretch")

question = pending_question or (typed_question.strip() if submitted else "")
if question:
    st.session_state.coach_messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking through your forecast..."):
            answer = generate_chat_response(
                st.session_state.coach_messages,
                input_context,
                result_context,
                impact_context,
            )
        st.markdown(answer.replace("$", r"\$"))
    st.session_state.coach_messages.append({"role": "assistant", "content": answer})

st.caption(
    "TaxLens AI provides educational estimates and explanations. It does not prepare a return or replace professional advice."
)
