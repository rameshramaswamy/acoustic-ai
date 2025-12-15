#!/bin/bash
echo "🚀 Starting SOUND-DD Enterprise Presentation Layer..."

# Start Researcher Dashboard (Streamlit) in background
# --server.address 0.0.0.0 allows external access in Docker
echo "Starting Streamlit on :8501"
streamlit run researcher_dashboard/app.py --server.port 8501 --server.address 0.0.0.0 &

# Start Public Portal (Gunicorn) in foreground
# --workers 4: Handles concurrent traffic (Formula: 2 * CPUs + 1)
# --bind 0.0.0.0:8050: Exposes to outside world
echo "Starting Gunicorn (Dash) on :8050"
gunicorn --workers 4 --threads 2 --bind 0.0.0.0:8050 wsgi:server