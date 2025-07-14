
import streamlit as st
import pandas as pd

# Load data
df = pd.read_csv("processed_with_timestamp.csv")

# Convert Timestamp column to datetime
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Check if 'Room' column exists before using it
if "Room" in df.columns:
    room_list = df["Room"].unique().tolist()
else:
    room_list = []

# Sidebar Filters
st.sidebar.title("🎯 Filters")
date_range = st.sidebar.date_input("Select Date Range", [df["Timestamp"].min(), df["Timestamp"].max()])
selected_rooms = st.sidebar.multiselect("Select Room(s)", options=room_list, default=room_list)

# Filter data by date range
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

# Display filtered data or error message
if not filtered_df.empty:
    st.title("📊 Smart Home Energy Dashboard")
    st.write(filtered_df.head())
else:
    st.warning("No data available for the selected filters.")
