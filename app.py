import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df['AC_Timestamp'] = pd.to_datetime(df['AC_Timestamp'])
    return df

# Login
def login():
    st.markdown("## 🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email and password:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.session_state.start_time = datetime.now()
            st.success(f"✅ Logged in as {email}")
            st.experimental_rerun()
        else:
            st.error("❌ Enter both email and password.")

# Main Dashboard
def main():
    df = load_data()

    st.sidebar.title("📊 Filter Options")
    room_options = ["Bathroom", "Bedroom", "Kitchen", "LivingRoom"]
    room_icons = {
        "Bathroom": "🛁",
        "Bedroom": "🛏️",
        "Kitchen": "🍳",
        "LivingRoom": "🛋️"
    }
    selected_room = st.sidebar.selectbox("🏠 Select Room", room_options, format_func=lambda x: f"{room_icons[x]} {x}")
    start_date = st.sidebar.date_input("📅 Start Date", df["AC_Timestamp"].min().date())
    end_date = st.sidebar.date_input("📅 End Date", df["AC_Timestamp"].max().date())
    time_group = st.sidebar.radio("⏱️ Time Grouping", ["Daily", "Weekly", "Monthly", "Yearly"])

    if start_date > end_date:
        st.error("Start Date must be before End Date.")
        return

    df_filtered = df[(df["AC_Timestamp"].dt.date >= start_date) & (df["AC_Timestamp"].dt.date <= end_date)]
    room_df = df_filtered[df_filtered["Room"] == selected_room]

    if room_df.empty:
        st.warning("No data available for selected filters.")
        return

    # KPI calculations
    temp_col = f"{selected_room}_Temperature"
    hum_col = f"{selected_room}_Humidity"

    avg_temp = room_df[temp_col].mean()
    max_temp = room_df[temp_col].max()
    min_temp = room_df[temp_col].min()

    avg_hum = room_df[hum_col].mean()
    max_hum = room_df[hum_col].max()
    min_hum = room_df[hum_col].min()

    total_energy = room_df["Energy_Consumption"].sum()

    # Show KPIs
    st.markdown(f"## {room_icons[selected_room]} {selected_room} Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️ Avg Temp (°C)", f"{avg_temp:.2f}")
    col2.metric("🌡️ Max Temp (°C)", f"{max_temp:.2f}")
    col3.metric("🌡️ Min Temp (°C)", f"{min_temp:.2f}")
    col4.metric("⚡ Total Energy", f"{total_energy:.2f} kWh")

    col5, col6, col7 = st.columns(3)
    col5.metric("💧 Avg Humidity (%)", f"{avg_hum:.2f}")
    col6.metric("💧 Max Humidity (%)", f"{max_hum:.2f}")
    col7.metric("💧 Min Humidity (%)", f"{min_hum:.2f}")

    # Time Grouping
    if time_group == "Daily":
        group_col = room_df["AC_Timestamp"].dt.date
    elif time_group == "Weekly":
        group_col = room_df["AC_Timestamp"].dt.to_period("W").apply(lambda r: r.start_time)
    elif time_group == "Monthly":
        group_col = room_df["AC_Timestamp"].dt.to_period("M").apply(lambda r: r.start_time)
    elif time_group == "Yearly":
        group_col = room_df["AC_Timestamp"].dt.to_period("Y").apply(lambda r: r.start_time)

    chart_df = room_df.copy()
    chart_df["Group"] = group_col
    chart_df = chart_df.groupby("Group").agg({
        temp_col: "mean",
        hum_col: "mean",
        "Energy_Consumption": "sum"
    }).reset_index()

    # Line Charts
    st.markdown("### 📈 Temperature Trend")
    fig_temp = px.line(chart_df, x="Group", y=temp_col, title="Average Temperature")
    st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("### 📉 Humidity Trend")
    fig_hum = px.line(chart_df, x="Group", y=hum_col, title="Average Humidity")
    st.plotly_chart(fig_hum, use_container_width=True)

    st.markdown("### ⚡ Energy Consumption Trend")
    fig_energy = px.line(chart_df, x="Group", y="Energy_Consumption", title="Total Energy Consumption")
    st.plotly_chart(fig_energy, use_container_width=True)

    # Download Button
    st.markdown("### 📥 Download Filtered Data (Excel)")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        room_df.to_excel(writer, index=False, sheet_name="Filtered Data")
        writer.close()
    st.download_button("Download Excel", data=buffer.getvalue(), file_name="filtered_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Run App
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    login()
else:
    st.sidebar.markdown(f"👤 **User:** {st.session_state.email}")
    st.sidebar.markdown(f"⏱️ **Session:** {(datetime.now() - st.session_state.start_time).seconds} sec")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()
    main()
