import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page settings ---
st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# --- Custom CSS for dark theme + stylish cards ---
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
        }
        .main {
            color: #FFFFFF;
            background-color: #0e1117;
        }
        .stApp {
            background-color: #0e1117;
        }
        .kpi-card {
            padding: 20px;
            border-radius: 15px;
            background-color: #1e1e2f;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
            text-align: center;
        }
        .kpi-card h3 {
            color: #6c76ff;
            font-size: 20px;
        }
        .kpi-card p {
            font-size: 28px;
            font-weight: bold;
            color: #ffffff;
        }
        hr {
            border: 1px solid #444;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1 style='color: #6c76ff;'>🏠 Smart Home Energy Dashboard</h1>", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

min_date = df["Timestamp"].min()
max_date = df["Timestamp"].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# ✅ Identify numeric room columns only (for energy usage)
valid_room_columns = [
    col for col in df.columns 
    if col != "Timestamp" and pd.api.types.is_numeric_dtype(df[col])
]

if not valid_room_columns:
    st.error("❌ No valid numeric energy usage columns found.")
    st.stop()

selected_rooms = st.sidebar.multiselect(
    "Select Room(s)",
    options=valid_room_columns,
    default=valid_room_columns
)

# --- Filter Logic ---
if isinstance(selected_dates, list) and len(selected_dates) == 2:
    start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
else:
    start_date, end_date = min_date, max_date

filtered_df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

# ✅ Prevent error if user deselects all rooms
if not selected_rooms:
    st.warning("⚠️ Please select at least one room to display data.")
    st.stop()

# --- Melted Data for Visualization ---
melted_df = filtered_df.melt(
    id_vars=["Timestamp"],
    value_vars=selected_rooms,
    var_name="Room",
    value_name="Energy_Consumption"
)

# --- KPI Cards ---
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_power = melted_df["Energy_Consumption"].sum()
avg_temp = 24.5  # Optional: link to actual values later
max_temp = 28.1
min_temp = 20.3

with col1:
    st.markdown(f"<div class='kpi-card'><h3>Total Power</h3><p>{total_power:.2f} kWh</p></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='kpi-card'><h3>Avg Temp</h3><p>{avg_temp:.2f} °C</p></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='kpi-card'><h3>Max Temp</h3><p>{max_temp:.2f} °C</p></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='kpi-card'><h3>Min Temp</h3><p>{min_temp:.2f} °C</p></div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# --- Line Chart ---
st.markdown("### 📈 Power Usage Over Time")
fig_line = px.line(
    melted_df, x="Timestamp", y="Energy_Consumption", color="Room",
    labels={"Energy_Consumption": "Power (kWh)"},
    template="plotly_dark"
)
st.plotly_chart(fig_line, use_container_width=True)

# --- Bar Chart ---
st.markdown("### 📊 Monthly Power Usage by Room")
bar_df = melted_df.copy()
bar_df["Month"] = bar_df["Timestamp"].dt.to_period("M").astype(str)
bar_chart = bar_df.groupby(["Room", "Month"])["Energy_Consumption"].sum().reset_index()

fig_bar = px.bar(
    bar_chart, x="Month", y="Energy_Consumption", color="Room",
    barmode="group", template="plotly_dark",
    labels={"Energy_Consumption": "Total Power (kWh)"}
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Pie Chart ---
st.markdown("### 🥧 Power % by Room")
pie_df = melted_df.groupby("Room")["Energy_Consumption"].sum().reset_index()

fig_pie = px.pie(
    pie_df, values="Energy_Consumption", names="Room", 
    title="Power Usage Share", template="plotly_dark"
)
st.plotly_chart(fig_pie, use_container_width=True)

# --- Footer ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<center style='color:#999;'>Built with ❤️ using Streamlit</center>", unsafe_allow_html=True)
