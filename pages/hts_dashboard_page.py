import streamlit as st
import pandas as pd
import requests

# Page config
st.set_page_config(page_title="HTS Dashboard", layout="wide")

# Title
st.title("HTS Data Dashboard")

# KoboToolbox credentials
KOBO_TOKEN = '5d64990c18958166334c29d4664653d2d0c20649'
ASSET_UID = 'aLUUWLzQ2Lz6W28asUxvQ6'

@st.cache_data
def fetch_data():
    headers = {'Authorization': f'Token {KOBO_TOKEN}'}
    url = f'https://kf.kobotoolbox.org/api/v2/assets/{ASSET_UID}/data.json?format=labels'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()['results']
    return pd.json_normalize(data)

# Load data
df_hts = fetch_data()

# Preprocess
cols_to_numeric = ['workload', 'screened', 'total_test', 'total_pos', 'hivst']
df_hts[cols_to_numeric] = df_hts[cols_to_numeric].apply(pd.to_numeric, errors='coerce')
df_hts['date'] = pd.to_datetime(df_hts['date_test'])
df_hts['% Screened'] = (df_hts['screened'] / df_hts['workload']) * 100
df_hts['% Positive'] = (df_hts['total_pos'] / df_hts['total_test']) * 100

# Summary function
def compute_summary(df, group_by):
    summary = df.groupby(group_by)[cols_to_numeric].sum().reset_index()
    summary['% Screened'] = (summary['screened'] / summary['workload']) * 100
    summary['% Positive'] = (summary['total_pos'] / summary['total_test']) * 100
    total_row = summary[cols_to_numeric].sum()
    total_row[group_by] = 'Total'
    total_row['% Screened'] = (total_row['screened'] / total_row['workload']) * 100
    total_row['% Positive'] = (total_row['total_pos'] / total_row['total_test']) * 100
    summary = pd.concat([summary, pd.DataFrame([total_row])], ignore_index=True)
    return summary

# Highlight function
def highlight_percent(val):
    if isinstance(val, str): return ''
    if val >= 90: return 'background-color: green'
    elif val >= 50: return 'background-color: yellow'
    else: return 'background-color: red'

# Display summaries
st.subheader("Summary by Date")
summary_date = compute_summary(df_hts, 'date')
st.dataframe(summary_date.style.applymap(highlight_percent, subset=['% Screened', '% Positive']).format({
    'workload': '{:,.0f}', 'screened': '{:,.0f}', '% Screened': '{:.1f}%',
    'total_test': '{:,.0f}', 'total_pos': '{:,.0f}', '% Positive': '{:.1f}%',
    'hivst': '{:,.0f}'
}))

st.subheader("Summary by Counselor")
summary_counselor = compute_summary(df_hts, 'counselor_name')
st.dataframe(summary_counselor.style.applymap(highlight_percent, subset=['% Screened', '% Positive']).format({
    'workload': '{:,.0f}', 'screened': '{:,.0f}', '% Screened': '{:.1f}%',
    'total_test': '{:,.0f}', 'total_pos': '{:,.0f}', '% Positive': '{:.1f}%',
    'hivst': '{:,.0f}'
}))

st.subheader("Summary by Facility")
summary_facility = compute_summary(df_hts, 'health_facility')
st.dataframe(summary_facility.style.applymap(highlight_percent, subset=['% Screened', '% Positive']).format({
    'workload': '{:,.0f}', 'screened': '{:,.0f}', '% Screened': '{:.1f}%',
    'total_test': '{:,.0f}', 'total_pos': '{:,.0f}', '% Positive': '{:.1f}%',
    'hivst': '{:,.0f}'
}))
