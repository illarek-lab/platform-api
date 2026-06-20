from redis.asyncio import Redis

from app.projects.c13200175.infra.settings import settings

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
