
import streamlit as st
import pandas as pd
import plotly.express as px

# ----- App Config -----
st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")

# ----- Custom Style -----
st.markdown("""
    <style>
        body, .main, .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        .metric {
            text-align: center !important;
        }
        .sidebar .sidebar-content {
            background-color: #161a2b;
        }
    </style>
""", unsafe_allow_html=True)

# ----- Load Data -----
@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

# ----- Sidebar -----
st.sidebar.header("🎛️ Filters")
date_range = st.sidebar.date_input("Select Date Range", [df["Timestamp"].min(), df["Timestamp"].max()])

room_cols = [col for col in df.columns if col.startswith("Energy_")]
selected_rooms = st.sidebar.multiselect("Select Rooms", room_cols, default=room_cols)

agg_choice = st.sidebar.radio("Aggregate Data By", ["Hourly", "Daily", "Monthly"])

# ----- Filter Data -----
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)][["Timestamp"] + selected_rooms]

# ----- Melt for Charting -----
if not selected_rooms:
    st.warning("Please select at least one room.")
    st.stop()

melted = filtered_df.melt(id_vars="Timestamp", var_name="Room", value_name="Power")
melted["Room"] = melted["Room"].str.replace("Energy_", "")

# ----- KPIs -----
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
total_power = melted["Power"].sum()
avg_temp = df[[col for col in df.columns if "Temperature" in col]].mean().mean()
max_temp = df[[col for col in df.columns if "Temperature" in col]].max().max()
min_temp = df[[col for col in df.columns if "Temperature" in col]].min().min()

col1.metric("Total Power", f"{total_power:.2f} kWh")
col2.metric("Avg Temperature", f"{avg_temp:.1f} °C")
col3.metric("Max Temp", f"{max_temp:.1f} °C")
col4.metric("Min Temp", f"{min_temp:.1f} °C")

# ----- Line Chart -----
st.markdown("### 📈 Power Usage Over Time")
if agg_choice == "Hourly":
    melted["Period"] = melted["Timestamp"].dt.strftime("%Y-%m-%d %H:00")
elif agg_choice == "Daily":
    melted["Period"] = melted["Timestamp"].dt.date
else:
    melted["Period"] = melted["Timestamp"].dt.to_period("M").astype(str)

grouped = melted.groupby(["Period", "Room"])["Power"].sum().reset_index()
fig_line = px.line(grouped, x="Period", y="Power", color="Room", markers=True, labels={"Power": "Energy (kWh)"}, template="plotly_dark")
st.plotly_chart(fig_line, use_container_width=True)

# ----- Bar Chart -----
st.markdown("### 📊 Power Usage by Room")
room_grouped = melted.groupby("Room")["Power"].sum().reset_index()
fig_bar = px.bar(room_grouped, x="Room", y="Power", color="Room", template="plotly_dark", labels={"Power": "Total Power"})
st.plotly_chart(fig_bar, use_container_width=True)
