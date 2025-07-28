import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# --------------------- LOGIN SYSTEM ---------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.login_time = None

def login():
    st.title("🔐 Smart Home Energy Dashboard Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.session_state.login_time = datetime.now()
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Incorrect username or password")

def logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully!")
        st.rerun()

# --------------------- MAIN DASHBOARD ---------------------------
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    if "Date" not in df.columns:
        df["Date"] = pd.date_range(start="2024-01-01", periods=len(df), freq="6H")
    df["Date"] = pd.to_datetime(df["AC_Timestamp"], errors='coerce')
    df.dropna(subset=["Date"], inplace=True)
    return df

def main():
    st.set_page_config(page_title="Smart Home Dashboard", layout="wide")
    st.sidebar.title("🗂️ Filter Options")

    logout()  # Logout button in sidebar

    df = load_data()

    # 🧠 Convert Timestamp column if not already
df["Date"] = pd.to_datetime(df["AC_Timestamp"])
df["Day"] = df["Date"].dt.date
df["Week"] = df["Date"].dt.isocalendar().week
df["Month"] = df["Date"].dt.month
df["Year"] = df["Date"].dt.year

# 📅 Sidebar Filter Section
st.sidebar.header("📅 Select Time Period")

time_filter = st.sidebar.selectbox("View By", ["Daily", "Weekly", "Monthly", "Yearly"])
room = st.sidebar.radio("Select Room", list(room_keywords.keys()), index=0)

# 🧠 Create Filtered Data based on time
if time_filter == "Daily":
    grouped_df = df.groupby("Day").agg({
        "Energy_Consumption": "sum"
    }).reset_index()
    grouped_df.rename(columns={"Day": "Time"}, inplace=True)

elif time_filter == "Weekly":
    grouped_df = df.groupby("Week").agg({
        "Energy_Consumption": "sum"
    }).reset_index()
    grouped_df.rename(columns={"Week": "Time"}, inplace=True)

elif time_filter == "Monthly":
    grouped_df = df.groupby("Month").agg({
        "Energy_Consumption": "sum"
    }).reset_index()
    grouped_df.rename(columns={"Month": "Time"}, inplace=True)

elif time_filter == "Yearly":
    grouped_df = df.groupby("Year").agg({
        "Energy_Consumption": "sum"
    }).reset_index()
    grouped_df.rename(columns={"Year": "Time"}, inplace=True)

# 🎯 Filter original data (df_filtered) for charts and KPIs
start_date, end_date = st.sidebar.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()])
df_filtered = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]


df_filtered = df[(df["Date"].dt.date >= from_date) & (df["Date"].dt.date <= to_date)]

rooms = {
        "Bathroom": "🛁",
        "Bedroom": "🛏️",
        "Hall": "🛋️",
        "Kitchen": "🍽️",
        "Living Room": "🖥️"
    }

selected_room = st.selectbox("🏠 Select Room", list(rooms.keys()), index=0, format_func=lambda x: f"{rooms[x]} {x}")

st.markdown(f"## {rooms[selected_room]} {selected_room}")

    # ----------- KPI Cards -------------
    col1, col2, col3 = st.columns(3)

    with col1:
        total_energy = df_filtered["Energy_Consumption"].sum()
        st.metric("⚡ Total Energy", f"{total_energy:.1f} kWh")

    with col2:
        room_keywords = {
            "Bathroom": "Bathroom",
            "Bedroom": "Bedroom",
            "Hall": "Hall",
            "Kitchen": "Kitchen",
            "Living Room": "LivingRoom"
        }
    keyword = room_keywords[selected_room]
    temp_cols = [col for col in df_filtered.columns if "Temperature" in col and keyword in col]
    avg_temp = df_filtered[temp_cols].mean().values[0] if temp_cols else 0
    st.metric("🌡️ Avg Temp", f"{avg_temp:.1f} °C")

    with col3:
        hum_cols = [col for col in df_filtered.columns if "Humidity" in col and keyword in col]
        avg_hum = df_filtered[hum_cols].mean().values[0] if hum_cols else 0
        st.metric("💧 Avg Humidity", f"{avg_hum:.1f} %")

    # ----------- Charts Section -------------
    chart_type = st.selectbox("📊 Select Chart Type", ["Line Chart", "Bar Chart", "Pie Chart"])

    if chart_type == "Line Chart":
        st.line_chart(df_filtered[["Date", "Energy_Consumption"]].set_index("Date"))

    elif chart_type == "Bar Chart":
        room_cols = [col for col in df_filtered.columns if "Energy_Consumption" in col or "Room" in col]
        df_bar = df_filtered.groupby(df_filtered["Date"].dt.date)["Energy_Consumption"].sum()
        st.bar_chart(df_bar)

    elif chart_type == "Pie Chart":
        room_cols = [col for col in df_filtered.columns if "Energy_Consumption" in col]
        df_pie = df_filtered.groupby(selected_room)["Energy_Consumption"].sum()
        st.write("💡 Pie chart placeholder (custom room-wise % coming soon...)")

    # ----------- Download Buttons -------------
    buffer = BytesIO()
    df_filtered.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)

    st.sidebar.download_button("📥 Download Excel", data=buffer, file_name="filtered_data.xlsx", mime="application/vnd.ms-excel")
    st.sidebar.download_button("📥 Download CSV", data=df_filtered.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")

    # ----------- Footer ----------
    st.markdown("---")
    st.caption(f"🕒 Logged in at: {st.session_state.login_time.strftime('%Y-%m-%d %H:%M:%S')}")

# ---------------- MAIN CALL ----------------------
if not st.session_state.logged_in:
    login()
else:
    main()
