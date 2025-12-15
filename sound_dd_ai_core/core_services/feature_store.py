import redis
import pickle
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import settings

class FeatureStore:
    def __init__(self):
        # Connection Pool for Enterprise Scale
        self.pool = redis.ConnectionPool(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            db=0,
            socket_connect_timeout=2
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def _generate_key(self, s3_key):
        return f"feat:{settings.MODEL_VERSION}:{hashlib.md5(s3_key.encode()).hexdigest()}"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def save_spectrogram(self, s3_key: str, spectrogram_tensor):
        """
        Stores Feature Vector with Retry Logic.
        """
        try:
            key = self._generate_key(s3_key)
            data = spectrogram_tensor.cpu().numpy() # Ensure CPU before pickle
            
            # Atomic Pipeline
            pipe = self.client.pipeline()
            pipe.setex(key, settings.FEATURE_TTL_SECONDS, pickle.dumps(data))
            pipe.execute()
        except redis.RedisError as e:
            # Log but don't crash pipeline? 
            # In enterprise, if Feature Store is down, we might want to skip caching but proceed.
            # But here we retry.
            raise e

    def get_spectrogram(self, s3_key: str):
        try:
            key = self._generate_key(s3_key)
            data = self.client.get(key)
            if data:
                return pickle.loads(data)
        except Exception:
            return None
        return None