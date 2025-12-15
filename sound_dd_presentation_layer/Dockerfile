FROM python:3.10-slim

WORKDIR /app

# Install Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Source Code
COPY . .

# Environment Variables
ENV API_BASE_URL="http://sound-dd-api:8000/api/v1"
ENV PYTHONUNBUFFERED=1

# Expose Ports
# 8050: Public Portal (Dash/Gunicorn)
# 8501: Researcher Dashboard (Streamlit)
EXPOSE 8050 8501

# Copy & Permission Entrypoint
COPY run_all.sh .
RUN chmod +x run_all.sh

# OPTIMIZATION 1: Production Run Command
# run_all.sh handles starting Gunicorn and Streamlit
CMD ["./run_all.sh"]