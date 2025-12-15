import paho.mqtt.client as mqtt
import requests
import json
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("IoT-Worker")

# Config
BROKER = "localhost"
API_BASE = "http://localhost:8000/api/v1"
API_KEY = "change-me-iot-secret-key"

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def upload_to_cloud_via_presigned(device_id, payload, audio_bytes):
    """
    Orchestrates the 2-step enterprise upload flow.
    1. Request S3 URL
    2. Upload Direct to S3
    3. Confirm Metadata
    """
    headers = {"x-api-key": API_KEY}

    # Step 1: Get URL
    req_data = {"device_id": device_id, "file_type": "audio/wav"}
    r1 = requests.post(f"{API_BASE}/upload/request", json=req_data, headers=headers)
    r1.raise_for_status()
    data = r1.json()
    
    upload_url = data['upload_url']
    s3_fields = data['fields']
    upload_id = data['upload_id']

    # Step 2: Direct Upload (Using multipart form with S3 fields)
    files = {'file': ('audio.wav', audio_bytes)}
    r2 = requests.post(upload_url, data=s3_fields, files=files)
    if r2.status_code not in [200, 204]:
        raise Exception(f"S3 Upload Failed: {r2.text}")

    # Step 3: Confirm
    conf_data = {
        "upload_id": upload_id,
        "device_id": device_id,
        "latitude": payload.get("lat", 0.0),
        "longitude": payload.get("long", 0.0),
        "file_size_bytes": len(audio_bytes)
    }
    r3 = requests.post(f"{API_BASE}/upload/confirm", json=conf_data, headers=headers)
    r3.raise_for_status()
    
    logger.info(f"✅ Upload Complete for {device_id}")

def on_message(client, userdata, msg):
    try:
        topic_parts = msg.topic.split("/")
        device_id = topic_parts[2]
        
        # Assumption: Metadata is in the topic or a separate coordination channel
        # For simplicity, we hardcode metadata, but in Prod, sensors send JSON+Binary
        dummy_meta = {"lat": 13.08, "long": 80.27}
        
        logger.info(f"Processing {len(msg.payload)} bytes from {device_id}")
        
        upload_to_cloud_via_presigned(device_id, dummy_meta, msg.payload)

    except Exception as e:
        logger.error(f"Processing Failed: {e}")

def run_worker():
    client = mqtt.Client()
    client.on_message = on_message
    
    while True:
        try:
            client.connect(BROKER, 1883, 60)
            client.subscribe("chennai/sensors/+/audio")
            logger.info("📡 Worker Connected & Listening")
            client.loop_forever()
        except Exception as e:
            logger.error(f"Connection lost: {e}. Retrying in 5s...")
            time.sleep(5)

if __name__ == "__main__":
    run_worker()