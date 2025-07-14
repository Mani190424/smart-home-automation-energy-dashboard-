import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# --- Custom CSS for styling ---
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
        }
        .main {
            color: #FFFFFF;
            background-color: #0e1117;
        }
        .kpi-card {
            padding: 20px;
            border-radius: 15px;
            background-color: #1e1e2f;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
            text-align: center;
            margin-bottom: 10px;
        }
        .kpi-card h3 {
            color: #6c76ff;
            font-size: 18px;
        }
        .kpi-card p {
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
        }
    </style>
""", unsafe_allow_html=True)

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
rooms = df["Room"].unique().tolist()
selected_rooms = st.sidebar.multiselect("Select Room(s)", rooms, default=rooms)

# --- Filtered Data ---
if isinstance(selected_dates, list) and len(selected_dates) == 2:
    start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
else:
    start_date, end_date = min_date, max_date

filtered_df = df[
    (df["Timestamp"] >= start_date) & 
    (df["Timestamp"] <= end_date) & 
    (df["Room"].isin(selected_rooms))
]

st.title("🏠 Smart Home Energy Dashboard")

# --- Room-wise KPI Cards ---
st.markdown("## 🧩 Room-wise Metrics")
for room in selected_rooms:
    room_df = filtered_df[filtered_df["Room"] == room]
    power = room_df[room_df["Metric"] == "Energy_Consumption"]["Value"].sum()
    temp = room_df[room_df["Metric"] == "Temperature"]["Value"].mean()
    hum = room_df[room_df["Metric"] == "Humidity"]["Value"].mean()

    col = st.columns(1)[0]
    with col:
        st.markdown(f"""
        <div class='kpi-card'>
            <h3>{room}</h3>
            <p>🌡️ Temp: {temp:.1f} °C</p>
            <p>💧 Humidity: {hum:.1f} %</p>
            <p>⚡ Power: {power:.2f} kWh</p>
        </div>
        """, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("<center style='color:#999;'>Built with ❤️ using Streamlit</center>", unsafe_allow_html=True)
