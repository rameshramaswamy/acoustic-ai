from fastapi import Header, HTTPException, status
from ..config import settings

async def verify_api_key(x_api_key: str = Header(...)):
    """
    Validates API Key for IoT/Mobile clients.
    Simple but effective for machine-to-machine auth.
    """
    valid_keys = [settings.IOT_API_KEY, settings.RESEARCHER_API_KEY]
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    return x_api_key