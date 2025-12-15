import boto3
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models.sql_models import AudioMetadata
from ..models.schemas import SoundscapeTrack, SoundscapeResponse
from ..config import settings
import random

class SoundscapeComposer:
    def __init__(self):
        self.s3_client = boto3.client('s3', region_name=settings.AWS_REGION)

    def _generate_presigned_url(self, s3_key: str) -> str:
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=3600
        )

    async def compose_dynamic_soundscape(
        self, db: AsyncSession, location_tag: str, theme: str
    ) -> SoundscapeResponse:
        """
        Algorithm:
        1. Base Layer: Fetch 1 long 'Background' loop (e.g., wind, distant hum).
        2. Event Layer: Fetch 3-5 distinct 'Events' (birds, horns) based on theme.
        3. Mixing: Assign volumes and start times.
        """
        tracks = []
        
        # 1. Background (simulated logic)
        # In real DB, we would have a 'type' column. Here we assume 'Non-Polluting' is bg-ish.
        bg_stmt = select(AudioMetadata).where(
            AudioMetadata.location_tag.contains(location_tag),
            AudioMetadata.class_label == "Non-Polluting"
        ).order_by(func.random()).limit(1)
        
        bg_res = await db.execute(bg_stmt)
        bg_track = bg_res.scalar_one_or_none()
        
        if bg_track:
            tracks.append(SoundscapeTrack(
                url=self._generate_presigned_url(bg_track.s3_key),
                volume=0.4,
                start_offset=0.0,
                type="background_loop"
            ))

        # 2. Foreground Events
        # If theme is 'Chaos', get Polluting sounds.
        target_label = "Polluting" if theme == "Urban Chaos" else "Non-Polluting"
        
        evt_stmt = select(AudioMetadata).where(
            AudioMetadata.location_tag.contains(location_tag),
            AudioMetadata.class_label == target_label
        ).order_by(func.random()).limit(4)
        
        evt_res = await db.execute(evt_stmt)
        
        for i, row in enumerate(evt_res.scalars()):
            tracks.append(SoundscapeTrack(
                url=self._generate_presigned_url(row.s3_key),
                volume=0.8,
                # Stagger the start times for a "Natural" feel
                start_offset=random.uniform(0.5, 5.0) + (i * 2),
                type="event_one_shot"
            ))

        return SoundscapeResponse(
            location=location_tag,
            theme=theme,
            tracks=tracks
        )