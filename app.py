"""TaxLens AI multipage application entry point."""

import streamlit as st

from taxlens_ui import apply_theme, initialize_state, top_navigation


st.set_page_config(page_title="TaxLens AI", page_icon="🔎", layout="wide")
initialize_state()
apply_theme()

pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/forecast.py", title="My Forecast", icon="🌤️"),
    st.Page("views/scenario_lab.py", title="Scenario Lab", icon="🧪"),
    st.Page("views/ai_coach_page.py", title="AI Coach", icon="💬"),
]

navigation = st.navigation(pages, position="hidden")
top_navigation()
navigation.run()
