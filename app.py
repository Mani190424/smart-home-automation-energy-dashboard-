import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Smart Home Energy Dashboard", layout="wide")
st.title("🏠 Smart Home Automation - Energy Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("processed_smart_home_data.xlsx", sheet_name="Sheet1")
    if "Date" not in df.columns:
        df["Date"] = pd.date_range(start="2024-01-01", periods=len(df), freq="6H")
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔎 Filter Options")
year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique()))
month = st.sidebar.selectbox("Select Month", sorted(df["Month"].unique()))
day = st.sidebar.selectbox("Select Day", sorted(df["Day"].unique()))

room = st.sidebar.selectbox("Select Room", ["Living Room", "Kitchen", "Bedroom"])
sensor_type = st.sidebar.selectbox(
    "Select Sensor Type", ["Temperature", "Humidity", "Light", "Motion", "Energy"]
)

# Apply date filter
filtered_df = df[(df["Year"] == year) & (df["Month"] == month) & (df["Day"] == day)]

# Sensor Column Mapping
sensor_column_map = {
    "Living Room": {
        "Temperature": "Temperature_LivingRoom",
        "Humidity": "Humidity_LivingRoom",
    },
    "Kitchen": {
        "Temperature": "Temperature_Kitchen",
        "Humidity": "Humidity_Kitchen",
    },
    "Bedroom": {
        "Temperature": "Temperature_Bedroom",
        "Humidity": "Humidity_Bedroom",
    },
    "Light": "Light_Intensity",
    "Motion": "Motion_Detected",  # only if column exists
    "Energy": "Energy_Consumption"
}

# Get selected sensor column
if sensor_type in ["Temperature", "Humidity"]:
    sensor_col = sensor_column_map[room][sensor_type]
else:
    sensor_col = sensor_column_map.get(sensor_type)

# --- KPI Cards ---
st.markdown("## 📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

total_power = filtered_df["Energy_Consumption"].sum()
avg_val = filtered_df[sensor_col].mean()
max_val = filtered_df[sensor_col].max()
min_val = filtered_df[sensor_col].min()

col1.metric("🔋 Total Power", f"{total_power:.2f} kWh")
col2.metric(f"📊 Avg {sensor_type}", f"{avg_val:.2f}")
col3.metric(f"📈 Max {sensor_type}", f"{max_val:.2f}")
col4.metric(f"📉 Min {sensor_type}", f"{min_val:.2f}")

st.divider()

# --- Chart: Line ---
st.subheader(f"📈 {sensor_type} Trend in {room}")
fig_line = px.line(filtered_df, x="Date", y=sensor_col, title=f"{sensor_type} Over Time")
st.plotly_chart(fig_line)

# --- Chart: Bar ---
st.subheader("📊 Power Usage by Room (Simulated)")
room_data = {
    "Room": ["Living Room", "Kitchen", "Bedroom"],
    "Power": [
        filtered_df["Temperature_LivingRoom"].mean() * 1.5,
        filtered_df["Temperature_Kitchen"].mean() * 1.5,
        filtered_df["Temperature_Bedroom"].mean() * 1.5,
    ]
}
room_df = pd.DataFrame(room_data)
fig_bar = px.bar(room_df, x="Room", y="Power", color="Room")
st.plotly_chart(fig_bar)

# --- Chart: Pie ---
st.subheader("🥧 Power % by Room")
fig_pie = px.pie(room_df, names="Room", values="Power")
st.plotly_chart(fig_pie)

# --- Download Buttons ---
st.subheader("⬇️ Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", data=csv, file_name="filtered_data.csv", mime="text/csv")

excel_io = BytesIO()
with pd.ExcelWriter(excel_io, engine="openpyxl") as writer:
    filtered_df.to_excel(writer, index=False, sheet_name="FilteredData")
excel_io.seek(0)
st.download_button("📥 Download Excel", data=excel_io, file_name="filtered_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Raw Data ---
with st.expander("📄 View Raw Filtered Data"):
    st.dataframe(filtered_df)
