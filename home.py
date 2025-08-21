import streamlit as st
from datetime import date

st.set_page_config(page_title="Welcome | Kibwezi EW Data Dashboards", layout="centered")

# Hide Streamlit branding and footer
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob, .viewerBadge_link__1S137 {display: none;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("📊 Kibwezi EW Data Dashboards")

st.markdown("""
Welcome to team Kibwezi EW data dashboards.

These dashboards provide near real-time data visualizations to support the team's performance tracking.

**Available Dashboards:**

- 🔬 **HTS Per Counselor Summary Dashboard** — Track screening, testing, and HIVST by date, counselor, and facility.
- 📅 **Weekly Appointment Dashboard** — Monitors appointment adherence, tracing, and follow-ups week by week.
- 🏥 **LTFU Audit Dashboard** — Summarizes facilities audited, clients per facility, and LTFU status.            

Use the sidebar on the left to navigate between dashboards.

---

🗓️ *Today's date:* **{today}**

""".format(today=date.today().strftime('%B %d, %Y')))

st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=250)
