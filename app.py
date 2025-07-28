import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

# ---------------- LOGIN ----------------
def check_login(username, password):
    return username == "admin" and password == "smart123"

def login_screen():
    st.markdown("## 🔐 Login to Smart Home Dashboard")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        if check_login(username, password):
            st.session_state.logged_in = True
            st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("✅ Login successful")
        else:
            st.error("❌ Invalid credentials")

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "login_time" not in st.session_state:
    st.session_state.login_time = None

# ---------------- LOGOUT ----------------
if st.session_state.logged_in:
    with st.sidebar:
        st.markdown(f"🟢 Logged in as **admin**")
        st.markdown(f"🕒 Login Time: {st.session_state.login_time}")
        if st.button("🔓 Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ---------------- DASHBOARD ----------------
st.set_page_config(page_title="Smart Home Dashboard", layout="wide")
st.title("🏠 Smart Home Energy Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
    if "Date" not in df.columns:
        df["Date"] = pd.date_range(start="2024-01-01", periods=len(df), freq="6H")
    df["Date"] = pd.to_datetime(df["AC_Timestamp"])
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    return df

df = load_data()

# ---------------- FILTERS ----------------
st.sidebar.header("📅 Filter Data")
year = st.sidebar.selectbox("Year", sorted(df["Year"].unique()))
month = st.sidebar.selectbox("Month", sorted(df["Month"].unique()))
day = st.sidebar.selectbox("Day", sorted(df["Day"].unique()))
room = st.sidebar.multiselect("Select Room", ["LivingRoom", "Kitchen", "Bedroom"], default=["LivingRoom", "Kitchen", "Bedroom"])
sensor = st.sidebar.multiselect("Select Sensor", ["Temperature", "Humidity"], default=["Temperature", "Humidity"])

filtered_df = df[(df["Year"] == year) & (df["Month"] == month) & (df["Day"] == day)]

# ---------------- KPI ----------------
st.markdown("## 📊 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

total_power = filtered_df["Energy_Consumption"].sum()
temps = []
for r in room:
    col = f"Temperature_{r}"
    if col in filtered_df.columns:
        temps.append(filtered_df[col])
avg_temp = pd.concat(temps, axis=1).mean().mean()
max_temp = pd.concat(temps, axis=1).max().max()
min_temp = pd.concat(temps, axis=1).min().min()

col1.metric("🔋 Total Power", f"{total_power:.2f} kWh")
col2.metric("🌡️ Avg Temp", f"{avg_temp:.2f} °C")
col3.metric("🔥 Max Temp", f"{max_temp:.2f} °C")
col4.metric("❄️ Min Temp", f"{min_temp:.2f} °C")

st.divider()

# ---------------- LINE CHART ----------------
st.subheader("📈 Power Usage Over Time")
line_df = filtered_df[["Date", "Energy_Consumption"]].set_index("Date")
st.line_chart(line_df)

# ---------------- BAR CHART ----------------
st.subheader("📊 Simulated Power Usage by Room")
room_power = []
for r in room:
    t_col = f"Temperature_{r}"
    if t_col in filtered_df.columns:
        avg = filtered_df[t_col].mean() * 1.5
        room_power.append({"Room": r, "Power": avg})
room_df = pd.DataFrame(room_power)
bar_fig = px.bar(room_df, x="Room", y="Power", color="Room", title="Room-wise Power Usage")
st.plotly_chart(bar_fig)

# ---------------- PIE CHART ----------------
st.subheader("🥧 Power Percentage by Room")
pie_fig = px.pie(room_df, names="Room", values="Power", title="Room Distribution")
st.plotly_chart(pie_fig)

# ---------------- DOWNLOAD ----------------
st.subheader("💾 Download Filtered Data")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered Data')
        writer.close()
    return output.getvalue()

excel_data = to_excel(filtered_df)
st.download_button("📥 Download Excel", data=excel_data, file_name='filtered_data.xlsx')
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download CSV", data=csv_data, file_name='filtered_data.csv')

# ---------------- RAW DATA ----------------
with st.expander("📄 Show Raw Data"):
    st.dataframe(filtered_df)
