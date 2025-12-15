from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NoisePoint(BaseModel):
    id: int
    lat: float
    lon: float
    intensity: float # Derived from classification confidence or sensor db
    label: str
    timestamp: datetime

class SoundscapeTrack(BaseModel):
    url: str
    volume: float
    start_offset: float
    type: str # 'background' or 'event'

class SoundscapeResponse(BaseModel):
    location: str
    theme: str # e.g., "Urban Chaos", "Morning Calm"
    tracks: List[SoundscapeTrack]