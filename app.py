
import streamlit as st
import pandas as pd
import plotly.express as px

# ----- App Config -----
st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")

# ----- Load Data -----
@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

# ----- Sidebar -----
st.sidebar.header("🔎 Filters")

# Fixed date range (2004–2014)
date_range = st.sidebar.date_input(
    "Select Date Range",
    [pd.to_datetime('2004-01-01'), pd.to_datetime('2014-12-31')],
    min_value=pd.to_datetime('2004-01-01'),
    max_value=pd.to_datetime('2014-12-31')
)

# Room selectors (for energy)
energy_rooms = [col for col in df.columns if col.startswith("Energy_")]
selected_energy_rooms = st.sidebar.multiselect("⚡ Select Energy Rooms", energy_rooms, default=energy_rooms)

# Room selectors (for temperature)
temp_rooms = [col for col in df.columns if col.startswith("Temperature_")]
selected_temp_rooms = st.sidebar.multiselect("🌡️ Select Temperature Rooms", temp_rooms, default=temp_rooms)

# Room selectors (for humidity)
humidity_rooms = [col for col in df.columns if col.startswith("Humidity_")]
selected_humidity_rooms = st.sidebar.multiselect("💧 Select Humidity Rooms", humidity_rooms, default=humidity_rooms)

# Aggregation toggle
agg_choice = st.sidebar.radio("🕓 Aggregate Data By", ["Hourly", "Daily", "Monthly"])

# ----- Filter Data -----
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

# ----- KPI Metrics -----
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_power = filtered_df[selected_energy_rooms].sum().sum()
avg_temp = filtered_df[selected_temp_rooms].mean().mean()
max_temp = filtered_df[selected_temp_rooms].max().max()
min_temp = filtered_df[selected_temp_rooms].min().min()

col1.metric("Total Power", f"{total_power:.2f} kWh")
col2.metric("Avg Temperature", f"{avg_temp:.1f} °C")
col3.metric("Max Temp", f"{max_temp:.1f} °C")
col4.metric("Min Temp", f"{min_temp:.1f} °C")

# ----- Energy Line Chart -----
st.markdown("### 📈 Power Usage Over Time")
melted_energy = filtered_df[["Timestamp"] + selected_energy_rooms].melt(id_vars="Timestamp", var_name="Room", value_name="Power")
melted_energy["Room"] = melted_energy["Room"].str.replace("Energy_", "")

if agg_choice == "Hourly":
    melted_energy["Period"] = melted_energy["Timestamp"].dt.strftime("%Y-%m-%d %H:00")
elif agg_choice == "Daily":
    melted_energy["Period"] = melted_energy["Timestamp"].dt.date
else:
    melted_energy["Period"] = melted_energy["Timestamp"].dt.to_period("M").astype(str)

grouped_energy = melted_energy.groupby(["Period", "Room"])["Power"].sum().reset_index()
fig_line = px.line(grouped_energy, x="Period", y="Power", color="Room", markers=True, labels={"Power": "Energy (kWh)"}, template="plotly_dark")
st.plotly_chart(fig_line, use_container_width=True)

# ----- Bar Chart -----
st.markdown("### 📊 Power Usage by Room")
room_grouped = melted_energy.groupby("Room")["Power"].sum().reset_index()
fig_bar = px.bar(room_grouped, x="Room", y="Power", color="Room", template="plotly_dark", labels={"Power": "Total Power"})
st.plotly_chart(fig_bar, use_container_width=True)
