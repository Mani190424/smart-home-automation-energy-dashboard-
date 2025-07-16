# 🏡 Smart Home Energy Dashboard

An interactive Streamlit dashboard for analyzing room-wise energy usage, temperature, and humidity data from smart homes.

---

### 🌟 Features

- 📅 Date range filtering
- 🏠 Room selector: LivingRoom, Kitchen, Bedroom
- 📊 Aggregation by Daily / Weekly / Monthly
- ⚡ Energy over time with chart type toggle (Line, Bar, Scatter, Combo)
- 🌡️ Temperature distribution (Line, Bar, Box)
- 💧 Humidity share (Pie, Bar, Scatter)
- 📥 Download filtered data as CSV
- 🔐 Optional login protection (available in advanced version)

---

### 📸 Sample Screens

_Add your dashboard screenshot or preview GIF here_

---

### 🚀 How to Run

```bash
# 1. Clone the repo
git clone https://github.com/your-username/smart-home-dashboard.git
cd smart-home-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

---

### 📁 Project Structure

```
smart-home-dashboard/
├── app.py
├── processed_with_ac_timestamp(Sheet1).csv
├── requirements.txt
└── README.md
```

---

### 📦 Dependencies

- `streamlit`
- `pandas`
- `plotly`

---

### 📄 License

This project is for educational/demo purposes. MIT license.
