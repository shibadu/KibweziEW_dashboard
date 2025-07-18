
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

        # Rename and process date columns
        df = df.rename(columns={
            'From (Friday Previous week):': 'date_start',
            'To (Thursday reporting week):': 'date_end'
        })

        df['date_start'] = pd.to_datetime(df['date_start'], errors='coerce')
        df['date_end'] = pd.to_datetime(df['date_end'], errors='coerce')

        # Sidebar date range filter
        min_date = df['date_start'].min().date()
        max_date = df['date_end'].max().date()
        start_filter = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        end_filter = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

        # Filter table data
        filtered_df = df[(df['week_start'].dt.date >= start_filter) & (df['week_end'].dt.date <= end_filter)].copy()

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
        df = df.dropna(subset=['date_start', 'date_end'])
        df['week'] = df['date_start'].dt.strftime('%Y-%m-%d') + ' to ' + df['date_end'].dt.strftime('%Y-%m-%d')

        weekly = df.groupby('week').agg({
            'booked': 'sum',
            'honored': 'sum',
            'missed': 'sum',
            'traced_back': 'sum'
        }).reset_index()

        weekly['% Honored'] = (weekly['honored'] / weekly['booked']) * 100
        weekly['% Traced Back'] = np.where(weekly['missed'] > 0, (weekly['traced_back'] / weekly['missed']) * 100, np.nan)

        # Plot 1: % Honored
        st.subheader("📈 Weekly % Honored with Booked and Honored Counts")
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        x = range(len(weekly))
        bar_width = 0.35
        ax1.bar([i - bar_width/2 for i in x], weekly['booked'], width=bar_width, label='Booked', color='skyblue')
        ax1.bar([i + bar_width/2 for i in x], weekly['honored'], width=bar_width, label='Honored', color='seagreen')
        ax1.set_xticks(x)
        ax1.set_xticklabels(weekly['week'], rotation=45, ha='right')
        ax1.set_ylabel('Number of Clients')
        ax1.legend(loc='upper left')

        ax2 = ax1.twinx()
        ax2.plot(x, weekly['% Honored'], color='darkgreen', marker='o', label='% Honored')
        for i, val in enumerate(weekly['% Honored']):
            ax2.text(i, val + 1, f'{val:.1f}%', color='darkgreen', ha='center')
        ax2.set_ylabel('% Honored')
        ax2.legend(loc='upper right')
        st.pyplot(fig1)

        # Plot 2: % Traced Back
        st.subheader("📈 Weekly % Traced Back with Missed and Traced Counts")
        fig2, ax1 = plt.subplots(figsize=(12, 6))
        ax1.bar([i - bar_width/2 for i in x], weekly['missed'], width=bar_width, label='Missed', color='salmon')
        ax1.bar([i + bar_width/2 for i in x], weekly['traced_back'], width=bar_width, label='Traced Back', color='orange')
        ax1.set_xticks(x)
        ax1.set_xticklabels(weekly['week'], rotation=45, ha='right')
        ax1.set_ylabel('Number of Clients')
        ax1.legend(loc='upper left')

        ax2 = ax1.twinx()
        ax2.plot(x, weekly['% Traced Back'], color='red', marker='o', label='% Traced Back')
        for i, val in enumerate(weekly['% Traced Back']):
            if pd.notna(val):
                ax2.text(i, val + 1, f'{val:.1f}%', color='red', ha='center')
        ax2.set_ylabel('% Traced Back')
        ax2.legend(loc='upper right')
        st.pyplot(fig2)

    except Exception as e:
        st.error(f"Error loading data: {e}")
else:
    st.info("Please enter your Kobo Token and Asset UID to load data.")
