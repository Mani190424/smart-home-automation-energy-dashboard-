
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

st.sidebar.header("🔎 Filters")

# Fixed date range 2004–2014
date_range = st.sidebar.date_input(
    "Select Date Range",
    [pd.to_datetime('2004-01-01'), pd.to_datetime('2014-12-31')],
    min_value=pd.to_datetime('2004-01-01'),
    max_value=pd.to_datetime('2014-12-31')
)

# Room selectors
energy_rooms = [col for col in df.columns if col.startswith("Energy_")]
temp_rooms = [col for col in df.columns if col.startswith("Temperature_")]
humidity_rooms = [col for col in df.columns if col.startswith("Humidity_")]

selected_energy = st.sidebar.multiselect("⚡ Energy Rooms", energy_rooms, default=energy_rooms)
selected_temp = st.sidebar.multiselect("🌡️ Temp Rooms", temp_rooms, default=temp_rooms)
selected_hum = st.sidebar.multiselect("💧 Humidity Rooms", humidity_rooms, default=humidity_rooms)

# Filter by date
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

# ----- KPIs -----
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
total_power = df_filtered[selected_energy].sum().sum()
avg_temp = df_filtered[selected_temp].mean().mean()
max_temp = df_filtered[selected_temp].max().max()
min_temp = df_filtered[selected_temp].min().min()

col1.metric("Total Power", f"{total_power:.2f} kWh")
col2.metric("Avg Temp", f"{avg_temp:.1f} °C")
col3.metric("Max Temp", f"{max_temp:.1f} °C")
col4.metric("Min Temp", f"{min_temp:.1f} °C")

# ----- Pie Chart 1: Temperature + Energy -----
st.markdown("### 🥧 Pie Chart: Temperature + Energy Consumption")
temp_energy_data = []
for col in selected_temp:
    room = col.replace("Temperature_", "")
    temp_avg = df_filtered[col].mean()
    energy_col = f"Energy_{room}"
    energy_sum = df_filtered[energy_col].sum() if energy_col in df_filtered.columns else 0
    combined = (temp_avg or 0) + (energy_sum or 0)
    temp_energy_data.append({"Room": room, "Combined Value": combined})

df_temp_pie = pd.DataFrame(temp_energy_data)
fig_temp_pie = px.pie(df_temp_pie, values="Combined Value", names="Room", title="Temperature + Energy", template="plotly_dark")
st.plotly_chart(fig_temp_pie, use_container_width=True)

# ----- Pie Chart 2: Humidity + Energy -----
st.markdown("### 🥧 Pie Chart: Humidity + Energy Consumption")
hum_energy_data = []
for col in selected_hum:
    room = col.replace("Humidity_", "")
    hum_avg = df_filtered[col].mean()
    energy_col = f"Energy_{room}"
    energy_sum = df_filtered[energy_col].sum() if energy_col in df_filtered.columns else 0
    combined = (hum_avg or 0) + (energy_sum or 0)
    hum_energy_data.append({"Room": room, "Combined Value": combined})

df_hum_pie = pd.DataFrame(hum_energy_data)
fig_hum_pie = px.pie(df_hum_pie, values="Combined Value", names="Room", title="Humidity + Energy", template="plotly_dark")
st.plotly_chart(fig_hum_pie, use_container_width=True)
