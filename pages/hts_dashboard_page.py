import streamlit as st
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="HTS Summary Dashboard", layout="wide")
st.sidebar.title("HTS Dashboard")

# Load your data
@st.cache_data
def load_data():
    KOBO_TOKEN = '5d64990c18958166334c29d4664653d2d0c20649'
    ASSET_UID = 'aLUUWLzQ2Lz6W28asUxvQ6'

    headers = {
        'Authorization': f'Token {KOBO_TOKEN}'
    }

    url = f'https://kf.kobotoolbox.org/api/v2/assets/{ASSET_UID}/data.json?format=labels'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()['results']
    df_hts = pd.json_normalize(data)
    df_hts['date'] = pd.to_datetime(df_hts['date_test'], errors='coerce')

    # Calculate percentages
    df_hts['% Screened'] = (df_hts['screened'] / df_hts['workload']) * 100
    df_hts['% Positive'] = (df_hts['total_pos'] / df_hts['total_test']) * 100
    return df_hts

# Highlighting function
def highlight_percent(val):
    if isinstance(val, str): return ''
    if val >= 90: return 'background-color: lightgreen'
    elif val >= 50: return 'background-color: khaki'
    else: return 'background-color: lightcoral'

# Load data
df_hts = load_data()

# ---------------------- Page Content ----------------------
st.title("📈 HTS Summary Reports")

# Summary by Date
st.subheader("Summary by Date")
date_summary = df_hts.groupby('date')[['workload', 'screened', 'total_test', 'total_pos', 'hivst']].sum().reset_index()
date_summary['% Screened'] = (date_summary['screened'] / date_summary['workload']) * 100
date_summary['% Positive'] = (date_summary['total_pos'] / date_summary['total_test']) * 100
total_row = date_summary[['workload', 'screened', 'total_test', 'total_pos', 'hivst']].sum()
total_row['date'] = 'Total'
total_row['% Screened'] = (total_row['screened'] / total_row['workload']) * 100
total_row['% Positive'] = (total_row['total_pos'] / total_row['total_test']) * 100
date_summary = pd.concat([date_summary, pd.DataFrame([total_row])], ignore_index=True)
styled_date = date_summary.style.applymap(highlight_percent, subset=['% Screened', '% Positive']) \
    .format({
        'workload': '{:,.0f}', 'screened': '{:,.0f}', '% Screened': '{:.1f}%',
        'total_test': '{:,.0f}', 'total_pos': '{:,.0f}', '% Positive': '{:.1f}%', 'hivst': '{:,.0f}'
    })
st.dataframe(styled_date, use_container_width=True)

# Summary by Counselor
st.subheader("Summary by Counselor")
counselor_summary = df_hts.groupby('counselor')[['workload', 'screened', 'total_test', 'total_pos', 'hivst']].sum().reset_index()
counselor_summary['% Screened'] = (counselor_summary['screened'] / counselor_summary['workload']) * 100
counselor_summary['% Positive'] = (counselor_summary['total_pos'] / counselor_summary['total_test']) * 100
total_row = counselor_summary[['workload', 'screened', 'total_test', 'total_pos', 'hivst']].sum()
total_row['counselor'] = 'Total'
total_row['% Screened'] = (total_row['screened'] / total_row['workload']) * 100
total_row['% Positive'] = (total_row['total_pos'] / total_row['total_test']) * 100
counselor_summary = pd.concat([counselor_summary, pd.DataFrame([total_row])], ignore_index=True)
styled_counselor = counselor_summary.style.applymap(highlight_percent, subset=['% Screened', '% Positive']) \
    .format({
        'workload': '{:,.0f}', 'screened': '{:,.0f}', '% Screened': '{:.1f}%',
        'total_test': '{:,.0f}', 'total_pos': '{:,.0f}', '% Positive': '{:.1f}%', 'hivst': '{:,.0f}'
    })
st.dataframe(styled_counselor, use_container_width=True)

# Summary by Facility
st.subheader("Summary by Facility")
facility_summary = df_hts.groupby('facility')[['workload', 'screened', 'total_test', 'total_pos', 'hivst']].sum().reset_index()
facility_summary['% Screened'] = (facility_summary['screened'] / facility_summary['workload']) * 100
facility_summary['% Positive'] = (facility_summary['total_pos'] / facility_summary['total_test']) * 100
total_row = facility_summary[['workload', 'screened', 'total_test', 'total_pos', 'hivst']].sum()
total_row['facility'] = 'Total'
total_row['% Screened'] = (total_row['screened'] / total_row['workload']) * 100
total_row['% Positive'] = (total_row['total_pos'] / total_row['total_test']) * 100
facility_summary = pd.concat([facility_summary, pd.DataFrame([total_row])], ignore_index=True)
styled_facility = facility_summary.style.applymap(highlight_percent, subset=['% Screened', '% Positive']) \
    .format({
        'workload': '{:,.0f}', 'screened': '{:,.0f}', '% Screened': '{:.1f}%',
        'total_test': '{:,.0f}', 'total_pos': '{:,.0f}', '% Positive': '{:.1f}%', 'hivst': '{:,.0f}'
    })
st.dataframe(styled_facility, use_container_width=True)
