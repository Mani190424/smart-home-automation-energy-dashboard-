
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

aggregation = st.sidebar.radio("Aggregation Level", ["Daily", "Weekly", "Monthly"], index=0)

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

# Chart Selector and Type Toggle
chart_option = st.selectbox("📊 Select Chart", ["Energy Over Time", "Temperature Distribution", "Humidity Share"])
chart_type = st.selectbox("🎛️ Select Chart Type", ["Line", "Bar", "Pie", "Scatter", "Combo"])

# Chart Data Logic
if chart_option == "Energy Over Time":
    if aggregation == "Daily":
        df_agg = df.groupby(df["AC_Timestamp"].dt.date).agg({"Energy_Consumption": "sum"}).reset_index()
        df_agg.rename(columns={"AC_Timestamp": "Date"}, inplace=True)
    elif aggregation == "Weekly":
        df_agg = df.resample("W", on="AC_Timestamp")["Energy_Consumption"].sum().reset_index()
        df_agg.rename(columns={"AC_Timestamp": "Date"}, inplace=True)
    else:
        df_agg = df.resample("M", on="AC_Timestamp")["Energy_Consumption"].sum().reset_index()
        df_agg.rename(columns={"AC_Timestamp": "Date"}, inplace=True)

    if chart_type == "Line":
        fig = px.line(df_agg, x="Date", y="Energy_Consumption", title=f"⚡ Energy Over Time ({aggregation})")
    elif chart_type == "Bar":
        fig = px.bar(df_agg, x="Date", y="Energy_Consumption", title=f"⚡ Energy Over Time ({aggregation})")
    elif chart_type == "Scatter":
        fig = px.scatter(df_agg, x="Date", y="Energy_Consumption", title=f"⚡ Energy Over Time ({aggregation})")
    elif chart_type == "Combo":
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_agg["Date"], y=df_agg["Energy_Consumption"], name="Bar"))
        fig.add_trace(go.Scatter(x=df_agg["Date"], y=df_agg["Energy_Consumption"], mode='lines+markers', name="Line"))
        fig.update_layout(title=f"⚡ Energy Over Time ({aggregation})")
    else:
        fig = px.area(df_agg, x="Date", y="Energy_Consumption", title=f"⚡ Energy Over Time ({aggregation})")

    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Temperature Distribution":
    if chart_type in ["Bar", "Line", "Area"]:
        fig = px.histogram(df, x=temp_col, nbins=20, title=f"🌡️ {selected_room} Temperature Distribution")
    elif chart_type == "Scatter":
        fig = px.scatter(df, x="AC_Timestamp", y=temp_col, title=f"🌡️ Temp Scatter - {selected_room}")
    elif chart_type == "Combo":
        fig = go.Figure()
        fig.add_trace(go.Box(y=df[temp_col], name="Temp Distribution"))
        fig.update_layout(title=f"🌡️ Temp Box Chart - {selected_room}")
    else:
        fig = px.histogram(df, x=temp_col, nbins=20, title=f"🌡️ {selected_room} Temperature Distribution")
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Humidity Share":
    avg_humidity = df[humid_col].mean()
    if chart_type == "Pie":
        fig = px.pie(values=[avg_humidity, 100 - avg_humidity], 
                     names=[f"Avg {selected_room} Humidity", "Other"], 
                     title="💧 Humidity Share")
    elif chart_type == "Bar":
        fig = px.bar(x=[humid_col, "Other"], y=[avg_humidity, 100 - avg_humidity], 
                     title="💧 Humidity Share")
    elif chart_type == "Scatter":
        fig = px.scatter(x=[humid_col, "Other"], y=[avg_humidity, 100 - avg_humidity], title="💧 Humidity Share")
    elif chart_type == "Combo":
        fig = go.Figure()
        fig.add_trace(go.Pie(values=[avg_humidity], labels=[f"{selected_room}"], hole=0.4))
        fig.update_layout(title="💧 Humidity Combo View")
    else:
        fig = px.pie(values=[avg_humidity, 100 - avg_humidity], 
                     names=[f"Avg {selected_room} Humidity", "Other"], 
                     title="💧 Humidity Share")
    st.plotly_chart(fig, use_container_width=True)

# Table & Download
st.markdown("---")
st.dataframe(df[["AC_Timestamp", temp_col, humid_col, "Energy_Consumption"]].tail(10), use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Filtered Data", data=csv, file_name="filtered_data.csv", mime="text/csv")
