
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("processed_with_timestamp.csv", parse_dates=["Timestamp"])

df = load_data()

st.sidebar.header("🔍 Filters")
min_date = df["Timestamp"].min()
max_date = df["Timestamp"].max()
selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date])

non_room_cols = ["Timestamp"]
room_columns = [col for col in df.columns if col not in non_room_cols]
selected_rooms = st.sidebar.multiselect("Select Room(s)", room_columns, default=room_columns)

start_date, end_date = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
filtered_df = df[(df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)]
melted_df = filtered_df.melt(id_vars=["Timestamp"], value_vars=selected_rooms, 
                             var_name="Room", value_name="Energy_Consumption")

# --- Weekly / Monthly Toggle ---
agg_option = st.selectbox("📅 View Aggregated By", ["Monthly", "Weekly"])
if agg_option == "Monthly":
    melted_df["Period"] = melted_df["Timestamp"].dt.to_period("M").astype(str)
else:
    melted_df["Period"] = melted_df["Timestamp"].dt.to_period("W").astype(str)

# Bar Chart
st.markdown(f"### 📊 {agg_option} Power Usage by Room")
bar_chart_df = melted_df.groupby(["Room", "Period"])["Energy_Consumption"].sum().reset_index()
fig_bar = px.bar(bar_chart_df, x="Period", y="Energy_Consumption", color="Room", barmode="group", template="plotly_dark")
st.plotly_chart(fig_bar, use_container_width=True)
