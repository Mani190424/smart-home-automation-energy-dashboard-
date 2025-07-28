# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

# ---------------- LOGIN PAGE ----------------
def check_login(username, password):
    return username == "admin" and password == "smart123"

def login_screen():
    st.markdown("## 🔐 Login to Smart Home Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("✅ Login successful")
        else:
            st.error("❌ Invalid credentials")

# --- Session State Setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_time" not in st.session_state:
    st.session_state.login_time = None

# --- Logout Sidebar ---
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(f"🟢 Logged in as **admin**")
        st.markdown(f"🕒 Login Time: {st.session_state.login_time}")
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ---------------- DASHBOARD ----------------
st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")
st.title("🏠 Smart Home Automation - Energy Dashboard")

# Load Data
@st.cache_data
def load_data():
   df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    if "Date" not in df.columns:
        df["Date"] = pd.date_range(start="2024-01-01", periods=len(df), freq="6H")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔎 Filter Data")
year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique()))
month = st.sidebar.selectbox("Select Month", sorted(df["Month"].unique()))
day = st.sidebar.selectbox("Select Day", sorted(df["Day"].unique()))

filtered_df = df[(df["Year"] == year) & (df["Month"] == month) & (df["Day"] == day)]

# ---------------- KPI CARDS ----------------
st.markdown("## 📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

total_power = filtered_df["Energy_Consumption"].sum()
avg_temp = filtered_df[["Temperature_LivingRoom", "Temperature_Kitchen", "Temperature_Bedroom"]].mean().mean()
max_temp = filtered_df[["Temperature_LivingRoom", "Temperature_Kitchen", "Temperature_Bedroom"]].max().max()
min_temp = filtered_df[["Temperature_LivingRoom", "Temperature_Kitchen", "Temperature_Bedroom"]].min().min()

col1.metric("🔋 Total Power", f"{total_power:.2f} kWh")
col2.metric("🌡️ Avg Temp", f"{avg_temp:.2f} °C")
col3.metric("🔥 Max Temp", f"{max_temp:.2f} °C")
col4.metric("❄️ Min Temp", f"{min_temp:.2f} °C")

st.divider()

# ---------------- LINE CHART ----------------
st.subheader("📈 Power Usage Over Time")
st.line_chart(filtered_df[["Date", "Energy_Consumption"]].set_index("Date"))

# ---------------- BAR CHART ----------------
st.subheader("📊 Power Usage by Room (Simulated)")
room_data = {
    "Room": ["Living Room", "Kitchen", "Bedroom"],
    "Power": [
        filtered_df["Temperature_LivingRoom"].mean() * 1.5,
        filtered_df["Temperature_Kitchen"].mean() * 1.5,
        filtered_df["Temperature_Bedroom"].mean() * 1.5,
    ]
}
room_df = pd.DataFrame(room_data)
bar_fig = px.bar(room_df, x="Room", y="Power", color="Room", title="Power Usage by Room")
st.plotly_chart(bar_fig)

# ---------------- PIE CHART ----------------
st.subheader("🥧 Power Percentage by Room")
pie_fig = px.pie(room_df, names="Room", values="Power", title="Room-wise Power Distribution")
st.plotly_chart(pie_fig)

# ---------------- DOWNLOAD SECTION ----------------
st.subheader("💾 Download Filtered Data")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered Data')
        writer.save()
    processed_data = output.getvalue()
    return processed_data

excel_data = to_excel(filtered_df)
st.download_button("📥 Download as Excel", data=excel_data, file_name='filtered_data.xlsx')

csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download as CSV", data=csv_data, file_name='filtered_data.csv')

# ---------------- RAW DATA ----------------
with st.expander("📄 Show Raw Data"):
    st.dataframe(filtered_df)
