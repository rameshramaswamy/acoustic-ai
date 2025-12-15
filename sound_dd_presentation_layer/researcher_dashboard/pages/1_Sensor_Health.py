import streamlit as st
import pandas as pd
from common.api_client import APIClient

st.header("📡 IoT Sensor Fleet Status")

# Streamlit Caching
# This prevents fetching data from the API every time a filter is applied.
# ttl=60 ensures data is fresh every minute.
@st.cache_data(ttl=60, show_spinner="Fetching Fleet Telemetry...")
def fetch_fleet_data():
    return APIClient.get_sensor_health()

# Fetch Data (Cached)
df = fetch_fleet_data()

if not df.empty:
    # filters trigger re-run, but fetch_fleet_data() hits cache now.
    status_filter = st.multiselect(
        "Filter Status", 
        ["Online", "Offline"], 
        default=["Online", "Offline"]
    )
    
    filtered_df = df[df["status"].isin(status_filter)]

    def highlight_status(val):
        color = '#ffcccb' if val == 'Offline' else '#90ee90'
        return f'background-color: {color}'

    st.dataframe(
        filtered_df.style.applymap(highlight_status, subset=['status']), 
        use_container_width=True
    )
else:
    st.warning("No sensor data available.")

if st.button("Force Refresh"):
    fetch_fleet_data.clear()
    st.rerun()