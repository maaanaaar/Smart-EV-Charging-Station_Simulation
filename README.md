# ⚡ Smart EV Charging Station Simulation

A **Streamlit-based interactive simulation** of a **smart electric vehicle (EV) charging station** that dynamically adjusts charging power based on **solar energy production** and **grid load conditions**.  
This project demonstrates how intelligent energy management can optimize EV charging, reduce grid stress, and promote renewable energy integration.

---

## 🚀 Overview

The simulation models a **24-hour charging scenario** (1-minute resolution) where:
- **Solar production** follows a realistic daylight curve.
- **Grid load** peaks in the evening.
- A **smart algorithm** dynamically controls charging to:
  - Prioritize solar energy when available.
  - Limit charging during high grid load hours (18:00–22:00).
  - Charge at full power during off-peak hours.

Users can interactively configure:
- Battery capacity  
- Initial state of charge (SoC)  
- Maximum charging power  

All results are visualized in **real time** using interactive **Plotly charts**.

---

## 🧠 Features

✅ Simulates 24-hour energy flow (grid, solar, and EV)  
✅ Smart, rule-based charging control  
✅ Real-time data visualization with Streamlit  
✅ Dynamic SoC tracking and completion time estimation  
✅ Adjustable EV parameters via an interactive dashboard  

---

## 🧩 Tech Stack

| Category | Tools / Libraries |
|-----------|------------------|
| Language | Python |
| Frontend | Streamlit |
| Data Processing | NumPy, Pandas |
| Visualization | Plotly |
| Time Management | datetime, time |

---

## 📊 Simulation Logic

**1. Data Generation**
- `Grid_Load_kW`: varies sinusoidally over 24 hours, peaking in the evening.
- `Solar_Prod_kW`: bell-shaped production curve with peak around noon.

**2. Dynamic Charging Algorithm**
- Prioritize solar > 5 kW.  
- Limit power to ≤5 kW during 18:00–22:00 (peak load).  
- Charge at max power otherwise.  
- Update battery **State of Charge (SoC)** at each step until 100%.

**3. Visualization**
- **Power Metrics Chart:** Grid Load, Solar Production, Charging Power.  
- **SoC Chart:** EV battery charge evolution.  
- **Metrics:** Current SoC and estimated full-charge time.

---

