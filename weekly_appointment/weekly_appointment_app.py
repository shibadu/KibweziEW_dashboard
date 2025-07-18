import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from datetime import datetime

KOBO_TOKEN = "5d64990c18958166334c29d4664653d2d0c20649"
ASSET_UID = "acbnBWmKaSwFH3duCpXeYz"

st.set_page_config(page_title="Weekly Appointment Dashboard", layout="wide")

# --- Sidebar: Configuration ---
st.sidebar.title("Appointment Dashboard")

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

        # Convert numeric columns
        num_cols = [
            'booked', 'ushauri', 'prior_call', 'messages', 'rescheduled',
            'honored', 'missed', 'traced_back', 'traced_back_physical',
            'traced_back_phone_only', 'missed_not_back'
        ]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Date processing
        if 'start' in df.columns:
            df['start_date'] = pd.to_datetime(df['start'], errors='coerce')
            df['date_end'] = df['start_date'] + pd.to_timedelta(6 - df['start_date'].dt.weekday, unit='D')
            df['date_end'] = df['date_end'].dt.date
            # Sidebar date range filter
            min_date = df['start_date'].min().date()
            max_date = df['start_date'].max().date()
            start_filter = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
            end_filter = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

            # Filter table data
            filtered_df = df[(df['start_date'].dt.date >= start_filter) & (df['start_date'].dt.date <= end_filter)].copy()

            # Compute metrics
            filtered_df['% Honored'] = (filtered_df['honored'] / filtered_df['booked']) * 100
            filtered_df['% Traced Back'] = np.where(filtered_df['missed'] > 0, (filtered_df['traced_back'] / filtered_df['missed']) * 100, np.nan)
            filtered_df['% Prior Called'] = (filtered_df['prior_call'] / filtered_df['booked']) * 100

            # Display table
            display_df = filtered_df[['health_facility', 'booked', 'honored', '% Honored', 'missed',
                                      'traced_back', '% Traced Back', 'prior_call', '% Prior Called']]
            display_df.columns = ['Facility Name', 'Booked', 'Honored', '% Honored', 'Missed',
                                  'Traced Back', '% Traced Back', 'Prior Calls', '% Prior Called']

            styled_table = display_df.style.background_gradient(
                subset=['% Honored', '% Traced Back', '% Prior Called'],
                cmap='RdYlGn'
            ).format({
                '% Honored': '{:.2f}%',
                '% Traced Back': '{:.2f}%',
                '% Prior Called': '{:.2f}%'
            })

            st.subheader("📊 Weekly Appointment Data (Filtered)")
            st.dataframe(styled_table)

            # Weekly trends for all data
            df['week'] = df['start_date'].dt.to_period('W').apply(lambda r: r.start_time.date().strftime('%Y-%m