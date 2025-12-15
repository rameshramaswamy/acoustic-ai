import streamlit as st
import sys
import os

# Add parent to path to import common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

st.set_page_config(page_title="SOUND-DD | Research Lab", layout="wide")

st.title("🎧 SOUND-DD Researcher Admin")
st.sidebar.success("Select a workspace above.")

st.markdown("""
### Enterprise Acoustic Intelligence Platform
Welcome to the internal control center.
- **Sensor Health**: Monitor IoT fleet status.
- **Label Validation**: Human-in-the-loop ML correction.
""")

# Quick Stats
col1, col2, col3 = st.columns(3)
col1.metric("Active Sensors", "42", "2 Offline")
col2.metric("Hours Recorded", "12,405", "+120 today")
col3.metric("Avg Noise Level (Chennai)", "72 dB", "+5% vs Avg")