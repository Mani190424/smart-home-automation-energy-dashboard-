
import streamlit as st
import pandas as pd

# Load CSV
df = pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

# Sidebar filters
st.sidebar.title("🔧 Filters")
date_range = st.sidebar.date_input("Select Date Range", [df['Timestamp'].min(), df['Timestamp'].max()])

# Filter data by date
if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df['Timestamp'] >= pd.to_datetime(start_date)) & (df['Timestamp'] <= pd.to_datetime(end_date))]

# Main title
st.title("📊 Smart Home Energy Dashboard")

# Notifications
st.subheader("🔔 Smart Alerts")
alerts = []
if df["Temperature"].mean() > 30:
    alerts.append("⚠️ High average temperature!")
if df["Humidity"].min() < 30 or df["Humidity"].max() > 70:
    alerts.append("⚠️ Humidity out of comfort range!")
if df["Power"].mean() > 500:
    alerts.append("⚠️ High power usage detected!")

if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("✅ All systems normal.")

# Show data (optional)
with st.expander("🔍 View Filtered Data"):
    st.dataframe(df)

# Export CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Filtered Data", csv, "filtered_data.csv", "text/csv")
