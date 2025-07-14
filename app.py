
import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

# Sidebar
st.sidebar.title("🔍 Filters")

# Date range filter
min_date, max_date = df["Timestamp"].min(), df["Timestamp"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Resample Frequency
freq = st.sidebar.radio("Aggregation", ["Weekly", "Monthly"])
resample_rule = "W" if freq == "Weekly" else "M"

# Room selection
room_options = ["LivingRoom", "Kitchen", "Bedroom"]
selected_rooms = st.sidebar.multiselect("Select Room(s)", room_options, default=room_options)

# Filter by date range
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

# Resampling
df_filtered.set_index("Timestamp", inplace=True)
agg_funcs = {}

for room in selected_rooms:
    agg_funcs[f"Temperature_{room}"] = "mean"
    agg_funcs[f"Humidity_{room}"] = "mean"

agg_funcs["Energy_Consumption"] = "sum"

df_resampled = df_filtered.resample(resample_rule).agg(agg_funcs).reset_index()

# Main UI
st.title("🏠 Smart Home Energy Dashboard")

# KPI Cards
st.subheader("🔋 Energy Overview")
st.metric("Total Energy Consumption", f"{df_filtered['Energy_Consumption'].sum():,.2f} kWh")

# Temperature and Humidity Charts by Room
for room in selected_rooms:
    col1, col2 = st.columns(2)
    with col1:
        fig_temp = px.line(df_resampled, x="Timestamp", y=f"Temperature_{room}", title=f"🌡️ Avg Temperature - {room}")
        st.plotly_chart(fig_temp, use_container_width=True)
    with col2:
        fig_hum = px.line(df_resampled, x="Timestamp", y=f"Humidity_{room}", title=f"💧 Avg Humidity - {room}")
        st.plotly_chart(fig_hum, use_container_width=True)

# Energy Usage Over Time
st.subheader("📈 Energy Consumption Over Time")
fig_energy = px.line(df_resampled, x="Timestamp", y="Energy_Consumption", title="Total Energy Usage")
st.plotly_chart(fig_energy, use_container_width=True)
