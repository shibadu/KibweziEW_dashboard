
import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
# Load the data
df = pd.read_csv("kobo_data.csv")

st.set_page_config(page_title="LTFU AUDIT Dashboard", layout="wide")
st.sidebar.title("LTFU Audit Dashboard")

st.title("LTFU Audit Data Summary")

# --- 1. Facilities Audited ---
st.header("1. Facilities Audited")
facilities_counts = df['health_facility'].value_counts().reset_index()
facilities_counts.columns = ['Facility', 'Count']
total_count = facilities_counts['Count'].sum()
total_row = pd.DataFrame([['**Total**', total_count]], columns=['Facility', 'Count'])
facilities_table = pd.concat([facilities_counts, total_row], ignore_index=True)
st.dataframe(facilities_table.style.format({'Count': '{:.0f}'}), hide_index=True)

# --- 2. Number of Clients per Health Facility ---
st.header("2. Number of Clients per Health Facility")
base = alt.Chart(facilities_counts).encode(
    y=alt.Y('Facility', sort='-x', title='Facility'),
    x=alt.X('Count', title='Count of Clients'),
)
bar_chart = base.mark_bar()
text_labels = base.mark_text(
    align='left', baseline='middle', dx=3
).encode(
    text=alt.Text('Count', format=',d')
)
chart = (bar_chart + text_labels).properties(title='Number of Clients per Health Facility')
st.altair_chart(chart, use_container_width=True)

# --- 3. Reasons for Missing an Appointment ---
st.header("3. Reasons for Missing an Appointment")
if 'reasons' in df.columns:
    reasons_counts = df['reasons'].value_counts().reset_index()
    reasons_counts.columns = ['Reason', 'Count']
    total_reasons = reasons_counts['Count'].sum()
    total_reasons_row = pd.DataFrame([['**Total**', total_reasons]], columns=['Reason', 'Count'])
    reasons_table = pd.concat([reasons_counts, total_reasons_row], ignore_index=True)
    st.dataframe(reasons_table.style.format({'Count': '{:.0f}'}), hide_index=True)
else:
    st.warning("Column 'reasons' not found in data.")

# --- 4. Client Status on Day of Audit ---
st.header("4. Client Status on Day of Audit")
if 'status' in df.columns:
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    total_status = status_counts['Count'].sum()
    total_status_row = pd.DataFrame([['**Total**', total_status]], columns=['Status', 'Count'])
    status_table = pd.concat([status_counts, total_status_row], ignore_index=True)
    st.dataframe(status_table.style.format({'Count': '{:.0f}'}), hide_index=True)
else:
    st.warning("Column 'status' not found in data.")

# --- 5. Age Distribution ---
st.header("5. Age Distribution")
if 'age' in df.columns:
    df['age'] = pd.to_datetime(df['age'], errors='coerce')
    df['age_years'] = (pd.Timestamp('today') - df['age']).dt.days // 365
    age_chart = alt.Chart(df.dropna(subset=['age_years'])).mark_bar().encode(
        alt.X("age_years:Q", bin=alt.Bin(maxbins=20), title="Age (Years)"),
        alt.Y("count()", title="Number of Clients")
    ).properties(title="Age Distribution of Clients")
    st.altair_chart(age_chart, use_container_width=True)
else:
    st.warning("Column 'age' not found in data.")

# --- 6. Gender Breakdown ---
st.header("6. Gender Breakdown")
if 'gender' in df.columns:
    gender_counts = df['gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    gender_chart = alt.Chart(gender_counts).mark_bar().encode(
        x=alt.X('Gender', title='Gender'),
        y=alt.Y('Count', title='Number of Clients'),
        color='Gender'
    ).properties(title="Gender Distribution")
    st.altair_chart(gender_chart, use_container_width=True)
else:
    st.warning("Column 'gender' not found in data.")

# --- 7. Tracing Outcomes ---
st.header("7. Tracing Outcomes")
if 'tracing' in df.columns:
    tracing_counts = df['tracing'].value_counts().reset_index()
    tracing_counts.columns = ['Tracing Outcome', 'Count']
    tracing_chart = alt.Chart(tracing_counts).mark_bar().encode(
        x=alt.X('Tracing Outcome', title='Tracing Outcome'),
        y=alt.Y('Count', title='Number of Clients'),
        color='Tracing Outcome'
    ).properties(title="Tracing Outcomes Summary")
    st.altair_chart(tracing_chart, use_container_width=True)
else:
    st.warning("Column 'tracing' not found in data.")
