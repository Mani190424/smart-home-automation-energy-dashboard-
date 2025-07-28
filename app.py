import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --------- Authentication ---------
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔐 Smart Home Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.login_time = datetime.now()
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid credentials")
        st.stop()

def logout():
    st.session_state.logged_in = False
    st.experimental_rerun()

login()

# --------- Sidebar ---------
st.sidebar.title("🧾 Filter Options")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    df.rename(columns={"AC_Timestamp": "Date"}, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# From-To Date Filter
min_date, max_date = df["Date"].min(), df["Date"].max()
from_date = st.sidebar.date_input("From", min_value=min_date, max_value=max_date, value=min_date)
to_date = st.sidebar.date_input("To", min_value=min_date, max_value=max_date, value=max_date)

# Room selection
rooms = ["LivingRoom", "Kitchen", "Bedroom"]
selected_rooms = st.sidebar.multiselect("Select Rooms", rooms, default=rooms)

# Theme
theme = st.sidebar.radio("Theme", ["🌞 Light", "🌙 Dark"])
st.markdown(
    f"""<style>
        body {{ background-color: {'#0e1117' if theme == "🌙 Dark" else '#ffffff'}; }}
    </style>""",
    unsafe_allow_html=True,
)

# Logout button
if st.sidebar.button("Logout"):
    logout()

# Filter data
filtered_df = df[(df["Date"].dt.date >= from_date) & (df["Date"].dt.date <= to_date)]

# KPI Calculations
energy = filtered_df["Energy_Consumption"].sum()
temp_cols = [f"Temperature_{room}" for room in selected_rooms]
humidity_cols = [f"Humidity_{room}" for room in selected_rooms]

avg_temp = filtered_df[temp_cols].mean().mean() if temp_cols else 0
avg_humidity = filtered_df[humidity_cols].mean().mean() if humidity_cols else 0

# --------- MAIN ---------
st.title("🏠 Smart Home Energy Dashboard")

st.markdown(f"""
<style>
.kpi-card {{
    padding: 1rem;
    border-radius: 1rem;
    background-color: #262730;
    text-align: center;
    color: white;
    font-size: 1.3rem;
    margin-bottom: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# KPI Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='kpi-card'>⚡ Total Energy<br><b>{energy:.1f} kWh</b></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='kpi-card'>🌡️ Avg Temp<br><b>{avg_temp:.1f} °C</b></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='kpi-card'>💧 Avg Humidity<br><b>{avg_humidity:.1f} %</b></div>", unsafe_allow_html=True)

# Chart: Power Usage Over Time
st.subheader("📈 Power Usage Over Time")
st.line_chart(filtered_df.set_index("Date")["Energy_Consumption"])

# Bar Chart: Power by Room
st.subheader("📊 Power Consumption by Room")
room_energy = {room: filtered_df[f"Temperature_{room}"].sum() for room in selected_rooms if f"Temperature_{room}" in df.columns}
room_df = pd.DataFrame(list(room_energy.items()), columns=["Room", "Total Power"])
fig_bar = px.bar(room_df, x="Room", y="Total Power", color="Room", title="Power Usage by Room")
st.plotly_chart(fig_bar)

# Pie Chart: Room %
st.subheader("🥧 Energy Usage Distribution")
fig_pie = px.pie(room_df, names="Room", values="Total Power", title="Power % by Room")
st.plotly_chart(fig_pie)

# Download
st.subheader("⬇️ Download Filtered Data")
col_csv, col_excel = st.columns(2)
with col_csv:
    st.download_button("Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv")
with col_excel:
    st.download_button("Download Excel", data=filtered_df.to_excel(index=False), file_name="filtered_data.xlsx")

# Track login time
if "login_time" in st.session_state:
    st.sidebar.caption(f"🕒 Logged in at: {st.session_state.login_time.strftime('%H:%M:%S')}")

