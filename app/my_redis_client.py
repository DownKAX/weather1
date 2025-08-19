import os
from redis.asyncio import Redis, ConnectionPool

redis_host = os.getenv('REDIS_HOST', 'localhost')
pool = ConnectionPool(host=redis_host, port=6379, db=0)

async def get_redis():
    return Redis(connection_pool=pool)