
import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Weekly Appointment Dashboard", layout="wide")

# --- Sidebar: Configuration ---
st.sidebar.title("Data Source")
KOBO_TOKEN = st.sidebar.text_input("Enter Kobo Token", type="password", value="5d64990c18958166334c29d4664653d2d0c20649")
ASSET_UID = st.sidebar.text_input("Enter Asset UID", value="acbnBWmKaSwFH3duCpXeYz")

# Fetch KoboToolbox data
@st.cache_data(ttl=3600)
def fetch_kobo_data(token, asset_uid):
    headers = {'Authorization': f'Token {token}'}
    url = f'https://kf.kobotoolbox.org/api/v2/assets/{asset_uid}/data.json'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    raw_data = response.json()['results']
    return pd.json_normalize(raw_data)

# Load data
if KOBO_TOKEN and ASSET_UID:
    try:
        df = fetch_kobo_data(KOBO_TOKEN, ASSET_UID)

        st.success("Data loaded successfully.")

        # Select numeric columns for conversion
        num_cols = [
            'booked', 'ushauri', 'prior_call', 'messages', 'rescheduled',
            'honored', 'missed', 'traced_back', 'traced_back_physical',
            'traced_back_phone_only', 'missed_not_back'
        ]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Date column processing
        if 'start' in df.columns:
            df['start_date'] = pd.to_datetime(df['start'], errors='coerce')
            df['week'] = df['start_date'].dt.to_period('W').astype(str)
            weekly_summary = df.groupby('week')[num_cols].sum().reset_index()

            # --- Main Plot ---
            st.subheader("📊 Weekly Appointment Trends")
            fig, ax = plt.subplots(figsize=(14, 6))
            weekly_summary.set_index('week')[['booked', 'honored', 'missed']].plot(kind='bar', stacked=False, ax=ax)
            ax.set_ylabel("Counts")
            ax.set_title("Weekly Booked vs Honored vs Missed Appointments")
            ax.legend(title="Status")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)

            # --- Summary Table ---
            st.subheader("📋 Weekly Summary Table")
            st.dataframe(weekly_summary)

        else:
            st.warning("Missing 'start' column for date processing.")

    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.info("Please enter your Kobo Token and Asset UID to load data.")
