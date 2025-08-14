import os
import redis

redis_host = os.getenv('REDIS_HOST', 'localhost')
pool = redis.ConnectionPool(host=redis_host, port=6379, db=0)

async def get_redis():
    return redis.Redis(connection_pool=pool)