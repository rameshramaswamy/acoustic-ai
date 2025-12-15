from fastapi_limiter.depends import RateLimiter
from fastapi import Request, Depends

async def get_user_tier(request: Request):
    """
    Mock logic to determine user tier from API Key.
    In Prod, this checks DB or JWT claims.
    """
    api_key = request.headers.get("x-api-key")
    if api_key == "RESEARCHER_SECRET":
        return "researcher"
    elif api_key == "ADMIN_SECRET":
        return "admin"
    return "public"

async def dynamic_rate_limit(request: Request):
    """
    Returns the limit string based on user tier.
    """
    tier = await get_user_tier(request)
    
    if tier == "admin":
        return "10000/second" # Effectively unlimited
    elif tier == "researcher":
        return "1000/minute"
    else:
        return "20/minute" # Public strict limit

# Specialized Limiter Class
class TieredLimiter:
    def __call__(self, request: Request, response):
        # We wrap the standard RateLimiter but inject dynamic limits
        # Note: fastapi-limiter supports dynamic callback
        return RateLimiter(times=self._get_times, seconds=60)(request, response)
    
    async def _get_times(self, request: Request, response):
        tier = await get_user_tier(request)
        return 1000 if tier == "researcher" else 20