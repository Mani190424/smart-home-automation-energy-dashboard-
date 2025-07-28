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
    df['AC_Timestamp'] = pd.to_datetime(df['AC_Timestamp'])
    return df

# -----------------------------
# MAIN APP
# -----------------------------
def main():
    st.title("🏠 Smart Home Energy Dashboard")

    # -----------------------------
    # Login Section
    # -----------------------------
    st.sidebar.header("🔐 Login")
    email = st.sidebar.text_input("Email", value="data.analyst190124@gmail.com")
    password = st.sidebar.text_input("Password", type="password")
    login_btn = st.sidebar.button("Login")

    if login_btn:
        if email == "data.analyst190124@gmail.com":
            st.sidebar.success("✅ Logged in as Admin")
        else:
            st.sidebar.error("❌ Invalid Email")
            st.stop()

    df = load_data()

    # -----------------------------
    # Room Tabs & Selection
    # -----------------------------
    room_list = ['Bathroom', 'Bedroom', 'Kitchen', 'LivingRoom']
    selected_room = st.sidebar.radio("Select Room", room_list)

    # -----------------------------
    # Date Filter & Time Grouping
    # -----------------------------
    min_date = df['AC_Timestamp'].min().date()
    max_date = df['AC_Timestamp'].max().date()
    start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

    time_group = st.sidebar.selectbox("Group by", ["Daily", "Weekly", "Monthly", "Yearly"])

    df_filtered = df[(df['AC_Timestamp'].dt.date >= start_date) & (df['AC_Timestamp'].dt.date <= end_date)]

    # -----------------------------
    # Column Mapping
    # -----------------------------
    temp_col = f"{selected_room}_Temperature"
    hum_col = f"{selected_room}_Humidity"

    # -----------------------------
    # KPI Cards
    # -----------------------------
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

    chart_df = df_filtered.groupby('GroupKey').agg({
        temp_col: "mean",
        hum_col: "mean",
        "Energy_Consumption": "sum"
    }).reset_index()

    # -----------------------------
    # Charts
    # -----------------------------
    st.subheader(f"📊 {selected_room} Sensor Charts ({time_group})")
    
    fig1 = px.line(chart_df, x='GroupKey', y=temp_col, title="Temperature Over Time", markers=True)
    fig2 = px.line(chart_df, x='GroupKey', y=hum_col, title="Humidity Over Time", markers=True)
    fig3 = px.line(chart_df, x='GroupKey', y='Energy_Consumption', title="Energy Usage Over Time", markers=True)

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

    # -----------------------------
    # Download Data
    # -----------------------------
    st.subheader("⬇️ Download Filtered Data")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="SmartHome")
        writer.close()
    st.download_button(label="📥 Download Excel", data=buffer.getvalue(), file_name="Smart_Home_Filtered.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    main()
