from pydantic import BaseModel, Field
from datetime import datetime

class AudioUploadResponse(BaseModel):
    id: int
    filename: str
    status: str
    message: str

class DeviceTelemetry(BaseModel):
    device_id: str
    lat: float
    long: float
    timestamp: datetime = Field(default_factory=datetime.now)