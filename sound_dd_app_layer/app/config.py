from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SOUND-DD Query API"
    API_V1_STR: str = "/api/v1"
    
    # Infrastructure
    DATABASE_URL: str
    REDIS_URL: str
    AWS_REGION: str = "us-east-1"
    AWS_BUCKET_NAME: str
    
    # Cache Config
    CACHE_TTL_SECONDS: int = 300  # 5 Minutes

    class Config:
        env_file = ".env"

settings = Settings()