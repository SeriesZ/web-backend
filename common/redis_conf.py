import os

import aioredis

REDIS_URL = os.getenv("REDIS_URL")


async def get_redis():
    redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    return redis
