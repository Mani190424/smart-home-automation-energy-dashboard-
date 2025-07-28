# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO

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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_time" not in st.session_state:
    st.session_state.login_time = None

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ---------------- DASHBOARD ----------------
st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")
st.title("🏠 Smart Home Automation - Energy Dashboard")

with st.sidebar:
    st.markdown(f"🟢 Logged in as **admin**")
    st.markdown(f"🕒 Login Time: {st.session_state.login_time}")
    if st.button("🔓 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

@st.cache_data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df["Date"] = pd.to_datetime(df["AC_Timestamp"])
    df["Day"] = df["Date"].dt.date
    df["Week"] = df["Date"].dt.isocalendar().week
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    return df

df = load_data()

# ---------------- SIDEBAR CONTROLS ----------------
st.sidebar.header("🔎 Filter Options")

room_icons = {
    "Living Room": "🛋️",
    "Kitchen": "🍳",
    "Bedroom": "🛏️",
    "Bathroom": "🛁"
}
selected_room = st.sidebar.selectbox("Select Room", options=list(room_icons.keys()), format_func=lambda x: f"{room_icons[x]} {x}")

view_by = st.sidebar.selectbox("View By", ["Daily", "Weekly", "Monthly", "Yearly"])

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Filter based on date range
df_filtered = df[(df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date)]

# ---------------- KPI METRICS ----------------
st.markdown(f"## 📊 {room_icons[selected_room]} {selected_room} Overview")

energy_used = df_filtered["Energy_Consumption"].sum()

temp_cols = [col for col in df.columns if "Temperature" in col and selected_room.lower() in col.lower()]
humid_cols = [col for col in df.columns if "Humidity" in col and selected_room.lower() in col.lower()]

avg_temp = df_filtered[temp_cols].mean().values[0] if temp_cols else 0
avg_humidity = df_filtered[humid_cols].mean().values[0] if humid_cols else 0

col1, col2, col3 = st.columns(3)
col1.metric("🔋 Total Energy", f"{energy_used:.2f} kWh")
col2.metric("🌡️ Avg Temp", f"{avg_temp:.2f} °C")
col3.metric("💧 Avg Humidity", f"{avg_humidity:.2f} %")

st.divider()

# ---------------- GROUPING DATA ----------------
group_key = {
    "Daily": df_filtered["Date"].dt.date,
    "Weekly": df_filtered["Date"].dt.isocalendar().week,
    "Monthly": df_filtered["Date"].dt.to_period("M").astype(str),
    "Yearly": df_filtered["Date"].dt.year
}[view_by]

grouped_df = df_filtered.groupby(group_key)["Energy_Consumption"].sum().reset_index()
grouped_df.columns = [view_by, "Total Energy"]

# ---------------- LINE CHART ----------------
st.subheader("📈 Energy Usage Over Time")
fig_line = px.line(grouped_df, x=view_by, y="Total Energy", markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# ---------------- BAR CHART ----------------
st.subheader("📊 Avg Temperature by Room")
avg_temp_rooms = {
    "Living Room": df_filtered["Temperature_LivingRoom"].mean(),
    "Kitchen": df_filtered["Temperature_Kitchen"].mean(),
    "Bedroom": df_filtered["Temperature_Bedroom"].mean(),
}
bar_df = pd.DataFrame(list(avg_temp_rooms.items()), columns=["Room", "Avg Temp"])
bar_fig = px.bar(bar_df, x="Room", y="Avg Temp", color="Room")
st.plotly_chart(bar_fig, use_container_width=True)

# ---------------- PIE CHART ----------------
st.subheader("🥧 Energy % by Room (simulated)")
pie_df = pd.DataFrame({
    "Room": ["Living Room", "Kitchen", "Bedroom"],
    "Energy": [
        df_filtered["Temperature_LivingRoom"].mean() * 1.2,
        df_filtered["Temperature_Kitchen"].mean() * 1.3,
        df_filtered["Temperature_Bedroom"].mean() * 1.1,
    ]
})
pie_fig = px.pie(pie_df, names="Room", values="Energy", title="Simulated Room-wise Energy Usage")
st.plotly_chart(pie_fig)

# ---------------- DOWNLOAD SECTION ----------------
st.subheader("💾 Download Filtered Data")

def to_excel(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

st.download_button("📥 Download Excel", data=to_excel(df_filtered), file_name="filtered_data.xlsx")
st.download_button("📥 Download CSV", data=df_filtered.to_csv(index=False).encode('utf-8'), file_name="filtered_data.csv")

# ---------------- RAW DATA ----------------
with st.expander("📄 Show Raw Data"):
    st.dataframe(df_filtered)
