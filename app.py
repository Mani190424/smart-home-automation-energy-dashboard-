
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Load data
df = pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

# Sidebar - Theme & Navigation
st.sidebar.markdown("### 🎨 Select Theme")
theme = st.sidebar.radio("Mode", ["Dark", "Light"], index=0)
st.markdown(f"<style>body {{ background-color: {'#0e1117' if theme == 'Dark' else '#FFFFFF'}; }}</style>", unsafe_allow_html=True)

st.sidebar.markdown("### 🧭 Navigate")
page = st.sidebar.selectbox("Navigation", ["🏠 Home", "📊 Room-wise", "📈 Trends", "⚙️ Settings"])

# Sidebar - Filters
st.sidebar.markdown("### 🔍 Filters")
start_date = df["Timestamp"].min().date()
end_date = df["Timestamp"].max().date()
date_range = st.sidebar.date_input("Select Date Range", [start_date, end_date])
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

# Extract rooms from columns
room_names = sorted(set(col.split("_")[1] for col in df.columns if "_" in col))

# Main
st.title("🏡 Smart Home Energy Dashboard")

if page == "🏠 Home":
    st.subheader("🌡️ Room-wise Temperature & Humidity")
    for room in room_names:
        temp_col = f"Temperature_{room}"
        hum_col = f"Humidity_{room}"
        if temp_col in df.columns and hum_col in df.columns:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(f"🌡️ {room} Temp", f"{df[temp_col].mean():.1f}°C", delta=f"{df[temp_col].max() - df[temp_col].min():.1f}°C")
            with col2:
                st.metric(f"💧 {room} Humidity", f"{df[hum_col].mean():.1f}%", delta=f"{df[hum_col].max() - df[hum_col].min():.1f}%")

elif page == "📊 Room-wise":
    selected_room = st.selectbox("Select Room", room_names)
    temp_col = f"Temperature_{selected_room}"
    hum_col = f"Humidity_{selected_room}"
    if temp_col in df.columns and hum_col in df.columns:
        fig1 = px.line(df, x="Timestamp", y=temp_col, title=f"{selected_room} - Temperature Over Time")
        fig2 = px.line(df, x="Timestamp", y=hum_col, title=f"{selected_room} - Humidity Over Time")
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

elif page == "📈 Trends":
    st.subheader("📊 Trends (All Rooms)")
    for room in room_names:
        temp_col = f"Temperature_{room}"
        if temp_col in df.columns:
            fig = px.line(df, x="Timestamp", y=temp_col, title=f"{room} - Temperature Trend")
            st.plotly_chart(fig, use_container_width=True)

elif page == "⚙️ Settings":
    st.subheader("⚙️ Dashboard Settings")
    st.markdown("- Toggle theme (Light/Dark)")
    st.markdown("- Navigate between pages")
    st.markdown("- Filter data by date range")
    st.markdown("- Future: Add export/download, notifications")

