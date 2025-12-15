from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, text
from sqlalchemy.sql import func
from geoalchemy2 import Geometry # OPTIMIZATION: PostGIS Native
from ..database import Base

class AudioMetadata(Base):
    __tablename__ = "audio_metadata"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # OPTIMIZATION: Store as Spatial Point (SRID 4326 = WGS84/GPS)
    # This enables queries like "SELECT * FROM audio WHERE ST_DWithin(geom, point, 500)"
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    
    # Keep floats for simple API responses if needed, or extract from geom
    latitude = Column(Float, nullable=True) 
    longitude = Column(Float, nullable=True)
    
    location_tag = Column(String, nullable=True)
    s3_key = Column(String, unique=True, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    format = Column(String, default="wav")
    is_processed = Column(Boolean, default=False)