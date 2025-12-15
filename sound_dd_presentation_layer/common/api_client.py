import requests
import pandas as pd
from datetime import datetime, timedelta
import random
from .config import config

class APIClient:
    """
    Adapter to talk to Phase 4 API.
    Includes 'Mock Mode' so the UI can be developed independently.
    """
    
    @staticmethod
    def get_map_clusters(lat, lon, zoom):
        if config.USE_MOCK:
            # Simulate clustered response
            return [
                {"lat": lat + 0.01, "lon": lon + 0.01, "count": 45, "intensity": 0.8, "type": "cluster"},
                {"lat": lat - 0.01, "lon": lon - 0.005, "count": 12, "intensity": 0.2, "type": "cluster"},
                {"lat": lat, "lon": lon, "count": 120, "intensity": 0.9, "type": "cluster"},
            ]
        try:
            resp = requests.get(f"{config.API_BASE_URL}/map/clusters", params={"lat": lat, "lon": lon, "zoom": zoom})
            return resp.json()
        except:
            return []

    @staticmethod
    def get_sensor_health():
        if config.USE_MOCK:
            return pd.DataFrame([
                {"device_id": "SN-001", "status": "Online", "last_ping": "2m ago", "battery": 85},
                {"device_id": "SN-002", "status": "Offline", "last_ping": "4h ago", "battery": 0},
                {"device_id": "SN-003", "status": "Online", "last_ping": "30s ago", "battery": 92},
            ])
        # In prod: Call backend /sensors/health
        return pd.DataFrame()

    @staticmethod
    def get_impact_report(region):
        if config.USE_MOCK:
            return {
                "region": region,
                "distribution": {"Polluting": 650, "Nature": 200, "Human": 150},
                "peak_pollution_hours": {8: 120, 9: 140, 18: 200, 19: 180}
            }
        resp = requests.get(f"{config.API_BASE_URL}/reports/impact", params={"region": region})
        return resp.json()