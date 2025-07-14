import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.set_page_config(page_title="Energy Dashboard", layout="wide")
st.title("🏠 Smart Home Energy Dashboard")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

# Show columns to debug
st.write("📋 Columns in CSV:", df.columns.tolist())

# Sidebar Filters
st.sidebar.header("🔍 Filters")
min_date = df["Timestamp"].min()
max_date = df["Timestamp"].max()

selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Dynamically detect room columns (excluding Timestamp and non-room columns)
non_room_cols = ["Timestamp"]
room_columns = [col for col in df.columns if col not in non_room_cols]
selected_rooms = st.sidebar.multiselect("Select Room(s)", room_columns, default=room_columns)

# Filter by date range
if isinstance(selected_dates, list) and len(selected_dates) == 2:
    start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
else:
    start_date, end_date = min_date, max_date

filtered_df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]

# Reshape to long format for plotting
melted_df = filtered_df.melt(id_vars=["Timestamp"], value_vars=selected_rooms, var_name="Room", value_name="Energy_Consumption")

# KPI Metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_power = melted_df["Energy_Consumption"].sum()

# Dummy temperature stats (since you don’t have Metric/Temperature columns)
avg_temp = 24.5  # Replace with real logic if available
max_temp = 28.1
min_temp = 20.3

col1.metric("Total Power", f"{total_power:.2f} kWh")
col2.metric("Avg Temp", f"{avg_temp:.2f} °C")
col3.metric("Max Temp", f"{max_temp:.2f} °C")
col4.metric("Min Temp", f"{min_temp:.2f} °C")

# Line Chart – Power Usage Over Time
st.subheader("📈 Power Usage Over Time")
fig_line = px.line(melted_df, x="Timestamp", y="Energy_Consumption", color="Room", labels={"Energy_Consumption": "Power (kWh)"})
st.plotly_chart(fig_line, use_container_width=True)

# Bar Chart – Power Usage by Room (Monthly)
st.subheader("📊 Monthly Power Usage by Room")
bar_df = melted_df.copy()
bar_df["Month"] = bar_df["Timestamp"].dt.to_period("M").astype(str)
bar_chart = bar_df.groupby(["Room", "Month"])["Energy_Consumption"].sum().reset_index()
fig_bar = px.bar(bar_chart, x="Month", y="Energy_Consumption", color="Room", barmode="group", labels={"Energy_Consumption": "Total Power (kWh)"})
st.plotly_chart(fig_bar, use_container_width=True)

# Pie Chart – Power % by Room
st.subheader("🥧 Power Consumption % by Room")
pie_df = melted_df.groupby("Room")["Energy_Consumption"].sum().reset_index()
fig_pie = px.pie(pie_df, values="Energy_Consumption", names="Room", title="Power Usage Share")
st.plotly_chart(fig_pie, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
