from locust import HttpUser, task, between, events
import random
import os

# Dummy WAV header for realistic payload
WAV_HEADER = b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00' + (b'\x00' * 1024)

class IoTSensorUser(HttpUser):
    """Simulates an IoT Device uploading audio every 30-60 seconds."""
    wait_time = between(30, 60)
    
    def on_start(self):
        # Assign a fake device ID
        self.device_id = f"LOCUST_SENSOR_{random.randint(1000, 9999)}"
        self.api_key = "change-me-iot-secret-key"

    @task
    def upload_audio(self):
        # 1. Request Upload URL
        headers = {"x-api-key": self.api_key}
        payload = {"device_id": self.device_id, "file_type": "audio/wav"}
        
        with self.client.post("/api/v1/upload/request", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Req Failed: {response.text}")
                return
            
            data = response.json()
            upload_url = data["upload_url"]
            upload_id = data["upload_id"]
            fields = data["fields"]

        # 2. Upload to S3 (Simulated directly if URL is external, or via proxy)
        # For load test, we might skip the actual S3 put if we want to test API capacity, 
        # but let's assume we confirm immediately to test DB writes.
        
        # 3. Confirm Upload
        confirm_payload = {
            "upload_id": upload_id,
            "device_id": self.device_id,
            "latitude": 13.08 + random.uniform(-0.1, 0.1),
            "longitude": 80.27 + random.uniform(-0.1, 0.1),
            "file_size_bytes": 1024
        }
        
        self.client.post("/api/v1/upload/confirm", json=confirm_payload, headers=headers)

class PublicDashboardUser(HttpUser):
    """Simulates a public user browsing the heatmap."""
    wait_time = between(5, 15)

    @task(3)
    def view_heatmap(self):
        # Fetch clusters
        self.client.get(
            "/api/v1/map/clusters", 
            params={"lat": 13.08, "lon": 80.27, "zoom": 12}
        )

    @task(1)
    def view_report(self):
        # Check impact report
        self.client.get("/api/v1/reports/impact", params={"region": "T. Nagar"})