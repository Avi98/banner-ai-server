from redis import Redis

from config.env_variables import get_settings


settings = get_settings()

redis_client: Redis = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)
