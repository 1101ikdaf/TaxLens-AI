"""Editorial landing page for TaxLens AI."""

import streamlit as st

from taxlens_ui import calculate_current, money


inputs, result, impact, indiana_result = calculate_current()
local_balance = (
    indiana_result.combined_refund_or_amount_owed if indiana_result is not None else 0.0
)
combined_balance = result.refund_or_amount_owed + local_balance
balance_word = "ahead" if combined_balance >= 0 else "owed"

hero_left, hero_right = st.columns([1.25, .75], gap="large")
with hero_left:
    st.markdown(
        """
        <section class="landing-hero">
          <span class="hero-pill">TAX CLARITY FOR REAL LIFE</span>
          <h1>Know what’s coming before tax season.</h1>
          <p>TaxLens turns paychecks, side income, and withholding into a clear year-end forecast—then helps you understand what to do next.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    buttons = st.columns([1, 2.1])
    if buttons[0].button("Build my forecast →", type="primary", width="stretch"):
        st.session_state.forecast_step = 1
        st.switch_page("views/forecast.py")

with hero_right:
    if st.session_state.forecast_ready:
        st.markdown(
            f"""
            <div class="forecast-preview">
              <div class="preview-label">Current tax weather</div>
              <div class="preview-value">{money(abs(combined_balance))}</div>
              <div>{'projected refund cushion' if combined_balance >= 0 else 'projected combined amount owed'}</div>
              <div class="preview-grid">
                <div class="preview-cell"><small>Projected wages</small><strong>{money(result.projected_wages)}</strong></div>
                <div class="preview-cell"><small>Federal tax</small><strong>{money(result.projected_total_tax)}</strong></div>
                <div class="preview-cell"><small>Side-gig reserve</small><strong>{impact['reserve_rate']:.0%}</strong></div>
                <div class="preview-cell"><small>Outlook</small><strong>{'Clear' if combined_balance > 250 else 'Cloudy' if combined_balance >= -250 else 'Stormy'}</strong></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="forecast-preview">
              <div class="preview-label">Your tax weather</div>
              <div class="empty-orb">◌</div>
              <div class="empty-title">Your forecast is waiting.</div>
              <div class="empty-copy">Complete three short steps to see your projected refund or amount owed.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("## Three ways to see your money more clearly")
st.markdown(
    """
    <div class="feature-grid">
      <div class="feature-card"><div class="feature-number">01 · FORECAST</div><h3>See the year ahead</h3><p>Turn current paychecks and side income into one understandable tax outlook.</p></div>
      <div class="feature-card"><div class="feature-number">02 · EXPLORE</div><h3>Test a different path</h3><p>Change income, withholding, or retirement savings and compare the result instantly.</p></div>
      <div class="feature-card"><div class="feature-number">03 · UNDERSTAND</div><h3>Ask without the jargon</h3><p>Use the AI coach to translate calculated results into straightforward explanations.</p></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption("Educational 2026 projection. TaxLens does not prepare or file tax returns.")
