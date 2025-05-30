import redis.asyncio as redis
from app.core.config import settings

# Redis 비동기 클라이언트
rdb = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True,  # 문자열 자동 디코딩
)
