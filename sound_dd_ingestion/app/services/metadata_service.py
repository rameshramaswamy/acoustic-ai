import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from ..models.sql_models import AudioMetadata
import logging

logger = logging.getLogger("sound_dd.enrichment")

async def enrich_weather_data(upload_id: int, lat: float, lon: float, db: AsyncSession):
    """
    Fetches weather data for the location and updates the DB record asynchronously.
    This runs AFTER the response is sent to the user.
    """
    # Mock Weather API (Open-Meteo is free/open)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m,weather_code"
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json().get("current", {})
                
                # Context string: "Temp: 30C, Wind: 15kmh, Code: 3"
                weather_tag = f"T:{data.get('temperature_2m')} W:{data.get('wind_speed_10m')} C:{data.get('weather_code')}"
                
                # Update DB
                # Note: We need a fresh session for background tasks usually, 
                # but FastAPI dependency injection handles this if passed correctly,
                # or we create a new scope. For simplicity here, we assume session is valid.
                stmt = (
                    update(AudioMetadata)
                    .where(AudioMetadata.id == upload_id)
                    .values(location_tag=weather_tag) # Storing in location_tag for now, or add new column
                )
                await db.execute(stmt)
                await db.commit()
                logger.info(f"✅ Enriched Upload {upload_id} with Weather: {weather_tag}")
            else:
                logger.warning("Weather API failed")
    except Exception as e:
        logger.error(f"Enrichment Error: {e}")