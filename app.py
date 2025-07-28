import streamlit as st
import pandas as pd
import datetime as dt
from io import BytesIO
import matplotlib.pyplot as plt

# --------------------- LOGIN FUNCTIONS ---------------------
def login():
    st.session_state["login_time"] = dt.datetime.now()
    st.session_state["logged_in"] = True
    st.success("Login successful ✅")

def logout():
    st.session_state["logged_in"] = False
    st.session_state.pop("login_time", None)
    st.success("You’ve been logged out ✅")

# --------------------- LOAD DATA ---------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("processed_with_ac_timestamp(Sheet1).csv")
        df.rename(columns=lambda x: x.strip(), inplace=True)
        df['AC_Timestamp'] = pd.to_datetime(df['AC_Timestamp'], errors='coerce')
        df.dropna(subset=['AC_Timestamp'], inplace=True)
        df['Date'] = df['AC_Timestamp'].dt.date
        df['Year'] = df['AC_Timestamp'].dt.year
        df['Month'] = df['AC_Timestamp'].dt.month
        df['Week'] = df['AC_Timestamp'].dt.strftime('%Y-%U')
        df['Day'] = df['AC_Timestamp'].dt.strftime('%Y-%m-%d')
        return df
    except FileNotFoundError:
        st.error("🚫 CSV file not found.")
        return pd.DataFrame()

# --------------------- MAIN APP ---------------------
def main():
    st.set_page_config("Smart Home Dashboard", layout="wide")
    st.title("🏠 Smart Home Energy Dashboard")

    # --------------------- Login Section ---------------------
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit and username == "admin" and password == "1234":
                login()
            elif submit:
                st.error("Invalid credentials")
        return
    else:
        st.sidebar.write(f"🕒 Login Time: {st.session_state['login_time'].strftime('%H:%M:%S')}")
        if st.sidebar.button("Logout"):
            logout()
            st.experimental_rerun()

    df = load_data()
    if df.empty:
        return

    # --------------------- Filters ---------------------
    col1, col2 = st.columns(2)
    with col1:
        date_from = st.date_input("From Date", min(df['Date']))
    with col2:
        date_to = st.date_input("To Date", max(df['Date']))

    df_filtered = df[(df['Date'] >= date_from) & (df['Date'] <= date_to)]

    view_by = st.radio("⏱️ View By", ["Daily", "Weekly", "Monthly", "Yearly"], horizontal=True)
    group_col = {
        "Daily": "Day",
        "Weekly": "Week",
        "Monthly": "Month",
        "Yearly": "Year"
    }[view_by]

    # --------------------- Rooms ---------------------
    room_tabs = {
        "🛁 Bathroom": "Bathroom",
        "🛏️ Bedroom": "Bedroom",
        "🍳 Kitchen": "Kitchen",
        "🛋️ LivingRoom": "LivingRoom"
    }

    selected_tabs = st.tabs(list(room_tabs.keys()))
    for i, room in enumerate(room_tabs.values()):
        with selected_tabs[i]:
            room_df = df_filtered.copy()

            temp_col = f"Temperature_{room}"
            hum_col = f"Humidity_{room}"

            if temp_col in room_df.columns:
                avg_temp = room_df[temp_col].mean()
                max_temp = room_df[temp_col].max()
                min_temp = room_df[temp_col].min()
            else:
                avg_temp = max_temp = min_temp = 0

            if hum_col in room_df.columns:
                avg_humidity = room_df[hum_col].mean()
            else:
                avg_humidity = 0

            total_power = room_df["Energy_Consumption"].sum()

            # KPI cards
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("⚡ Total Energy (kWh)", f"{total_power:.2f}")
            k2.metric("🌡️ Avg Temp", f"{avg_temp:.1f} °C")
            k3.metric("🔥 Max Temp", f"{max_temp:.1f} °C")
            k4.metric("❄️ Min Temp", f"{min_temp:.1f} °C")
            k5.metric("💧 Avg Humidity", f"{avg_humidity:.1f} %")

            # Group for charts
            chart_df = room_df.groupby(group_col).agg({
                temp_col: "mean",
                hum_col: "mean",
                "Energy_Consumption": "sum"
            }).reset_index()

            # Charts
            st.markdown("#### 📈 Temperature Trend")
            st.line_chart(chart_df, x=group_col, y=temp_col, use_container_width=True)

            st.markdown("#### 💧 Humidity Trend")
            st.line_chart(chart_df, x=group_col, y=hum_col, use_container_width=True)

            st.markdown("#### ⚡ Energy Consumption Trend")
            st.bar_chart(chart_df, x=group_col, y="Energy_Consumption", use_container_width=True)

    # --------------------- Download Section ---------------------
    st.markdown("---")
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="FilteredData")
    st.download_button(
        "⬇️ Download Filtered Data (Excel)",
        data=buffer.getvalue(),
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    main()
