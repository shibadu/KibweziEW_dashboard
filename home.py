import streamlit as st
from datetime import date

st.set_page_config(page_title="Welcome | Health Data Dashboards", layout="centered")

st.title("📊 Health Data Dashboards")

st.markdown("""
Welcome to the integrated health monitoring dashboards.

These dashboards provide real-time data visualizations to support program performance tracking.

**Available Dashboards:**

- 🔬 **HTS Summary Dashboard** — Track screening, testing, and HIVST by date, counselor, and facility.
- 📅 **Weekly Appointment Dashboard** — Monitor appointment adherence, tracing, and follow-ups week by week.

Use the sidebar on the left to navigate between dashboards.

---

🗓️ *Today's date:* **{today}**

🛠️ *Built with [Streamlit](https://streamlit.io/)*  
📁 *Hosted via GitHub*
""".format(today=date.today().strftime('%B %d, %Y')))

st.image("https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=250)
