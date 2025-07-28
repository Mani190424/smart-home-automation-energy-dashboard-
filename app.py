import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# ----------------------------- SESSION ----------------------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --------------------------- ROOM ICONS ---------------------------- #
room_icons = {
    "Bathroom": "🛁",
    "Bedroom": "🛏️",
    "Kitchen": "🍽️",
    "LivingRoom": "🛋️"
}

# ------------------------ LOAD & CLEAN DATA ------------------------ #
@st.cache_data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df['AC Timestamp'] = pd.to_datetime(df['AC Timestamp'])
    df['Date'] = df['AC Timestamp'].dt.date
    df['Year'] = df['AC Timestamp'].dt.year
    df['Month'] = df['AC Timestamp'].dt.to_period("M").astype(str)
    df['Week'] = df['AC Timestamp'].dt.isocalendar().week
    df['Day'] = df['AC Timestamp'].dt.to_period("D").astype(str)
    return df

# -------------------------- LOGIN SECTION -------------------------- #
def login():
    st.title("🔐 Smart Home Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == "admin" and pwd == "admin":
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# ----------------------------- MAIN APP ---------------------------- #
def main():
    df = load_data()

    # Sidebar Filters
    st.sidebar.title("Filters")
    selected_room = st.sidebar.selectbox("Select Room", list(room_icons.keys()))
    sensors = df[df['Room'] == selected_room]['Sensor'].unique()
    selected_sensor = st.sidebar.selectbox("Select Sensor", sensors)

    # Date Filter
    min_date = df['AC Timestamp'].min().date()
    max_date = df['AC Timestamp'].max().date()
    start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])

    # Time Grouping
    grouping = st.sidebar.radio("Group by", ["Daily", "Weekly", "Monthly", "Yearly"])
    group_col = "Day"
    if grouping == "Weekly":
        group_col = "Week"
    elif grouping == "Monthly":
        group_col = "Month"
    elif grouping == "Yearly":
        group_col = "Year"

    # Filtered Data
    df_filtered = df[(df['Room'] == selected_room) &
                     (df['Sensor'] == selected_sensor) &
                     (df['AC Timestamp'].dt.date >= start_date) &
                     (df['AC Timestamp'].dt.date <= end_date)]

    temp_col = "Temperature"
    hum_col = "Humidity"

    # ------------------------ KPI Cards ------------------------ #
    avg_temp = df_filtered[temp_col].mean()
    max_temp = df_filtered[temp_col].max()
    min_temp = df_filtered[temp_col].min()
    avg_hum = df_filtered[hum_col].mean()
    max_hum = df_filtered[hum_col].max()
    min_hum = df_filtered[hum_col].min()
    total_energy = df_filtered['Energy_Consumption'].sum()

    st.markdown(f"## {room_icons[selected_room]} {selected_room} Dashboard")
    st.write(f"### Sensor: {selected_sensor}")

    col1, col2, col3 = st.columns(3)
    col1.metric("🌡️ Avg Temperature", f"{avg_temp:.2f} °C")
    col2.metric("🌡️ Max Temperature", f"{max_temp:.2f} °C")
    col3.metric("🌡️ Min Temperature", f"{min_temp:.2f} °C")

    col4, col5, col6 = st.columns(3)
    col4.metric("💧 Avg Humidity", f"{avg_hum:.2f} %")
    col5.metric("💧 Max Humidity", f"{max_hum:.2f} %")
    col6.metric("💧 Min Humidity", f"{min_hum:.2f} %")

    st.metric("⚡ Total Energy Consumption", f"{total_energy:.2f} kWh")

    # ------------------------ Charts ------------------------ #
    chart_df = df_filtered.groupby(group_col).agg({
        temp_col: "mean",
        hum_col: "mean",
        "Energy_Consumption": "sum"
    }).reset_index()

    st.write("### 📈 Temperature Over Time")
    fig1 = px.line(chart_df, x=group_col, y=temp_col, title="Temperature")
    st.plotly_chart(fig1, use_container_width=True)

    st.write("### 💧 Humidity Over Time")
    fig2 = px.line(chart_df, x=group_col, y=hum_col, title="Humidity")
    st.plotly_chart(fig2, use_container_width=True)

    # ------------------------ Download ------------------------ #
    st.write("### 📥 Download Filtered Data")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="FilteredData")
        writer.close()
    st.download_button("Download as Excel", buffer.getvalue(), "SmartHomeData.xlsx")

# --------------------------- APP ENTRY ---------------------------- #
if not st.session_state.logged_in:
    login()
else:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
    main()
