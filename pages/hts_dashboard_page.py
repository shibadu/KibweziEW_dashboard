import streamlit as st
import pandas as pd
import requests

# Page config
st.set_page_config(page_title="HTS Dashboard", layout="wide")
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
# Title
st.title("HTS Data Dashboard")

# KoboToolbox credentials
KOBO_TOKEN = '5d64990c18958166334c29d4664653d2d0c20649'
ASSET_UID = 'aLUUWLzQ2Lz6W28asUxvQ6'

# --- Fetch KoboToolbox Data ---
@st.cache_data(ttl=3600)
def fetch_kobo_data(token, asset_uid):
    headers = {'Authorization': f'Token {token}'}
    url = f'https://kf.kobotoolbox.org/api/v2/assets/{asset_uid}/data.json'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    raw_data = response.json()['results']
    return pd.json_normalize(raw_data)

# --- Load and Process Data ---
if KOBO_TOKEN and ASSET_UID:
    try:
        # Load data
        df_hts = fetch_kobo_data(KOBO_TOKEN, ASSET_UID)
        st.success("Data loaded successfully.")

        # --- Preprocess ---
        cols_to_numeric = [
            'workload', 'screened', 'under15_Tested', 'over15_Tested', 'total_test',
            'total_pos', 'pns_pos', 'prep_new', 'prep_newpgbf', 'S', 'hivst'
        ]
        df_hts[cols_to_numeric] = df_hts[cols_to_numeric].apply(pd.to_numeric, errors='coerce')
        df_hts['date'] = pd.to_datetime(df_hts['date_test'])
        df_hts['% Screened'] = (df_hts['screened'] / df_hts['workload']) * 100
        df_hts['% Positive'] = (df_hts['total_pos'] / df_hts['total_test']) * 100

        # --- Sidebar Filters ---
        st.sidebar.header("Filters")

        # Date filter
        min_date = df_hts['date'].min()
        max_date = df_hts['date'].max()
        start_filter = st.sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
        end_filter = st.sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)

        # Counselor filter
        counselors = ['All'] + sorted(df_hts['counselor_name'].dropna().unique().tolist())
        selected_counselor = st.sidebar.selectbox("Select Counselor", counselors)

        # Facility filter
        facilities = ['All'] + sorted(df_hts['health_facility'].dropna().unique().tolist())
        selected_facility = st.sidebar.selectbox("Select Facility", facilities)

        # --- Apply Filters ---
        df_hts_filtered = df_hts[
            (df_hts['date'] >= pd.to_datetime(start_filter)) &
            (df_hts['date'] <= pd.to_datetime(end_filter))
        ]

        if selected_counselor != 'All':
            df_hts_filtered = df_hts_filtered[df_hts_filtered['counselor_name'] == selected_counselor]

        if selected_facility != 'All':
            df_hts_filtered = df_hts_filtered[df_hts_filtered['health_facility'] == selected_facility]

        # --- Summary Function ---
        def compute_summary(df, group_by):
            summary = df.groupby(group_by)[cols_to_numeric].sum().reset_index()
            summary['% Screened'] = (summary['screened'] / summary['workload']) * 100
            summary['% Positive'] = (summary['total_pos'] / summary['total_test']) * 100

            # Total row
            total_row = summary[cols_to_numeric].sum()
            total_row[group_by] = 'Total'
            total_row['% Screened'] = (total_row['screened'] / total_row['workload']) * 100
            total_row['% Positive'] = (total_row['total_pos'] / total_row['total_test']) * 100

            summary = pd.concat([summary, pd.DataFrame([total_row])], ignore_index=True)
            return summary

        # --- Highlight Function ---
        def highlight_percent(val):
            if isinstance(val, str): return ''
            if val >= 90: return 'background-color: green'
            elif val >= 50: return 'background-color: yellow'
            else: return 'background-color: red'

        # --- Display Summaries ---
        format_dict = {
            'workload': '{:,.0f}', 'screened': '{:,.0f}', '% Screened': '{:.1f}%',
            'total_test': '{:,.0f}', 'total_pos': '{:,.0f}', '% Positive': '{:.1f}%',
            'hivst': '{:,.0f}'
        }

        st.subheader("Summary by Date")
        summary_date = compute_summary(df_hts_filtered, 'date')
        st.dataframe(summary_date.style.applymap(highlight_percent, subset=['% Screened', '% Positive']).format(format_dict))

        st.subheader("Summary by Counselor")
        summary_counselor = compute_summary(df_hts_filtered, 'counselor_name')
        st.dataframe(summary_counselor.style.applymap(highlight_percent, subset=['% Screened', '% Positive']).format(format_dict))

        st.subheader("Summary by Facility")
        summary_facility = compute_summary(df_hts_filtered, 'health_facility')
        st.dataframe(summary_facility.style.applymap(highlight_percent, subset=['% Screened', '% Positive']).format(format_dict))

    except Exception as e:
        st.error(f"Error loading data: {e}")

else:
    st.info("Please enter your Kobo Token and Asset UID in the settings.")