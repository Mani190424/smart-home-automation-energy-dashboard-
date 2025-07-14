
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

# Sidebar Filters
st.sidebar.header("🔍 Filters")
min_date = df["Timestamp"].min()
max_date = df["Timestamp"].max()

selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])
selected_rooms = st.sidebar.multiselect("Select Room(s)", df["Room"].unique(), default=list(df["Room"].unique()))

# Apply Filters
if isinstance(selected_dates, list) and len(selected_dates) == 2:
    start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
else:
    start_date, end_date = min_date, max_date

filtered_df = df[
    (df["Timestamp"] >= start_date) &
    (df["Timestamp"] <= end_date) &
    (df["Room"].isin(selected_rooms))
]

# KPI Metrics
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

total_power = filtered_df["Energy_Consumption"].sum()
avg_temp = filtered_df["Value"][filtered_df["Metric"].str.contains("Temperature")].mean()
max_temp = filtered_df["Value"][filtered_df["Metric"].str.contains("Temperature")].max()
min_temp = filtered_df["Value"][filtered_df["Metric"].str.contains("Temperature")].min()

col1.metric("Total Power", f"{total_power:.2f} kWh")
col2.metric("Avg Temp", f"{avg_temp:.2f} °C" if pd.notna(avg_temp) else "No Data")
col3.metric("Max Temp", f"{max_temp:.2f} °C" if pd.notna(max_temp) else "No Data")
col4.metric("Min Temp", f"{min_temp:.2f} °C" if pd.notna(min_temp) else "No Data")

# Line Chart – Power Usage Over Time
st.subheader("📈 Power Usage Over Time")
power_df = filtered_df[filtered_df["Metric"] == "Energy_Consumption"]
fig_line = px.line(power_df, x="Timestamp", y="Value", color="Room", labels={"Value": "Power (kWh)"})
st.plotly_chart(fig_line, use_container_width=True)

# Bar Chart – Power Usage by Room (Monthly)
st.subheader("📊 Monthly Power Usage by Room")
bar_df = power_df.copy()
bar_df["Month"] = bar_df["Timestamp"].dt.to_period("M").astype(str)
bar_chart = bar_df.groupby(["Room", "Month"])["Value"].sum().reset_index()
fig_bar = px.bar(bar_chart, x="Month", y="Value", color="Room", barmode="group", labels={"Value": "Total Power (kWh)"})
st.plotly_chart(fig_bar, use_container_width=True)

# Pie Chart – Power % by Room
st.subheader("🥧 Power Consumption % by Room")
pie_df = power_df.groupby("Room")["Value"].sum().reset_index()
fig_pie = px.pie(pie_df, values="Value", names="Room", title="Power Usage Share")
st.plotly_chart(fig_pie, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
