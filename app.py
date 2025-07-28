import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# -----------------------------
# Load Data
# -----------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df.columns = df.columns.str.replace(" ", "_")  # ✅ Replace spaces with _
    df['AC_Timestamp'] = pd.to_datetime(df['AC_Timestamp'])
    return df

# -----------------------------
# MAIN APP
# -----------------------------
def main():
    st.title("🏠 Smart Home Energy Dashboard")

    df = load_data()

    # -----------------------------
    # Sidebar Filters
    # -----------------------------
    st.sidebar.header("📊 Filters")
    min_date = df['AC_Timestamp'].min().date()
    max_date = df['AC_Timestamp'].max().date()
    start_date, end_date = st.sidebar.date_input("📅 Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

    time_group = st.sidebar.selectbox("🕒 Group By", ["Daily", "Weekly", "Monthly", "Yearly"])

    room_list = ['LivingRoom', 'Bedroom', 'Outdoor', 'Kitchen']
    selected_room = st.sidebar.selectbox("📍 Select Room", room_list)

    sensor_list = ["Temperature", "Humidity", "Energy_Consumption"]
    if selected_room in ['LivingRoom', 'Bedroom', 'Kitchen']:
        sensor_list += ["Wind_Speed", "Light_Intensity"]

    selected_sensors = st.sidebar.multiselect("📈 Select Sensors", sensor_list, default=sensor_list[:3])

    # -----------------------------
    # Data Filtering
    # -----------------------------
    df_filtered = df[(df['AC_Timestamp'].dt.date >= start_date) & (df['AC_Timestamp'].dt.date <= end_date)]

    # -----------------------------
    # KPI Columns
    # -----------------------------
    temp_col = f"{selected_room}_Temperature"
    hum_col = f"{selected_room}_Humidity"

    st.subheader(f"🛠️ Room: {selected_room}")
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
    # Time Grouping
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
    # Charts
    # -----------------------------
    st.subheader(f"📈 {selected_room} Sensor Trends - {time_group}")
    for sensor in selected_sensors:
        col_name = f"{selected_room}_{sensor}" if sensor != "Energy_Consumption" else sensor
        fig = px.line(chart_df, x='GroupKey', y=col_name, title=f"{sensor.replace('_', ' ')} Over Time", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # Appliance Details (only for some rooms)
    # -----------------------------
    if selected_room in ['LivingRoom', 'Bedroom', 'Kitchen']:
        st.subheader("🛋️ Appliance Info")
        st.markdown("✅ **Fan:** Present\n\n✅ **Light:** Present")

    # -----------------------------
    # Download Filtered Data
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
