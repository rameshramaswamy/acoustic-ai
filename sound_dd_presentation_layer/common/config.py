import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")
    USE_MOCK = os.getenv("USE_MOCK", "False").lower() == "true"
    
    # OPTIMIZATION: Redis Config for UI Caching
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1") # DB 1 for UI

config = Config()