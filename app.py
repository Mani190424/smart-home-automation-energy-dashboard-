import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Smart Home Energy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏠"
)

# Neon Purple Theme Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #1c0c36, #2d1457);
        color: white;
    }
    .css-1d391kg, .css-1v3fvcr, .block-container {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px;
        padding: 20px;
        color: white !important;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Load Data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df["AC_Timestamp"] = pd.to_datetime(df["AC_Timestamp"])
    df["Date"] = df["AC_Timestamp"].dt.date
    df["Time"] = df["AC_Timestamp"].dt.time
    return df

df = load_data()

# Sidebar Navigation
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1530/1530297.png", width=100)
    st.markdown("## 🏡 Smart Home Energy")
    page = st.radio("Navigate", ["🏠 Dashboard", "🛏️ Rooms", "📈 Trends", "⚙️ Settings"])

# Page Routing
if page == "🏠 Dashboard":
    st.markdown("<h1 style='text-align: center;'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        temp_val = df["Temperature_LivingRoom"].mean()
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = temp_val,
            title = {'text': f"Avg Temp (°C)"},
            gauge = {
                'axis': {'range': [0, 50]},
                'bar': {'color': '#d627ff' if temp_val < 30 else '#ff4444'}
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = df["Humidity_LivingRoom"].mean(),
            title = {'text': f"Avg Humidity (%)"},
            gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': '#1ecbe1'}}
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = df['Energy_Consumption'].sum(),
            title = {'text': f"Total Energy (kWh)"},
            gauge = {'axis': {'range': [0, df['Energy_Consumption'].sum()*1.2]}, 'bar': {'color': '#fcca1b'}}
        ))
        st.plotly_chart(fig, use_container_width=True)

elif page == "🛏️ Rooms":
    st.header("🛏️ Room-wise Visualization")
    st.info("Placeholder for room-wise comparison charts and stats.")

elif page == "📈 Trends":
    st.header("📈 Trend Analysis")
    st.info("Placeholder for trend over time (line/bar charts).")

elif page == "⚙️ Settings":
    st.header("⚙️ Settings")
    st.info("Placeholder for theme toggles, export options, etc.")
