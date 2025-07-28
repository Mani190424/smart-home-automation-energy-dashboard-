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

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    from_date = st.sidebar.date_input("From", min_value=min_date, max_value=max_date, value=min_date)
    to_date = st.sidebar.date_input("To", min_value=min_date, max_value=max_date, value=max_date)

    if from_date > to_date:
        st.warning("⚠️ From date is greater than To date.")
        return

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
        avg_temp = df_filtered[[col for col in df_filtered.columns if "Temperature" in col and selected_room.lower() in col.lower()]].mean().values[0]
        st.metric("🌡️ Avg Temp", f"{avg_temp:.1f} °C")

    with col3:
        avg_hum = df_filtered[[col for col in df_filtered.columns if "Humidity" in col and selected_room.lower() in col.lower()]].mean().values[0]
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
