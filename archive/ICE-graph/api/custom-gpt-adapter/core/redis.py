import redis.asyncio as redis
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis_client():
    """
    Dependency to get a Redis client.
    """
    return redis_client 