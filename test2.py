import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Set random seed for reproducibility
np.random.seed(42)

# Simulate 24-hour data (1-minute resolution)
def generate_simulation_data():
    time_steps = 1440  # 24 hours * 60 minutes
    time_index = pd.date_range(start="2025-05-12 00:00", periods=time_steps, freq="min")
    
    # Grid load: Higher during evening (18:00-22:00), base load ~5 kW
    grid_load = 5 + 10 * np.sin(np.linspace(0, 2 * np.pi, time_steps)) + np.random.normal(0, 1, time_steps)
    grid_load[1080:1320] += 10  # Peak load from 18:00 to 22:00
    
    # Solar production: Peaks at noon, max 15 kW
    solar_prod = 15 * np.exp(-((np.linspace(0, 24, time_steps) - 12) ** 2) / 8) + np.random.normal(0, 0.5, time_steps)
    solar_prod = np.clip(solar_prod, 0, None)  # No negative production
    
    return pd.DataFrame({
        "Time": time_index,
        "Grid_Load_kW": grid_load,
        "Solar_Prod_kW": solar_prod
    })

# Dynamic charging algorithm
def simulate_charging(data, battery_capacity, initial_soc, max_power, step_limit=None):
    soc = initial_soc
    energy_needed = battery_capacity * (1 - initial_soc)  # kWh needed to full charge
    charging_power = []
    soc_values = []
    time_steps = len(data) if step_limit is None else max(1, min(step_limit, len(data)))  # Ensure at least 1 step
    
    # Debug: Log parameters
    st.write(f"Debug: battery_capacity={battery_capacity}, initial_soc={initial_soc}, max_power={max_power}, time_steps={time_steps}")
    
    for i in range(time_steps):
        grid_load = data["Grid_Load_kW"].iloc[i]
        solar_prod = data["Solar_Prod_kW"].iloc[i]
        hour = data["Time"].iloc[i].hour
        
        # Rules for dynamic charging
        if solar_prod > 5:  # Prioritize solar if significant production
            power = min(solar_prod, max_power, energy_needed * 60 / (time_steps - i))  # kW
        elif 18 <= hour <= 22:  # Reduce power during peak grid load
            power = min(5, max_power, energy_needed * 60 / (time_steps - i))  # Load shedding
        else:  # Off-peak: charge at max power if needed
            power = min(max_power, energy_needed * 60 / (time_steps - i))
        
        # Update SoC (energy added in kWh = power * time_step_in_hours)
        energy_added = power * (1 / 60)  # 1 minute = 1/60 hour
        soc += energy_added / battery_capacity
        soc = min(soc, 1.0)  # Cap at 100%
        energy_needed = max(0, battery_capacity * (1 - soc))
        
        charging_power.append(power)
        soc_values.append(soc * 100)  # In percentage
    
    # Pad with zeros/previous values if step_limit < total steps
    if time_steps < len(data):
        charging_power.extend([0] * (len(data) - time_steps))
        soc_values.extend([soc_values[-1] if soc_values else initial_soc * 100] * (len(data) - time_steps))
    
    data["Charging_Power_kW"] = charging_power
    data["SoC_Percent"] = soc_values
    
    # Estimate completion time
    completion_idx = next((i for i, soc in enumerate(soc_values) if soc >= 99.9), len(data) - 1)
    completion_time = data["Time"].iloc[completion_idx]
    
    return data, completion_time

# Streamlit app
def main():
    st.title("Smart EV Charging Station Simulation")
    st.markdown("""
    Simulate a smart EV charging station that adjusts power based on grid load and solar production.
    Adjust the EV parameters and click 'Run Simulation' to see dynamic results in separate diagrams.
    """)

    # User-configurable parameters
    st.subheader("EV Configuration")
    col1, col2, col3 = st.columns(3)
    with col1:
        battery_capacity = st.slider("Battery Capacity (kWh)", min_value=10.0, max_value=100.0, value=60.0, step=5.0, key="battery_capacity_unique")
    with col2:
        initial_soc = st.slider("Initial SoC (%)", min_value=0.0, max_value=90.0, value=20.0, step=5.0, key="initial_soc_unique") / 100
    with col3:
        max_power = st.slider("Max Charging Power (kW)", min_value=3.7, max_value=50.0, value=22.0, step=3.7, key="max_power_unique")

    # Display selected parameters
    st.subheader("Selected Parameters")
    st.write(f"Battery Capacity: {battery_capacity} kWh")
    st.write(f"Initial SoC: {initial_soc*100:.1f}%")
    st.write(f"Max Charging Power: {max_power} kW")

    # Run simulation button
    if st.button("Run Simulation", key="run_simulation_unique"):
        # Clear previous session state
        if "simulation_step" in st.session_state:
            del st.session_state["simulation_step"]
        
        # Generate fresh data
        data = generate_simulation_data()
        
        # Placeholder for dynamic visualization
        power_plot = st.empty()
        soc_plot = st.empty()
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            soc_metric = st.empty()
        with status_col2:
            completion_metric = st.empty()
        
        # Simulate charging dynamically
        total_steps = 1440  # 24 hours * 60 minutes
        step_size = 60  # Update every 60 steps (1 hour) for demo
        for step in range(step_size, total_steps + step_size, step_size):  # Start at step_size to avoid 0
            st.session_state["simulation_step"] = step
            current_step = min(step, total_steps)
            
            # Run simulation up to current step
            sim_data = generate_simulation_data()  # Fresh data to avoid caching
            sim_data, completion_time = simulate_charging(
                sim_data, battery_capacity, initial_soc, max_power, step_limit=current_step
            )
            
            # Power plot (Grid Load, Solar Production, Charging Power)
            power_fig = go.Figure()
            power_fig.add_trace(go.Scatter(x=sim_data["Time"], y=sim_data["Grid_Load_kW"], name="Grid Load (kW)", line=dict(color="red")))
            power_fig.add_trace(go.Scatter(x=sim_data["Time"], y=sim_data["Solar_Prod_kW"], name="Solar Production (kW)", line=dict(color="orange")))
            power_fig.add_trace(go.Scatter(x=sim_data["Time"], y=sim_data["Charging_Power_kW"], name="Charging Power (kW)", line=dict(color="blue")))
            power_fig.update_layout(
                xaxis=dict(title="Time"),
                yaxis=dict(title="Power (kW)", side="left"),
                legend=dict(x=0.01, y=0.99),
                height=400,
                title="Power Metrics"
            )
            power_plot.plotly_chart(power_fig, use_container_width=True)
            
            # SoC plot
            soc_fig = go.Figure()
            soc_fig.add_trace(go.Scatter(x=sim_data["Time"], y=sim_data["SoC_Percent"], name="SoC (%)", line=dict(color="green")))
            soc_fig.update_layout(
                xaxis=dict(title="Time"),
                yaxis=dict(title="SoC (%)", side="right", range=[0, 100]),
                legend=dict(x=0.01, y=0.99),
                height=400,
                title="State of Charge"
            )
            soc_plot.plotly_chart(soc_fig, use_container_width=True)
            
            # Update metrics
            soc_metric.metric("Current SoC", f"{sim_data['SoC_Percent'].iloc[current_step-1]:.1f}%")
            completion_metric.metric("Estimated Completion", completion_time.strftime("%H:%M"))
            
            # Simulate real-time delay
            time.sleep(0.5)  # Update every 0.5 seconds for demo
            
            # Stop if fully charged
            if sim_data["SoC_Percent"].iloc[current_step-1] >= 99.9:
                break

if __name__ == "__main__":
    main()