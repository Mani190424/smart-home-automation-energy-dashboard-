
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

# Determine valid date range from data
min_date = df["Timestamp"].min()
max_date = df["Timestamp"].max()

# Sidebar Filters
st.sidebar.header("🔎 Filters")
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

energy_cols = [col for col in df.columns if col.startswith("Energy_")]
temp_cols = [col for col in df.columns if col.startswith("Temperature_")]
humidity_cols = [col for col in df.columns if col.startswith("Humidity_")]

energy_rooms = st.sidebar.multiselect("⚡ Energy Rooms", energy_cols, default=energy_cols)
temp_rooms = st.sidebar.multiselect("🌡️ Temp Rooms", temp_cols, default=temp_cols)
humidity_rooms = st.sidebar.multiselect("💧 Humidity Rooms", humidity_cols, default=humidity_cols)

# Filter based on selected date range
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

# Check if data exists
if filtered_df.empty:
    st.warning("No data available for the selected date range.")
    st.stop()

# Display KPIs
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_power = filtered_df[energy_rooms].sum().sum() if energy_rooms else 0
avg_temp = filtered_df[temp_rooms].mean().mean() if temp_rooms else float("nan")
max_temp = filtered_df[temp_rooms].max().max() if temp_rooms else float("nan")
min_temp = filtered_df[temp_rooms].min().min() if temp_rooms else float("nan")

col1.metric("Total Power", f"{total_power:.2f} kWh")
col2.metric("Avg Temp", f"{avg_temp:.2f} °C")
col3.metric("Max Temp", f"{max_temp:.2f} °C")
col4.metric("Min Temp", f"{min_temp:.2f} °C")

# Pie Chart for Temp + Energy
st.subheader("🥧 Pie Chart: Temperature + Energy Consumption")
if temp_rooms and energy_rooms:
    temp_energy = pd.DataFrame({
        "Room": [col.replace("Temperature_", "") for col in temp_rooms],
        "TempAvg": filtered_df[temp_rooms].mean().values,
        "Energy": filtered_df[energy_rooms].sum().values
    })
    pie1 = px.pie(temp_energy, names="Room", values="Energy", title="Temperature + Energy", template="plotly_dark")
    st.plotly_chart(pie1, use_container_width=True)

# Pie Chart for Humidity + Energy
st.subheader("🥧 Pie Chart: Humidity + Energy Consumption")
if humidity_rooms and energy_rooms:
    humidity_energy = pd.DataFrame({
        "Room": [col.replace("Humidity_", "") for col in humidity_rooms],
        "HumidityAvg": filtered_df[humidity_rooms].mean().values,
        "Energy": filtered_df[energy_rooms].sum().values
    })
    pie2 = px.pie(humidity_energy, names="Room", values="Energy", title="Humidity + Energy", template="plotly_dark")
    st.plotly_chart(pie2, use_container_width=True)
