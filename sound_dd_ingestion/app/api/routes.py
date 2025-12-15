from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi_limiter.depends import RateLimiter # OPTIMIZATION
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from ..database import get_db
from ..models.sql_models import AudioMetadata
from ..models.pydantic_schemas import UploadRequest, UploadResponse, UploadConfirmation
from ..services.storage_service import StorageService
from ..core.security import verify_api_key
from ..services.metadata_service import enrich_weather_data

router = APIRouter()
storage = StorageService()

# --- Schemas ---
class UploadRequest(BaseModel):
    device_id: str
    file_type: str = "audio/wav" # or audio/flac

class UploadRequest(BaseModel):
    device_id: str
    file_type: str = "audio/wav"
    md5_checksum: Optional[str] = None
    
class UploadConfirmation(BaseModel):
    upload_id: str
    device_id: str
    latitude: float
    longitude: float
    location_tag: Optional[str] = None
    file_size_bytes: int

# --- Endpoints ---

@router.post(
    "/upload/request", 
    response_model=UploadResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))] # OPTIMIZATION: Limit to 10 req/min
)
async def request_upload_url(
    req: UploadRequest, 
    api_key: str = Depends(verify_api_key) # Security Check
):
    """
    Step 1: Client requests permission to upload.
    Server returns a direct S3 link (Presigned URL).
    """
    if req.file_type not in ["audio/wav", "audio/x-wav", "audio/flac"]:
        raise HTTPException(status_code=400, detail="Unsupported MIME type")

    try:
        presigned_data = await storage.generate_presigned_post(req.device_id, req.file_type)
        return UploadResponse(
            upload_url=presigned_data["url"],
            fields=presigned_data["fields"],
            upload_id=presigned_data["key"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Infrastructure Error")

@router.post("/upload/confirm")
async def confirm_upload(
    conf: UploadConfirmation, 
    db: AsyncSession = Depends(get_db), # Async Session
    api_key: str = Depends(verify_api_key)
):
    # 1. Verification
    # Note: s3_client is still sync, but it's fast. 
    # For extreme scale, use 'aioboto3', but 'boto3' is thread-safe enough for now.
    if not await storage.check_file_exists(conf.upload_id):
        raise HTTPException(status_code=404, detail="File not found in S3")

    # 2. Async Idempotency Check
    query = select(AudioMetadata).where(AudioMetadata.s3_key == conf.upload_id)
    result = await db.execute(query)
    existing = result.scalar_one_or_none()
    
    if existing:
        return {"status": "already_exists", "id": existing.id}

    # 3. Persistence with Geospatial Data
    # Create Point geometry: POINT(long lat)
    # WKT Element: f'POINT({conf.longitude} {conf.latitude})'
    
    db_record = AudioMetadata(
        device_id=conf.device_id,
        latitude=conf.latitude,
        longitude=conf.longitude,
        # OPTIMIZATION: Insert directly into PostGIS Geometry column
        geom=f'SRID=4326;POINT({conf.longitude} {conf.latitude})',
        location_tag=conf.location_tag,
        s3_key=conf.upload_id,
        file_size_bytes=conf.file_size_bytes,
        format="wav" if "wav" in conf.upload_id else "flac"
    )
    
    try:
        db.add(db_record)
        await db.commit() # Async Commit
        await db.refresh(db_record)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    return {"status": "success", "id": db_record.id}