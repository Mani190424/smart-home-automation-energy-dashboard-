import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# ----- CONFIG -----
st.set_page_config(page_title="Smart Home Dashboard", layout="wide")
VALID_USERS = ["data.analyst190124@gmail.com"]

# ----- LOAD DATA -----
@st.cache_data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df['AC_Timestamp'] = pd.to_datetime(df['AC_Timestamp'])
    return df

# ----- LOGIN -----
def login():
    st.title("🔐 Smart Home Login")
    email = st.text_input("Enter your email to login")
    if st.button("Login"):
        if email in VALID_USERS:
            st.session_state["authenticated"] = True
            st.session_state["email"] = email
            st.session_state["login_time"] = datetime.now()
            st.experimental_rerun()
        else:
            st.error("Unauthorized user!")

# ----- MAIN DASHBOARD -----
def main():
    df = load_data()

    # Sidebar Filters
    st.sidebar.title("🏠 Filter Options")
    selected_room = st.sidebar.selectbox("Select Room", ["LivingRoom", "Bedroom", "Kitchen"])
    date_range = st.sidebar.date_input("Select Date Range", [df["AC_Timestamp"].min().date(), df["AC_Timestamp"].max().date()])
    time_group = st.sidebar.radio("Group by Time", ["Daily", "Weekly", "Monthly", "Yearly"])

    # Filter data
    df_filtered = df[
        (df["AC_Timestamp"].dt.date >= date_range[0]) &
        (df["AC_Timestamp"].dt.date <= date_range[1])
    ]

    # Room-specific columns
    temp_col = f"Temperature_{selected_room}"
    hum_col = f"Humidity_{selected_room}"
    energy_col = "Energy_Consumption"

    st.title(f"📊 Smart Home Dashboard - {selected_room}")

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️ Avg Temp (°C)", f"{df_filtered[temp_col].mean():.2f}")
    col2.metric("🌡️ Max Temp (°C)", f"{df_filtered[temp_col].max():.2f}")
    col3.metric("🌡️ Min Temp (°C)", f"{df_filtered[temp_col].min():.2f}")
    col4.metric("⚡ Total Energy (kWh)", f"{df_filtered[energy_col].sum():.2f}")

    # Grouping
    if time_group == "Daily":
        df_filtered["Group"] = df_filtered["AC_Timestamp"].dt.date
    elif time_group == "Weekly":
        df_filtered["Group"] = df_filtered["AC_Timestamp"].dt.to_period("W").astype(str)
    elif time_group == "Monthly":
        df_filtered["Group"] = df_filtered["AC_Timestamp"].dt.to_period("M").astype(str)
    elif time_group == "Yearly":
        df_filtered["Group"] = df_filtered["AC_Timestamp"].dt.to_period("Y").astype(str)

    # Charts
    st.subheader("📈 Temperature Over Time")
    fig_temp = px.line(df_filtered, x="AC_Timestamp", y=temp_col, title="Temperature Trend", markers=True)
    st.plotly_chart(fig_temp, use_container_width=True)

    st.subheader("💧 Humidity Over Time")
    fig_hum = px.line(df_filtered, x="AC_Timestamp", y=hum_col, title="Humidity Trend", markers=True)
    st.plotly_chart(fig_hum, use_container_width=True)

    st.subheader("⚡ Energy Consumption Over Time")
    fig_energy = px.line(df_filtered, x="AC_Timestamp", y=energy_col, title="Energy Usage", markers=True)
    st.plotly_chart(fig_energy, use_container_width=True)

    # Export Button
    st.subheader("📁 Download Data")
    download_df = df_filtered[["AC_Timestamp", temp_col, hum_col, energy_col]]
    st.download_button(
        label="Download as Excel",
        data=download_df.to_excel(index=False, engine='openpyxl'),
        file_name=f"{selected_room}_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ----- LOGIC ENTRY -----
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
else:
    main()
    st.sidebar.markdown("---")
    st.sidebar.write(f"✅ Logged in as: {st.session_state['email']}")
    st.sidebar.write(f"🕒 Login Time: {st.session_state['login_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()
