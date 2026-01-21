import os
from redis.asyncio import Redis, ConnectionPool
import redis

redis_host = os.getenv('REDIS_HOST', 'localhost')
pool = ConnectionPool(host=redis_host, port=6379, db=0)
sync_pool = redis.ConnectionPool(host=redis_host, port=6379, db=1)

async def get_redis():
    return Redis(connection_pool=pool)

def get_sync_redis():
    return redis.Redis(connection_pool=sync_pool)