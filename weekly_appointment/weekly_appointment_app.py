import streamlit as st
import pandas as pd
import numpy as np
import requests
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
            df['date_end'] = df['start_date'] + pd.to_timedelta(6 - df['start_date'].dt.weekday, unit='D')
            df['date_end'] = df['date_end'].dt.date

            # Sidebar filter for week ending
            week_options = sorted(df['date_end'].dropna().unique())
            selected_week = st.sidebar.selectbox("Select Week Ending", week_options)
            df = df[df['date_end'] == selected_week]

            # Compute metrics
            df['% Honored'] = (df['honored'] / df['booked']) * 100
            df['% Traced Back'] = np.where(df['missed'] > 0, (df['traced_back'] / df['missed']) * 100, np.nan)
            df['% Prior Called'] = (df['prior_call'] / df['booked']) * 100

            # Select and rename columns for display
            display_df = df[['health_facility', 'booked', 'honored', '% Honored', 'missed',
                             'traced_back', '% Traced Back', 'prior_call', '% Prior Called']]
            display_df.columns = ['Facility Name', 'Booked', 'Honored', '% Honored', 'Missed',
                                  'Traced Back', '% Traced Back', 'Prior Calls', '% Prior Called']

            # Style the table with color gradients
            styled_table = display_df.style.background_gradient(
                subset=['% Honored', '% Traced Back', '% Prior Called'],
                cmap='RdYlGn'
            ).format({
                '% Honored': '{:.2f}%',
                '% Traced Back': '{:.2f}%',
                '% Prior Called': '{:.2f}%'
            })

            # Display the styled table
            st.subheader("📊 Weekly Appointment Metrics")
            st.dataframe(styled_table)

        else:
            st.warning("Missing 'start' column for date processing.")

    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.info("Please enter your Kobo Token and Asset UID to load data.")
