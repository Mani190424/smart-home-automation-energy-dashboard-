
import pandas as pd
import yagmail
from datetime import datetime

# === CONFIGURATION ===
SENDER_EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"  # Get from https://myaccount.google.com/apppasswords
RECIPIENT_EMAIL = "recipient_email@gmail.com"
CSV_FILE = "processed_with_ac_timestamp(Sheet1).csv"

# === LOAD TODAY'S DATA ===
df = pd.read_csv(CSV_FILE)
df["AC_Timestamp"] = pd.to_datetime(df["AC_Timestamp"])
today = pd.Timestamp.today().normalize()
df_today = df[df["AC_Timestamp"].dt.date == today.date()]

# === GENERATE SUMMARY ===
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

# === SEND EMAIL ===
try:
    yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)
    yag.send(
        to=RECIPIENT_EMAIL,
        subject=f"Smart Home Report – {today.date()}",
        contents=[summary],
        attachments=[CSV_FILE]
    )
    print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Email sending failed:", e)
