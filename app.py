
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# === USER AUTHENTICATION FROM CSV ===
USERS_FILE = "users.csv"
users_path = os.path.join(os.path.dirname(__file__), USERS_FILE)
users_df = pd.read_csv(users_path)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.email = ""

if not st.session_state.authenticated:
    st.markdown("""
        <h2 style='text-align:center;'>🔐 Login Required</h2>
        <p style='text-align:center;'>Enter your email and password to access the dashboard.</p>
    """, unsafe_allow_html=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns([1, 2])

    with col1:
        login = st.button("Login")
    with col2:
        forgot = st.button("❓ Forgot Password?")

    if login:
        user = users_df[(users_df['email'] == email) & (users_df['password'] == password)]
        if not user.empty:
            st.session_state.authenticated = True
            st.session_state.email = email
            st.success("✅ Login successful")
            st.rerun()
        else:
            st.error("❌ Invalid email or password")

    if forgot:
        with st.expander("📩 Reset your password"):
            user_email = st.text_input("Enter your registered email")
            if st.button("Send Reset Link"):
                if user_email in users_df.email.values:
                    st.success(f"✅ Reset link sent to {user_email} (simulated)")
                else:
                    st.warning("⚠️ Email not found in user list")

    st.stop()
    
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
st.sidebar.header("👤 My Profile")
USER_PROFILE_FILE = "user_profiles.csv"

with st.form("profile_form"):
    username = st.text_input("Username")
    email = st.text_input("Email")
    mobile = st.text_input("Mobile Number")
    submitted = st.form_submit_button("💾 Save Profile")

    if submitted:
        profile_df = pd.DataFrame([{"Username": username, "Email": email, "Mobile": mobile}])

        if os.path.exists(USER_PROFILE_FILE):
            existing_df = pd.read_csv(USER_PROFILE_FILE)
            combined_df = pd.concat([existing_df, profile_df], ignore_index=True)
            combined_df.drop_duplicates(subset=["Email"], keep="last", inplace=True)
        else:
            combined_df = profile_df

        combined_df.to_csv(USER_PROFILE_FILE, index=False)
        st.success(f"✅ Profile Saved: {username} | {email} | {mobile}")

st.sidebar.header("🔍 Filter Data")
min_date = df["AC_Timestamp"].min()
max_date = df["AC_Timestamp"].max()

selected_dates = st.sidebar.date_input(
    "📆Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

room_options = ["LivingRoom", "Kitchen", "Bedroom"]
selected_room = st.sidebar.selectbox("🏡Select Room", room_options)

aggregation = st.sidebar.radio("📈Aggregation Level", ["Daily", "Weekly", "Monthly"], index=0)

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

# ENERGY OVER TIME
st.subheader("⚡ Energy Over Time")
energy_chart_type = st.selectbox("Chart Type - Energy", ["Line", "Bar", "Scatter", "Combo"], key="energy")

if aggregation == "Daily":
    df_energy = df.groupby(df["AC_Timestamp"].dt.date).agg({"Energy_Consumption": "sum"}).reset_index()
    df_energy.rename(columns={"AC_Timestamp": "Date"}, inplace=True)
elif aggregation == "Weekly":
    df_energy = df.resample("W", on="AC_Timestamp")["Energy_Consumption"].sum().reset_index()
    df_energy.rename(columns={"AC_Timestamp": "Date"}, inplace=True)
else:
    df_energy = df.resample("M", on="AC_Timestamp")["Energy_Consumption"].sum().reset_index()
    df_energy.rename(columns={"AC_Timestamp": "Date"}, inplace=True)

if energy_chart_type == "Line":
    fig = px.line(df_energy, x="Date", y="Energy_Consumption")
elif energy_chart_type == "Bar":
    fig = px.bar(df_energy, x="Date", y="Energy_Consumption")
elif energy_chart_type == "Scatter":
    fig = px.scatter(df_energy, x="Date", y="Energy_Consumption")
elif energy_chart_type == "Combo":
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_energy["Date"], y=df_energy["Energy_Consumption"], name="Bar"))
    fig.add_trace(go.Scatter(x=df_energy["Date"], y=df_energy["Energy_Consumption"], mode='lines+markers', name="Line"))
else:
    fig = px.area(df_energy, x="Date", y="Energy_Consumption")

st.plotly_chart(fig, use_container_width=True)

# TEMPERATURE DISTRIBUTION
st.subheader("🌡️ Temperature Distribution")
temp_chart_type = st.selectbox("Chart Type - Temperature", ["Line", "Bar", "Box"], key="temp")

if aggregation == "Daily":
    df_temp = df.groupby(df["AC_Timestamp"].dt.date).agg({temp_col: "mean"}).reset_index()
    df_temp.rename(columns={"AC_Timestamp": "Date"}, inplace=True)
elif aggregation == "Weekly":
    df_temp = df.resample("W", on="AC_Timestamp")[temp_col].mean().reset_index()
    df_temp.rename(columns={"AC_Timestamp": "Date"}, inplace=True)
else:
    df_temp = df.resample("M", on="AC_Timestamp")[temp_col].mean().reset_index()
    df_temp.rename(columns={"AC_Timestamp": "Date"}, inplace=True)

if temp_chart_type == "Line":
    fig = px.line(df_temp, x="Date", y=temp_col)
elif temp_chart_type == "Bar":
    fig = px.bar(df_temp, x="Date", y=temp_col)
elif temp_chart_type == "Box":
    fig = px.box(df, y=temp_col)

st.plotly_chart(fig, use_container_width=True)

# HUMIDITY SHARE
st.subheader("💧 Humidity Share")
humid_chart_type = st.selectbox("Chart Type - Humidity", ["Pie", "Bar", "Scatter"], key="humid")

if aggregation == "Daily":
    df_humid = df.groupby(df["AC_Timestamp"].dt.date).agg({humid_col: "mean"}).reset_index()
elif aggregation == "Weekly":
    df_humid = df.resample("W", on="AC_Timestamp")[humid_col].mean().reset_index()
else:
    df_humid = df.resample("M", on="AC_Timestamp")[humid_col].mean().reset_index()

avg_humidity = df_humid[humid_col].mean()

if humid_chart_type == "Pie":
    fig = px.pie(values=[avg_humidity, 100 - avg_humidity], names=[f"Avg {selected_room} Humidity", "Other"])
elif humid_chart_type == "Bar":
    fig = px.bar(x=[humid_col, "Other"], y=[avg_humidity, 100 - avg_humidity])
elif humid_chart_type == "Scatter":
    fig = px.scatter(x=[humid_col, "Other"], y=[avg_humidity, 100 - avg_humidity])
st.plotly_chart(fig, use_container_width=True)

# In your sidebar (or top section):
start_date, end_date = st.sidebar.date_input("📆Select Date Range", value=[df["AC_Timestamp"].min(), df["AC_Timestamp"].max()])

# Convert to datetime
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Apply filter
filtered_df = df[(df["AC_Timestamp"] >= start_date) & (df["AC_Timestamp"] <= end_date)]

# 📊 Preview table of filtered data
st.markdown("### 🔎 Filtered Data Preview")
st.write(f"Showing {len(filtered_df)} rows from **{start_date}** to **{end_date}**")
st.dataframe(filtered_df, use_container_width=True, height=500)

# 📥 Download section
with st.expander("📩 Download Filtered Report"):
    csv = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="filtered_report.csv", mime="text/csv")


# Table & Download
st.markdown("---")
st.dataframe(df[["AC_Timestamp", temp_col, humid_col, "Energy_Consumption"]].tail(10), use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📩Download Filtered Data", data=csv, file_name="filtered_data.csv", mime="text/csv")
