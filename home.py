import streamlit as st
from datetime import date

st.set_page_config(page_title="Welcome | Kibwezi EW Data Dashboards", layout="centered")

st.title("📊 Kibwezi EW Data Dashboards")

st.markdown("""
Welcome to team Kibwezi EW monitoring dashboards.

These dashboards provide near real-time data visualizations to support the team's performance tracking.

**Available Dashboards:**

- 🔬 **HTS Per Counselor Summary Dashboard** — Track screening, testing, and HIVST by date, counselor, and facility.
- 📅 **Weekly Appointment Dashboard** — Monitors appointment adherence, tracing, and follow-ups week by week.

Use the sidebar on the left to navigate between dashboards.

---

🗓️ *Today's date:* **{today}**

""".format(today=date.today().strftime('%B %d, %Y')))

st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=250)
