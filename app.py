
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page Config
st.set_page_config(
    page_title="Smart Home Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏡"
)

# Load Data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df["AC_Timestamp"] = pd.to_datetime(df["AC_Timestamp"])
    df["Date"] = df["AC_Timestamp"].dt.date
    df["Time"] = df["AC_Timestamp"].dt.time
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filter Data")
min_date = df["AC_Timestamp"].min()
max_date = df["AC_Timestamp"].max()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Apply filter
if isinstance(selected_dates, list) and len(selected_dates) == 2:
    df = df[(df["AC_Timestamp"] >= pd.to_datetime(selected_dates[0])) &
            (df["AC_Timestamp"] <= pd.to_datetime(selected_dates[1]))]

# Header
st.markdown("""
    <h1 style='text-align: center; color: #00ffcc;'>🏡 Smart Home Energy Dashboard</h1>
    <hr style='border: 1px solid #333;'>
""", unsafe_allow_html=True)

# KPIs
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🌡️ Avg Temperature", f"{df[['Temperature_LivingRoom','Temperature_Kitchen','Temperature_Bedroom']].mean().mean():.2f} °C")
with col2:
    st.metric("💧 Avg Humidity", f"{df[['Humidity_LivingRoom','Humidity_Kitchen','Humidity_Bedroom']].mean().mean():.2f} %")
with col3:
    st.metric("⚡ Total Energy Used", f"{df['Energy_Consumption'].sum():.2f} kWh")

st.markdown("---")

# Charts
col1, col2 = st.columns((2,1))
with col1:
    fig1 = px.line(df, x="AC_Timestamp", y="Energy_Consumption", title="⚡ Energy Consumption Over Time",
                   labels={"AC_Timestamp":"Time", "Energy_Consumption":"Energy (kWh)"})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    avg_temp = df[["Temperature_LivingRoom", "Temperature_Kitchen", "Temperature_Bedroom"]].mean()
    fig2 = px.bar(avg_temp, x=avg_temp.index, y=avg_temp.values, 
                  title="🌡️ Avg Temperature by Room",
                  labels={"x":"Room", "y":"Avg Temp (°C)"})
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns((1,1))
with col3:
    avg_humidity = df[["Humidity_LivingRoom", "Humidity_Kitchen", "Humidity_Bedroom"]].mean()
    fig3 = px.pie(values=avg_humidity.values, names=avg_humidity.index,
                  title="💧 Humidity Distribution by Room")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.dataframe(df.tail(10), use_container_width=True)

# Download filtered data
csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Filtered Data", data=csv, file_name="filtered_data.csv", mime='text/csv')
