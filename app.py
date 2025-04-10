import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 60 seconds (60000 ms)
st_autorefresh(interval=60000, key="datarefresh")

# Load data
df = pd.read_csv("parsed_cloudtrail_events.csv")
df['eventTime'] = pd.to_datetime(df['eventTime'])

# Assign roles if missing
if 'role' not in df.columns:
    def categorize_user(user):
        user = str(user).lower()
        if 'admin' in user:
            return 'Admin'
        elif 'dev' in user:
            return 'Developer'
        elif 'ext' in user:
            return 'External'
        elif 'arunesh' in user:
            return 'Root'  # or 'Developer', your choice
        else:
            return 'Unknown'
    df['role'] = df['userName'].apply(categorize_user)

# Load anomalies
try:
    anomalies = pd.read_csv("anomaly_events.csv")
    anomalies['hour'] = pd.to_datetime(anomalies['hour'])
except FileNotFoundError:
    anomalies = pd.DataFrame()

# Sidebar filters
st.sidebar.title("🔍 Filter Logs")
event_options = df['eventName'].unique()
role_options = df['role'].unique()

selected_event = st.sidebar.multiselect("Event Name", event_options, default=list(event_options))
selected_role = st.sidebar.multiselect("Role", role_options, default=list(role_options))

filtered_df = df[(df['eventName'].isin(selected_event)) & (df['role'].isin(selected_role))]

# Main UI
st.title("☁️ Cloud Access Monitoring Dashboard")
st.markdown("Real-time anomaly detection and user access logs from AWS CloudTrail")

st.subheader("📊 Overview")
st.write(f"Total Login Events: {len(df)}")
st.write(f"Filtered Events: {len(filtered_df)}")

# Trends
st.subheader("📈 Access Trends by Hour")
df['hour'] = df['eventTime'].dt.floor('H')
access_by_hour = df.groupby(['hour']).size().reset_index(name='count')

fig = px.line(access_by_hour, x='hour', y='count', title="Hourly Login Volume")
st.plotly_chart(fig)

# Anomalies
if not anomalies.empty:
    st.subheader("🚨 Anomalies Detected")
    fig_anom = px.line(anomalies, x='hour', y=anomalies.columns[1:], title="Detected Anomalies by Role")
    st.plotly_chart(fig_anom)
else:
    st.info("No anomalies detected in current dataset.")

# Raw table
st.subheader("📋 Raw Access Logs")
st.dataframe(filtered_df.head(100))
