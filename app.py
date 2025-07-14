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

room_options = ["LivingRoom", "Kitchen", "Bedroom"]
selected_room = st.sidebar.selectbox("Select Room", room_options)

# Apply date filter
if isinstance(selected_dates, list) and len(selected_dates) == 2:
    df = df[(df["AC_Timestamp"] >= pd.to_datetime(selected_dates[0])) &
            (df["AC_Timestamp"] <= pd.to_datetime(selected_dates[1]))]

# Dynamic column names based on room
temp_col = f"Temperature_{selected_room}"
humid_col = f"Humidity_{selected_room}"

# Header
st.markdown("""
    <div style='background-color:#1f4e5f;padding:10px;border-radius:10px;'>
        <h1 style='text-align: center; color: white;'>🏡 Smart Home Energy Dashboard</h1>
    </div>
    <br>
""", unsafe_allow_html=True)

# KPI Cards
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.markdown("<div style='background-color:#264653;padding:20px;border-radius:10px;color:white;'>"
                f"<h4>🌡️ Avg {selected_room} Temp</h4><h2>{df[temp_col].mean():.2f} °C</h2></div>", unsafe_allow_html=True)
with kpi2:
    st.markdown("<div style='background-color:#2a9d8f;padding:20px;border-radius:10px;color:white;'>"
                f"<h4>💧 Avg {selected_room} Humidity</h4><h2>{df[humid_col].mean():.2f} %</h2></div>", unsafe_allow_html=True)
with kpi3:
    st.markdown("<div style='background-color:#e76f51;padding:20px;border-radius:10px;color:white;'>"
                f"<h4>⚡ Total Energy</h4><h2>{df['Energy_Consumption'].sum():.2f} kWh</h2></div>", unsafe_allow_html=True)

st.markdown("---")

# Charts
col1, col2 = st.columns((2,1))
with col1:
    fig1 = px.line(df, x="AC_Timestamp", y="Energy_Consumption", title="⚡ Energy Over Time")
    fig1.update_layout(plot_bgcolor="#111", paper_bgcolor="#111", font_color="#fff")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.histogram(df, x=temp_col, nbins=20, title=f"🌡️ {selected_room} Temperature Distribution")
    fig2.update_layout(plot_bgcolor="#111", paper_bgcolor="#111", font_color="#fff")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    fig3 = px.pie(values=[df[humid_col].mean(), 100 - df[humid_col].mean()], 
                  names=[f"Avg {selected_room} Humidity", "Other"], 
                  title="💧 Humidity Share")
    fig3.update_layout(paper_bgcolor="#111", font_color="#fff")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.dataframe(df[["AC_Timestamp", temp_col, humid_col, "Energy_Consumption"]].tail(10), use_container_width=True)

# Download Button
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Filtered Data", data=csv, file_name="filtered_data.csv", mime="text/csv")
