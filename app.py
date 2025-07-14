
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

st.sidebar.header("🎛️ Filters")
min_date, max_date = df["Timestamp"].min(), df["Timestamp"].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Safely handle room column
if "Room" in df.columns:
    room_list = df["Room"].dropna().unique().tolist()
else:
    room_list = df["Location"].dropna().unique().tolist() if "Location" in df.columns else []

selected_rooms = st.sidebar.multiselect("Select Room(s)", room_list, default=room_list)

# Apply filters
if isinstance(selected_dates, list) and len(selected_dates) == 2:
    start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
else:
    start_date, end_date = min_date, max_date

filtered_df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

if "Room" in df.columns:
    filtered_df = filtered_df[filtered_df["Room"].isin(selected_rooms)]
elif "Location" in df.columns:
    filtered_df = filtered_df[filtered_df["Location"].isin(selected_rooms)]

st.title("🏠 Smart Home Energy Dashboard")
st.subheader("📊 Data Preview")
st.dataframe(filtered_df.head())

if not filtered_df.empty:
    if "Energy_Consumption" in filtered_df.columns:
        st.subheader("⚡ Total Power Consumption Over Time")
        fig = px.line(filtered_df, x="Timestamp", y="Energy_Consumption", color=filtered_df.get("Room", filtered_df.get("Location", None)))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ 'Energy_Consumption' column not found in data.")
else:
    st.warning("No data available for selected filters.")
