from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index, text
from geoalchemy2 import Geometry
from ..database import Base

class AudioMetadata(Base):
    __tablename__ = "audio_metadata"

    id = Column(Integer, primary_key=True)
    device_id = Column(String)
    timestamp = Column(DateTime(timezone=True))
    geom = Column(Geometry(geometry_type='POINT', srid=4326))
    class_label = Column(String) 
    confidence = Column(Float)
    s3_key = Column(String)
    location_tag = Column(String)

  
    # Allows fast searching: "Find sounds in 'industrial'"
    __table_args__ = (
        Index(
            'ix_audio_metadata_location_fts',
            text("to_tsvector('english', location_tag)"),
            postgresql_using='gin'
        ),
        # Spatial Index is handled automatically by GeoAlchemy2, but explicit is good
        Index('ix_audio_metadata_geom', 'geom', postgresql_using='gist'),
    )


# We store the definition here to run at startup/migration
MATERIALIZED_VIEW_SQL = """
CREATE MATERIALIZED VIEW IF NOT EXISTS impact_stats_mv AS
SELECT 
    split_part(location_tag, ',', 1) as region, -- Simplified extraction
    class_label,
    EXTRACT(HOUR FROM timestamp) as hour_of_day,
    COUNT(*) as count
FROM audio_metadata
GROUP BY region, class_label, hour_of_day;

CREATE INDEX IF NOT EXISTS ix_impact_stats_region ON impact_stats_mv(region);
"""

REFRESH_VIEW_SQL = "REFRESH MATERIALIZED VIEW CONCURRENTLY impact_stats_mv;"