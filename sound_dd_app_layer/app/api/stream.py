from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as redis
from ..config import settings
import json
import asyncio

router = APIRouter()

@router.get("/alerts/live")
async def live_noise_alerts(request: Request, region: str = "all"):
    """
   
    Keeps connection open. Pushes data when AI detects anomaly.
    More efficient than Polling.
    """
    async def event_generator():
        # Connect to Redis Pub/Sub
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe("sound_alerts_channel")
        
        try:
            while True:
                # Check for disconnection
                if await request.is_disconnected():
                    break
                
                # Get message (non-blocking wait with small sleep loop)
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                
                if message:
                    data = json.loads(message["data"])
                    # Filter logic: Only send if region matches
                    if region == "all" or region in data.get("location", ""):
                        yield {
                            "event": "noise_spike",
                            "data": json.dumps(data)
                        }
                
                await asyncio.sleep(0.5) # Prevent CPU spin
        finally:
            await pubsub.unsubscribe("sound_alerts_channel")
            await r.close()

    return EventSourceResponse(event_generator())