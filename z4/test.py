import redis
r = redis.Redis()
id = 'foo'
r.hset('pogodzip:login:foo', 'login', 'pogodzip')
x=r.hget('pogodzip:login:admin', 'login')
print(x)
