import streamlit as st
import pandas as pd
import plotly.express as px

# Load parsed and anomaly data
df = pd.read_csv("parsed_cloudtrail_events.csv")
df['eventTime'] = pd.to_datetime(df['eventTime'])

try:
    anomalies = pd.read_csv("anomaly_events.csv")
    anomalies['hour'] = pd.to_datetime(anomalies['hour'])
except FileNotFoundError:
    anomalies = pd.DataFrame()

# Sidebar
st.sidebar.title("🔍 Filter Logs")
selected_event = st.sidebar.multiselect("Event Name", df['eventName'].unique(), default=list(df['eventName'].unique()))
selected_role = st.sidebar.multiselect("Role", df.get('role', ['Unknown']).unique(), default=df.get('role', ['Unknown']).unique())

# Apply filters
filtered_df = df[(df['eventName'].isin(selected_event)) & (df.get('role', 'Unknown').isin(selected_role))]

# Title
st.title("☁️ Cloud Access Monitoring Dashboard")
st.markdown("Real-time anomaly detection and user access logs from AWS CloudTrail")

# Overview stats
st.subheader("📊 Overview")
st.write(f"Total Login Events: {len(df)}")
st.write(f"Filtered Events: {len(filtered_df)}")

# Line chart: Access over time
st.subheader("📈 Access Trends by Hour")
df['hour'] = df['eventTime'].dt.floor('H')
access_by_hour = df.groupby(['hour']).size().reset_index(name='count')

fig = px.line(access_by_hour, x='hour', y='count', title="Hourly Login Volume")
st.plotly_chart(fig)

# Anomaly Visualization
if not anomalies.empty:
    st.subheader("🚨 Anomalies Detected")
    fig_anom = px.line(anomalies, x='hour', y=anomalies.columns[1:], title="Detected Anomalies by Role")
    st.plotly_chart(fig_anom)
else:
    st.info("No anomalies detected in current dataset.")

# Show full log table
st.subheader("📋 Raw Access Logs")
st.dataframe(filtered_df.head(100))