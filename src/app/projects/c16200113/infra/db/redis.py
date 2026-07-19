from redis.asyncio import Redis

from app.projects.c16200113.infra.settings import settings

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

