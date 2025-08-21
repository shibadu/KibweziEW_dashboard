import streamlit as st
import pandas as pd
import altair as alt
import requests

# --- Configuration ---
KOBO_TOKEN = "5d64990c18958166334c29d4664653d2d0c20649"
ASSET_UID = "abwfEv8qS6WJNPkSgCdYsn"
st.set_page_config(page_title="LTFU AUDIT Dashboard", layout="wide")

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

# --- Sidebar ---
st.sidebar.title("LTFU Audit Dashboard")

# --- Functions ---
def load_data():
    """Fetches data from KoboToolbox API."""
    url = f"https://kobo.humanitarianresponse.info/api/v2/assets/{ASSET_UID}/data.csv"
    headers = {"Authorization": f"Token {KOBO_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return pd.read_csv(url, storage_options=headers)
    else:
        st.error(f"Failed to fetch data from KoboToolbox. Status code: {response.status_code}")
        return None

# --- Main app ---
df = load_data()

if df is not None:
    st.title("LTFU Audit Data Summary")

    # --- 1. Table with Facilities (Valuecounts and with a total at the end) ---
    st.header("1. Facilities Audited")
    facilities_counts = df['Name of health facility:'].value_counts().reset_index()
    facilities_counts.columns = ['Facility', 'Count']
    total_count = facilities_counts['Count'].sum()
    total_row = pd.DataFrame([['**Total**', total_count]], columns=['Facility', 'Count'])
    facilities_table = pd.concat([facilities_counts, total_row], ignore_index=True)
    st.dataframe(facilities_table.style.format({'Count': '{:.0f}'}), hide_index=True)

    # --- 2. Horizontal Bar Graph with value labels ---
    st.header("2. Number of Clients per Health Facility")
    base = alt.Chart(facilities_counts).encode(
        y=alt.Y('Facility', sort='-x', title='Facility'),
        x=alt.X('Count', title='Count of Clients'),
    )
    bar_chart = base.mark_bar()
    text_labels = base.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(
        text=alt.Text('Count', format=',d')
    )
    chart = (bar_chart + text_labels).properties(
        title='Number of Clients per Health Facility'
    )
    st.altair_chart(chart, use_container_width=True)

    # --- 3. Summary of 'Reason of Missing an Appointment/LTFU' ---
    st.header("3. Reasons for Missing an Appointment")
    reasons_counts = df['What was the reason of Missing an Appointment/LTFU (interrupting treatment) as per the last tracing attempt'].value_counts().reset_index()
    reasons_counts.columns = ['Reason', 'Count']
    total_reasons = reasons_counts['Count'].sum()
    total_reasons_row = pd.DataFrame([['**Total**', total_reasons]], columns=['Reason', 'Count'])
    reasons_table = pd.concat([reasons_counts, total_reasons_row], ignore_index=True)
    st.dataframe(reasons_table.style.format({'Count': '{:.0f}'}), hide_index=True)

    # --- 4. Summary of 'Client status on day of audit' ---
    st.header("4. Client Status on Day of Audit")
    status_counts = df['Client status on day of audit'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    total_status = status_counts['Count'].sum()
    total_status_row = pd.DataFrame([['**Total**', total_status]], columns=['Status', 'Count'])
    status_table = pd.concat([status_counts, total_status_row], ignore_index=True)
    st.dataframe(status_table.style.format({'Count': '{:.0f}'}), hide_index=True)