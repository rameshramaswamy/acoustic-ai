import strawberry
from typing import List, Optional
from sqlalchemy.future import select
from sqlalchemy import desc
from ..database import AsyncSessionLocal
from ..models.sql_models import AudioMetadata

@strawberry.type
class AudioEventType:
    id: int
    timestamp: str
    class_label: str
    confidence: float
    location_tag: str
    
    # Computed Field: URL generation logic moved here
    @strawberry.field
    def audio_url(self) -> str:
        # In prod, generate presigned URL here
        return f"https://s3.amazonaws.com/bucket/{self.s3_key_placeholder}"

    # Private mapping
    s3_key_placeholder: strawberry.Private[str]

@strawberry.type
class Query:
    @strawberry.field
    async def events(
        self, 
        limit: int = 10, 
        region: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[AudioEventType]:
        """
        Flexible Query: "Get top 10 events in Mylapore with confidence > 0.8"
        """
        async with AsyncSessionLocal() as session:
            stmt = select(AudioMetadata).order_by(desc(AudioMetadata.timestamp))
            
            if region:
                stmt = stmt.where(AudioMetadata.location_tag.ilike(f"%{region}%"))
            
            stmt = stmt.where(AudioMetadata.confidence >= min_confidence)
            stmt = stmt.limit(limit)
            
            result = await session.execute(stmt)
            rows = result.scalars().all()
            
            return [
                AudioEventType(
                    id=r.id,
                    timestamp=str(r.timestamp),
                    class_label=r.class_label,
                    confidence=r.confidence,
                    location_tag=r.location_tag,
                    s3_key_placeholder=r.s3_key
                )
                for r in rows
            ]

schema = strawberry.Schema(query=Query)