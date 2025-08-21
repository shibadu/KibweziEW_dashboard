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
@st.cache_data
def fetch_kobo_data(token, asset_uid):
    """Fetches and normalizes data from KoboToolbox API with labels."""
    headers = {"Authorization": f"Token {token}"}
    url = f"https://kf.kobotoolbox.org/api/v2/assets/{asset_uid}/data.json"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        raw_data = response.json().get('results', [])
        df = pd.json_normalize(raw_data)

        # Map the internal field names to human-readable labels
        column_mapping = {
            'Name of health facility:': 'Facility',
            'What was the reason of Missing an Appointment/LTFU (interrupting treatment) as per the last tracing attempt': 'Reason for Missing Appointment',
            'Client status on day of audit': 'Client Status',
            'Gender': 'Gender',
            'Client Type': 'Client Type',
            'Number of Missed appointments  in the last 1 year': 'Missed Appointments'
        }
        df = df.rename(columns=column_mapping)
        return df

    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to fetch data from KoboToolbox. Please check your token and asset UID. Error: {e}")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# --- Main App ---
st.title("LTFU Audit Data Summary")

df = fetch_kobo_data(KOBO_TOKEN, ASSET_UID)

if df is not None:
    st.success("Data loaded successfully.")

    col1, col2 = st.columns(2)

    with col1:
        # --- 1. Table with Facilities (Valuecounts and with a total at the end) ---
        st.header("1. Facilities Audited")
        if 'Facility' in df.columns:
            facilities_counts = df['Facility'].value_counts().reset_index()
            facilities_counts.columns = ['Facility', 'Count']
            total_count = facilities_counts['Count'].sum()
            total_row = pd.DataFrame([['**Total**', total_count]], columns=['Facility', 'Count'])
            facilities_table = pd.concat([facilities_counts, total_row], ignore_index=True)
            st.dataframe(facilities_table.style.format({'Count': '{:.0f}'}), hide_index=True)

            # --- 2. Horizontal Bar Graph for Facilities ---
            st.header("2. Clients per Health Facility")
            base = alt.Chart(facilities_counts).encode(
                y=alt.Y('Facility', sort='-x', title='Facility'),
                x=alt.X('Count', title='Count of Clients'),
                tooltip=['Facility', 'Count']
            )
            bar_chart = base.mark_bar()
            text_labels = base.mark_text(align='left', baseline='middle', dx=3).encode(
                text=alt.Text('Count', format=',d')
            )
            chart = (bar_chart + text_labels).properties(
                title='Number of Clients per Health Facility'
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("The 'Facility' column was not found. Please check your data source.")

    with col2:
        # --- 3. Bar Chart for Gender Distribution ---
        st.header("3. Client Gender Distribution")
        if 'Gender' in df.columns:
            gender_counts = df['Gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Count']
            gender_chart = alt.Chart(gender_counts).mark_bar().encode(
                x=alt.X('Gender', title='Gender'),
                y=alt.Y('Count', title='Count of Clients'),
                tooltip=['Gender', 'Count']
            ).properties(
                title='Distribution of Clients by Gender'
            )
            st.altair_chart(gender_chart, use_container_width=True)
        else:
            st.warning("The 'Gender' column was not found.")

        # --- 4. Pie Chart for Client Type ---
        st.header("4. Client Type Distribution")
        if 'Client Type' in df.columns:
            client_type_counts = df['Client Type'].value_counts().reset_index()
            client_type_counts.columns = ['Client Type', 'Count']
            pie_chart = alt.Chart(client_type_counts).mark_arc(outerRadius=120).encode(
                theta=alt.Theta("Count", stack=True),
                color=alt.Color("Client Type", title="Client Type"),
                order=alt.Order("Count", sort="descending"),
                tooltip=["Client Type", "Count"]
            ).properties(
                title='Distribution of Clients by Type'
            )
            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.warning("The 'Client Type' column was not found.")

    st.markdown("---")
    st.header("Detailed Summaries")
    col3, col4 = st.columns(2)

    with col3:
        # --- 5. Summary of Reasons for Missing Appointment ---
        st.subheader("5. Reasons for Missing an Appointment")
        if 'Reason for Missing Appointment' in df.columns:
            reasons_counts = df['Reason for Missing Appointment'].value_counts().reset_index()
            reasons_counts.columns = ['Reason', 'Count']
            total_reasons = reasons_counts['Count'].sum()
            total_reasons_row = pd.DataFrame([['**Total**', total_reasons]], columns=['Reason', 'Count'])
            reasons_table = pd.concat([reasons_counts, total_reasons_row], ignore_index=True)
            st.dataframe(reasons_table.style.format({'Count': '{:.0f}'}), hide_index=True)
        else:
            st.warning("The 'Reason for Missing Appointment' column was not found.")

    with col4:
        # --- 6. Summary of Client Status on Day of Audit ---
        st.subheader("6. Client Status on Day of Audit")
        if 'Client Status' in df.columns:
            status_counts = df['Client Status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            total_status = status_counts['Count'].sum()
            total_status_row = pd.DataFrame([['**Total**', total_status]], columns=['Status', 'Count'])
            status_table = pd.concat([status_counts, total_status_row], ignore_index=True)
            st.dataframe(status_table.style.format({'Count': '{:.0f}'}), hide_index=True)
        else:
            st.warning("The 'Client Status' column was not found.")