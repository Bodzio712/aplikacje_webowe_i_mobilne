import redis

r = redis.Redis()

r.hset('pogodzip:webapp:users', 'admin', 'admin', 'admin')
