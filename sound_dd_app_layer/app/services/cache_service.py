import redis.asyncio as redis
import json
import functools
import Geohash # NEW Library
from ..config import settings

# ... RedisCache class remains same ...

def cached_geo_query(precision=6, ttl_seconds=300):
    """
    OPTIMIZATION: Geohash-based Caching.
     precision=6 is approx 1.2km x 0.6km error margin.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract geospatial args
            lat = kwargs.get('lat') or args[1] # heuristic extraction
            lon = kwargs.get('lon') or args[2]
            
            if lat and lon:
                # Generate Geohash Key (e.g., "query:tf34m")
                geo_key = Geohash.encode(lat, lon, precision=precision)
                # Combine with other args (like zoom level)
                zoom = kwargs.get('zoom_level', 15)
                cache_key = f"{func.__name__}:{geo_key}:z{zoom}"
            else:
                # Fallback to standard key
                cache_key = f"{func.__name__}:{str(kwargs)}"

            # Try Cache
            cached_val = await cache.get_json(cache_key)
            if cached_val:
                return cached_val
            
            # Execute
            result = await func(*args, **kwargs)
            
            # Serialize & Store
            to_cache = result # Assuming result is dict/list, strictly logic needs serialization check
            await cache.set_json(cache_key, to_cache, ttl_seconds)
            return result
        return wrapper
    return decorator