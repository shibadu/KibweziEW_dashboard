import streamlit as st
import pandas as pd
import altair as alt
import requests
import matplotlib.pyplot as plt
# --- Configuration ---
KOBO_TOKEN = '5d64990c18958166334c29d4664653d2d0c20649'  # Replace with your actual token
ASSET_UID = 'abwfEv8qS6WJNPkSgCdYsn'  # Replace with your actual asset UID

# --- Functions ---
@st.cache_data(ttl=3600)
def fetch_kobo_data(token, asset_uid):
    headers = {'Authorization': f'Token {token}'}
    url = f'https://kf.kobotoolbox.org/api/v2/assets/{asset_uid}/data.json'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    raw_data = response.json().get('results', [])
    return pd.json_normalize(raw_data)

# --- Main app ---
st.set_page_config(page_title="LTFU AUDIT Dashboard", layout="wide")
st.sidebar.title("LTFU Audit Dashboard")

try:
    df = fetch_kobo_data(KOBO_TOKEN, ASSET_UID)
    st.success("Data loaded successfully.")
except Exception as e:
    st.error(f"Error loading data: {e}")
    df = None

if df is not None:
    st.title("LTFU Audit Data Summary")

    # --- 1. Table with Facilities ---
    st.header("1. Facilities Audited")
    if 'health_facility' in df.columns:
        facilities_counts = df['health_facility'].value_counts().reset_index()
        facilities_counts.columns = ['Facility', 'Count']
        total_count = facilities_counts['Count'].sum()
        total_row = pd.DataFrame([['**Total**', total_count]], columns=['Facility', 'Count'])
        facilities_table = pd.concat([facilities_counts, total_row], ignore_index=True)
        st.dataframe(facilities_table.style.format({'Count': '{:.0f}'}), hide_index=True)
    else:
        st.warning("Column 'Name of health facility:' not found in data.")

    # --- 2. Reasons for Missing Appointment ---
    st.header("2. Reasons for Missing an Appointment")
    if 'reasons' in df.columns:
        reasons_counts = df['reasons'].value_counts().reset_index()
        reasons_counts.columns = ['Reason', 'Count']
        chart = alt.Chart(reasons_counts).mark_bar().encode(
            x=alt.X('Reason', sort='-y'),
            y='Count',
            color='Reason'
        ).properties(title="Reasons for Missing an Appointment")
        st.altair_chart(chart, use_container_width=True)

    # --- 3. Client Status on Day of Audit ---
    st.header("3. Client Status on Day of Audit")
    if 'status' in df.columns:
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        chart = alt.Chart(status_counts).mark_bar().encode(
            x=alt.X('Status', sort='-y'),
            y='Count',
            color='Status'
        ).properties(title="Client Status on Day of Audit")
        st.altair_chart(chart, use_container_width=True)

    # --- 4. Profession Distribution ---
    st.header("4. Profession Distribution")
    if 'prof' in df.columns:
        prof_counts = df['prof'].value_counts().reset_index()
        prof_counts.columns = ['Profession', 'Count']
        chart = alt.Chart(prof_counts).mark_bar().encode(
            x=alt.X('Profession', sort='-y'),
            y='Count',
            color='Profession'
        ).properties(title="Profession Breakdown")
        st.altair_chart(chart, use_container_width=True)

    # --- 5. Age at Last Visit Histogram ---
    st.header("5. Age at Last Visit")
    if 'age' in df.columns and 'date_last' in df.columns:
        df['age'] = pd.to_datetime(df['age'], errors='coerce')
        df['date_last'] = pd.to_datetime(df['date_last'], errors='coerce')
        df['age_at_last_visit'] = (df['date_last'] - df['age']).dt.days // 365
        age_data = df.dropna(subset=['age_at_last_visit'])
        chart = alt.Chart(age_data).mark_bar().encode(
            alt.X("age_at_last_visit:Q", bin=alt.Bin(maxbins=20), title="Age at Last Visit (Years)"),
            alt.Y("count()", title="Number of Clients")
        ).properties(title="Age at Last Visit Distribution")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Required columns 'age' and 'date_last' not found or could not be parsed.")
