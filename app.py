import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp_renamed.csv")
    df['AC_Timestamp'] = pd.to_datetime(df['AC_Timestamp'], errors='coerce')
    return df.dropna(subset=["AC_Timestamp"])

def main():
    st.title("🏠 Smart Home Energy Dashboard")

    df = load_data()

    # -----------------------------
    # Sidebar or Top Filters
    # -----------------------------
    st.subheader("📍 Room & Date Selection")
    col_top1, col_top2 = st.columns([1, 2])

    with col_top1:
        room_list = ['LivingRoom', 'Bedroom', 'Outdoor', 'Kitchen']
        selected_room = st.selectbox("Select Room", room_list)

    with col_top2:
        min_date = datetime(2004, 1, 1).date()
        max_date = datetime(2012, 7, 21).date()
        start_date, end_date = st.date_input("Select Date Range", [min_date, max_date],
                                             min_value=min_date, max_value=max_date)

    time_group = st.selectbox("🕒 Time Grouping", ["Daily", "Weekly", "Monthly", "Yearly"])

    # -----------------------------
    # Filtered Data
    # -----------------------------
    df_filtered = df[(df['AC_Timestamp'].dt.date >= start_date) & (df['AC_Timestamp'].dt.date <= end_date)]

    # -----------------------------
    # KPI Section
    # -----------------------------
    st.subheader(f"🔢 KPIs - {selected_room}")

    temp_col = f"{selected_room}_Temperature"
    hum_col = f"{selected_room}_Humidity"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌡️ Avg Temp (°C)", f"{df_filtered[temp_col].mean():.2f}")
    with col2:
        st.metric("🌡️ Max Temp (°C)", f"{df_filtered[temp_col].max():.2f}")
    with col3:
        st.metric("💧 Avg Humidity (%)", f"{df_filtered[hum_col].mean():.2f}")
    with col4:
        st.metric("⚡ Total Energy (kWh)", f"{df_filtered['Energy_Consumption'].sum():.2f}")

    # -----------------------------
    # Sensor Selection (Below KPIs)
    # -----------------------------
    st.subheader("📈 Select Sensors to View Trends")

    sensor_list = ["Temperature", "Humidity", "Energy_Consumption"]
if selected_room in ['Living Room', 'Bedroom', 'Kitchen']:
    st.metric("💨 Wind Speed", f"{df_filtered['Wind Speed'].mean():.2f} km/h")
    st.metric("💡 Light Intensity", f"{df_filtered['Light Intensity'].mean():.2f} lux")

    selected_sensors = st.multiselect("Choose Sensors", sensor_list, default=sensor_list[:3])

    # -----------------------------
    # Time Grouping for Charts
    # -----------------------------
    df_filtered['GroupKey'] = df_filtered['AC_Timestamp']
    if time_group == "Daily":
        df_filtered['GroupKey'] = df_filtered['AC_Timestamp'].dt.date
    elif time_group == "Weekly":
        df_filtered['GroupKey'] = df_filtered['AC_Timestamp'].dt.to_period("W").apply(lambda r: r.start_time)
    elif time_group == "Monthly":
        df_filtered['GroupKey'] = df_filtered['AC_Timestamp'].dt.to_period("M").dt.to_timestamp()
    elif time_group == "Yearly":
        df_filtered['GroupKey'] = df_filtered['AC_Timestamp'].dt.to_period("Y").dt.to_timestamp()

    agg_dict = {}
    for sensor in selected_sensors:
        col_name = f"{selected_room}_{sensor}" if sensor != "Energy_Consumption" else sensor
        agg_dict[col_name] = "mean" if sensor != "Energy_Consumption" else "sum"

    chart_df = df_filtered.groupby('GroupKey').agg(agg_dict).reset_index()

    # -----------------------------
    # Line Charts for Selected Sensors
    # -----------------------------
    st.subheader(f"📊 {selected_room} Sensor Trends - {time_group}")
    for sensor in selected_sensors:
        col_name = f"{selected_room}_{sensor}" if sensor != "Energy_Consumption" else sensor
        fig = px.line(chart_df, x='GroupKey', y=col_name,
                      title=f"{sensor.replace('_', ' ')} Over Time", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Appliance Details
    # -----------------------------
    if selected_room in ['LivingRoom', 'Bedroom', 'Kitchen']:
        st.subheader("🛋️ Appliance Info")
        st.markdown("✅ **Fan:** Present")
        st.markdown("✅ **Light:** Present")

    # -----------------------------
    # Download Button
    # -----------------------------
    st.subheader("⬇️ Download Filtered Data")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="FilteredData")
    st.download_button(
        label="📥 Download Excel",
        data=buffer.getvalue(),
        file_name="Smart_Home_Filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == '__main__':
    main()
