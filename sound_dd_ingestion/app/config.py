from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SOUND-DD Ingestion Engine (Ent)"
    
    # Infrastructure
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "us-east-1"
    AWS_BUCKET_NAME: str
    
    # Database
    DATABASE_URL: str

    # Security (NEW)
    # In Prod, these should be injected via Secrets Manager
    IOT_API_KEY: str = "change-me-iot-secret-key"
    RESEARCHER_API_KEY: str = "change-me-researcher-key"
    CORS_ORIGINS: List[str] = ["https://sound-dd.org", "http://localhost:3000"]

    # MQTT
    MQTT_BROKER_URL: str = "localhost"
    MQTT_PORT: int = 1883

    class Config:
        env_file = ".env"

settings = Settings()