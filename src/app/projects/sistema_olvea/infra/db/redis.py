from redis.asyncio import Redis

from app.projects.sistema_olvea.infra.settings import settings

redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
