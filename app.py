
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page config ---
st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# --- Theme Toggle ---
theme = st.sidebar.radio("🌗 Select Theme", ["Dark", "Light"], index=0)
dark_mode = theme == "Dark"

# --- Custom CSS ---
if dark_mode:
    st.markdown("""
        <style>
            body, .stApp {
                background-color: #0e1117;
                color: #FFFFFF;
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
                font-size: 26px;
                font-weight: bold;
                color: #ffffff;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            .kpi-card {
                padding: 20px;
                border-radius: 15px;
                background-color: #f0f2f6;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
                text-align: center;
            }
            .kpi-card h3 {
                color: #2a2a2a;
                font-size: 20px;
            }
            .kpi-card p {
                font-size: 26px;
                font-weight: bold;
                color: #000000;
            }
        </style>
    """, unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

# --- Multi-page Navigation ---
page = st.sidebar.selectbox("🔀 Navigate", ["🏠 Home", "📊 Room-wise", "📈 Trends", "⚙️ Settings"])

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")
min_date = df["Timestamp"].min()
max_date = df["Timestamp"].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])
room_list = df["Room"].unique().tolist()
selected_rooms = st.sidebar.multiselect("Select Room(s)", room_list, default=room_list)

# --- Filtered Data ---
start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
filtered_df = df[
    (df["Timestamp"] >= start_date) &
    (df["Timestamp"] <= end_date) &
    (df["Room"].isin(selected_rooms))
]

# --- Export Button ---
st.sidebar.download_button("📥 Download Filtered CSV", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv")

# --- Home Page ---
if page == "🏠 Home":
    st.title("🏠 Smart Home Energy Dashboard")

    col1, col2, col3 = st.columns(3)
    total_energy = filtered_df[filtered_df["Metric"] == "Energy_Consumption"]["Value"].sum()
    avg_temp = filtered_df[filtered_df["Metric"] == "Temperature"]["Value"].mean()
    avg_hum = filtered_df[filtered_df["Metric"] == "Humidity"]["Value"].mean()

    with col1:
        st.markdown(f"<div class='kpi-card'><h3>Total Power</h3><p>{total_energy:.2f} kWh</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='kpi-card'><h3>Avg Temp</h3><p>{avg_temp:.2f} °C</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='kpi-card'><h3>Avg Humidity</h3><p>{avg_hum:.2f} %</p></div>", unsafe_allow_html=True)

# --- Room-wise Page ---
elif page == "📊 Room-wise":
    st.title("📊 Room-wise Temperature & Humidity")
    for room in selected_rooms:
        room_df = filtered_df[filtered_df["Room"] == room]
        temp = room_df[room_df["Metric"] == "Temperature"]["Value"].mean()
        hum = room_df[room_df["Metric"] == "Humidity"]["Value"].mean()

        st.markdown(f"<div class='kpi-card'><h3>{room}</h3><p>Temp: {temp:.1f} °C | Humidity: {hum:.1f} %</p></div><br>", unsafe_allow_html=True)

# --- Trends Page ---
elif page == "📈 Trends":
    st.title("📈 Trends Over Time")
    metric_options = filtered_df["Metric"].unique().tolist()
    metric_selected = st.selectbox("Choose Metric", metric_options, index=0)
    trend_df = filtered_df[filtered_df["Metric"] == metric_selected]
    fig = px.line(trend_df, x="Timestamp", y="Value", color="Room", template="plotly_dark" if dark_mode else "plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# --- Settings Page ---
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.info("This page can later include notification thresholds, profile, API keys, etc.")

# --- Alerts ---
alert_df = filtered_df[filtered_df["Metric"] == "Temperature"]
if not alert_df.empty and alert_df["Value"].max() > 30:
    st.sidebar.warning("🔥 High temperature alert!")

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<center>Built with ❤️ by Makka using Streamlit</center>", unsafe_allow_html=True)
