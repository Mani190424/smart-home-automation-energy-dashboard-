import streamlit as st

# === LOGIN PAGE ===
PASSWORD = "smart123"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <h2 style='text-align:center;'>🔐 Login Required</h2>
        <p style='text-align:center;'>Enter the password to access the Smart Home Dashboard.</p>
    """, unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Access Granted")
            st.rerun()
        else:
            st.error("❌ Incorrect Password")
    st.stop()

# === LOGIN PAGE ===
PASSWORD = "smart123"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <h2 style='text-align:center;'>🔐 Login Required</h2>
        <p style='text-align:center;'>Enter the password to access the Smart Home Dashboard.</p>
    """, unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Access Granted")
            st.rerun()
        else:
            st.error("❌ Incorrect Password")
    st.stop()
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# === LOGIN PAGE ===
PASSWORD = "smart123"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
        <h2 style='text-align:center;'>🔐 Login Required</h2>
        <p style='text-align:center;'>Enter the password to access the Smart Home Dashboard.</p>
    """, unsafe_allow_html=True)
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Access Granted")
            st.rerun()
        else:
            st.error("❌ Incorrect Password")
    st.stop()

# === PAGE CONFIG ===
st.set_page_config(
    page_title="Smart Home Energy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏠"
)

# === THEME STYLING ===
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

# === LOAD DATA ===
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df["AC_Timestamp"] = pd.to_datetime(df["AC_Timestamp"])
    df["Date"] = df["AC_Timestamp"].dt.date
    df["Time"] = df["AC_Timestamp"].dt.time
    return df

df = load_data()

# === REPORT DOWNLOAD ===
with st.expander("📩 Download Report"):
    if st.button("Download Daily Report (CSV)"):
        st.download_button(
            label="📥 Download Now",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="daily_report.csv",
            mime="text/csv"
        )

# === SIDEBAR ===
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1530/1530297.png", width=100)
    st.markdown("## 🏡 Smart Home Energy")
    page = st.radio("Navigate", ["🏠 Dashboard", "📈 Trends", "⚙️ Settings"])

# === ROOM TABS ===
st.markdown("<h1 style='text-align: center;'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
room_tab = st.tabs(["🛋️ Living Room", "🍳 Kitchen", "🛏 Bedroom"])

room_keys = ["LivingRoom", "Kitchen", "Bedroom"]
room_icons = ["🛋️", "🍳", "🛏"]

for tab, room, icon in zip(room_tab, room_keys, room_icons):
    with tab:
        temp_col = f"Temperature_{room}"
        humid_col = f"Humidity_{room}"
        temp_val = df[temp_col].mean()
        humid_val = df[humid_col].mean()
        energy_val = df['Energy_Consumption'].sum()

        col1, col2, col3 = st.columns(3)

        with col1:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = temp_val,
                title = {'text': f"{icon} {room} Temp (°C)"},
                gauge = {
                    'axis': {'range': [0, 50]},
                    'bar': {'color': '#d627ff' if temp_val < 30 else '#ff4444'}
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = humid_val,
                title = {'text': f"💧 {room} Humidity (%)"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': '#1ecbe1'}}
            ))
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = energy_val,
                title = {'text': f"⚡ Total Energy (kWh)"},
                gauge = {'axis': {'range': [0, energy_val * 1.2]}, 'bar': {'color': '#fcca1b'}}
            ))
            st.plotly_chart(fig, use_container_width=True)

# === OTHER PAGES ===
if page == "📈 Trends":
    st.header("📈 Trend Analysis")
    st.info("Placeholder for trend over time (line/bar charts).")

elif page == "⚙️ Settings":
    st.header("⚙️ Settings")
    st.info("Placeholder for theme toggles, export options, etc.")
