from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, literal_column
from ..models.sql_models import AudioMetadata
from ..models.schemas import NoisePoint, ImpactReport
from typing import List, Dict

class GeospatialService:
    @staticmethod
    async def get_clustered_noise_map(
        db: AsyncSession, 
        min_lat: float, max_lat: float, 
        min_lon: float, max_lon: float, 
        zoom_level: int
    ) -> List[Dict]:
        """
        OPTIMIZATION: Server-Side Clustering.
        Instead of sending 10k points, we snap points to a grid based on zoom level.
        Returns: {lat, lon, count, avg_intensity}
        """
        # Dynamic Grid Size based on Map Zoom (Approximate degrees)
        # Zoom 10 ~ 0.1 deg, Zoom 18 ~ 0.0001 deg
        grid_size = 0.0005 if zoom_level > 15 else 0.01

        # PostGIS ST_SnapToGrid groups nearby points
        stmt = (
            select(
                func.ST_Y(func.ST_SnapToGrid(AudioMetadata.geom, grid_size)).label("bucket_lat"),
                func.ST_X(func.ST_SnapToGrid(AudioMetadata.geom, grid_size)).label("bucket_lon"),
                func.count().label("point_count"),
                func.avg(AudioMetadata.confidence).label("avg_intensity")
            )
            .where(
                # Bounding Box Filter (Viewport)
                func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326).ST_Contains(AudioMetadata.geom)
            )
            .group_by("bucket_lat", "bucket_lon")
        )

        result = await db.execute(stmt)
        clusters = []
        for row in result:
            clusters.append({
                "lat": row.bucket_lat,
                "lon": row.bucket_lon,
                "count": row.point_count,
                "intensity": row.avg_intensity,
                "type": "cluster"
            })
        return clusters

    @staticmethod
    async def generate_impact_report_optimized(db: AsyncSession, location_tag: str) -> Dict:
        """
        Speed: ~5ms (vs 2s on raw table).
        """
        # We query the pre-aggregated view
        # Note: We use string matching on the region column of the view
        stmt = text("""
            SELECT class_label, hour_of_day, count 
            FROM impact_stats_mv 
            WHERE region ILIKE :loc
        """)
        
        result = await db.execute(stmt, {"loc": f"%{location_tag}%"})
        rows = result.fetchall()

        if not rows:
            return {"region": location_tag, "status": "no_data"}

        # Process Aggregates in Python (CPU bound, fast)
        distribution = {}
        peak_hours = {}

        for row in rows:
            # Row: (class_label, hour, count)
            lbl, hr, cnt = row[0], int(row[1]), row[2]
            
            # Sum for distribution
            distribution[lbl] = distribution.get(lbl, 0) + cnt
            
            # Sum for Peak Hours (if Polluting)
            if lbl == 'Polluting':
                peak_hours[hr] = peak_hours.get(hr, 0) + cnt

        return {
            "region": location_tag,
            "source": "materialized_view", # Debug info
            "distribution": distribution,
            "peak_pollution_hours": peak_hours
        }

    @staticmethod
    async def search_locations(db: AsyncSession, query: str) -> List[str]:
        """
        OPTIMIZATION 2: Full Text Search.
        """
        # Using plainto_tsquery for natural language search
        stmt = text("""
            SELECT DISTINCT location_tag 
            FROM audio_metadata 
            WHERE to_tsvector('english', location_tag) @@ plainto_tsquery('english', :q)
            LIMIT 10
        """)
        result = await db.execute(stmt, {"q": query})
        return [row[0] for row in result]