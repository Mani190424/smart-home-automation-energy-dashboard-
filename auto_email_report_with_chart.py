
import pandas as pd
import matplotlib.pyplot as plt
import yagmail
from datetime import datetime

# === CONFIG ===
SENDER_EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"  # From https://myaccount.google.com/apppasswords
RECIPIENT_EMAIL = "recipient_email@gmail.com"
CSV_FILE = "processed_with_ac_timestamp(Sheet1).csv"
CHART_FILE = "daily_chart.png"

# === LOAD TODAY'S DATA ===
df = pd.read_csv(CSV_FILE)
df["AC_Timestamp"] = pd.to_datetime(df["AC_Timestamp"])
today = pd.Timestamp.today().normalize()
df_today = df[df["AC_Timestamp"].dt.date == today.date()]

if df_today.empty:
    summary = f"No data available for {today.date()}."
else:
    energy = df_today["Energy_Consumption"].sum()
    temp = df_today["Temperature_LivingRoom"].mean()
    humid = df_today["Humidity_LivingRoom"].mean()
    summary = f"""
📊 Smart Home Daily Report – {today.date()}

⚡ Total Energy: {energy:.2f} kWh
🌡️ Avg Temp (Living Room): {temp:.2f} °C
💧 Avg Humidity (Living Room): {humid:.2f} %
    """.strip()

    # === PLOT CHART ===
    plt.figure(figsize=(10, 6))
    plt.plot(df_today["AC_Timestamp"], df_today["Energy_Consumption"], label="Energy (kWh)", color="orange")
    plt.plot(df_today["AC_Timestamp"], df_today["Temperature_LivingRoom"], label="Temp (°C)", color="purple")
    plt.plot(df_today["AC_Timestamp"], df_today["Humidity_LivingRoom"], label="Humidity (%)", color="skyblue")
    plt.title(f"📈 Smart Home Metrics – {today.date()}")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(CHART_FILE)
    plt.close()

# === SEND EMAIL ===
try:
    yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)
    yag.send(
        to=RECIPIENT_EMAIL,
        subject=f"Smart Home Report – {today.date()}",
        contents=[summary, "Attached: CSV + chart image 📎"],
        attachments=[CSV_FILE, CHART_FILE]
    )
    print("✅ Email sent with chart and CSV.")
except Exception as e:
    print("❌ Email sending failed:", e)
