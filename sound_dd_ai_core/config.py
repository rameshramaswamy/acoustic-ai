from pydantic_settings import BaseSettings
from typing import Optional

class AISettings(BaseSettings):
    # App Info
    APP_NAME: str = "SoundDD-AI-Core"
    ENV: str = "prod"
    
    # Model Config
    MODEL_NAME: str = "NewCNNLeaf"
    MODEL_VERSION: str = "v1.2.0"
    CONFIDENCE_THRESHOLD: float = 0.6
    
    # Hardware
    FORCE_CPU: bool = False
    
    # Infrastructure
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    MLFLOW_TRACKING_URI: str = "http://mlflow:5000"
    
    # Feature Store
    FEATURE_TTL_SECONDS: int = 604800 # 1 week

    class Config:
        env_file = ".env"

settings = AISettings()