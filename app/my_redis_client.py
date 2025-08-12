import os
import redis

redis_host = os.getenv('REDIS_HOST', 'localhost')
pool = redis.ConnectionPool(host=redis_host, port=6379, db=0)
r = redis.Redis(connection_pool=pool)