import cachetools


cached_data = cachetools.TTLCache(maxsize=1000, ttl=1200)
