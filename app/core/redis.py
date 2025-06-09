import redis.asyncio as redis
from app.core.config import settings

rdb = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    decode_responses=True,
)
