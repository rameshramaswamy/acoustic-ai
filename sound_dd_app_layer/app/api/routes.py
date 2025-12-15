from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..database import get_db
from ..models.schemas import NoisePoint, SoundscapeResponse
from ..services.geospatial_service import GeospatialService
from ..services.synthesis_service import SoundscapeComposer
from ..services.cache_service import cached_query
from ..core.throttling import get_user_tier
router = APIRouter()
composer = SoundscapeComposer()

@router.get("/noise-map", response_model=List[NoisePoint])
@cached_query(ttl_seconds=120) # Cache heavy geo-queries for 2 mins
async def get_noise_map(
    lat: float, 
    lon: float, 
    radius: int = Query(500, description="Radius in meters"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns heatmap data points. 
    Cached to prevent DB overload during high traffic.
    """
    return await GeospatialService.get_noise_map(db, lat, lon, radius)

@router.get("/soundscape/compose", response_model=SoundscapeResponse)
async def compose_soundscape(
    location: str = Query(..., description="e.g. T. Nagar"),
    theme: str = Query("Standard", enum=["Standard", "Urban Chaos", "Nature Retreat"]),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates a dynamic audio composition recipe.
    The frontend uses this JSON to layer audio tracks.
    """
    return await composer.compose_dynamic_soundscape(db, location, theme)

# 1. OPTIMIZED MAP ENDPOINT (Clustered)
@router.get("/map/clusters")
@cached_geo_query(precision=5) # Cache bucketed by ~5km regions
async def get_map_clusters(
    lat: float, 
    lon: float, 
    zoom: int = Query(12, ge=1, le=20),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns aggregated clusters for the viewport.
    Performance: Fast (Server-side aggregation + Geohash Cache).
    """
    # Calculate simple bounding box based on lat/lon + zoom (Simulated)
    delta = 0.1 # Approx 10km view
    return await GeospatialService.get_clustered_noise_map(
        db, 
        min_lat=lat - delta, max_lat=lat + delta,
        min_lon=lon - delta, max_lon=lon + delta,
        zoom_level=zoom
    )

@router.get("/reports/impact")
async def get_impact_report(
    region: str = Query(..., min_length=3),
    db: AsyncSession = Depends(get_db),
    user_tier: str = Depends(get_user_tier) 
):
    # Logic: Maybe hide detailed stats for 'public' tier?
    report = await GeospatialService.generate_impact_report_optimized(db, region)
    
    if user_tier == "public":
        # Redact raw data, only show summaries
        del report["peak_pollution_hours"]
        
    return report

@router.get("/locations/search")
async def search_locations(
    q: str = Query(..., min_length=3),
    db: AsyncSession = Depends(get_db)
):
    """
    New Endpoint: Fast Location Autocomplete using FTS
    """
    return await GeospatialService.search_locations(db, q)


@router.get("/health")
def health():
    return {"status": "operational", "phase": "4 - Application Layer"}