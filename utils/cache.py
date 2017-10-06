from django.core.cache import cache, caches  # noqa
from django.conf import settings  # noqa

from django_redis.cache import RedisCache
from django_redis.client.default import DefaultClient


class MyRedisClient(DefaultClient):
    def __getattr__(self, item):
        client = self.get_client(write=True)
        return getattr(client, item)

    def redis_incr(self, key, count=1):
        """
        django 默认的 incr 在 key 不存在时候会抛异常
        """
        client = self.get_client(write=True)
        return client.incr(key, count)


class MyRedisCache(RedisCache):
    def __init__(self, server, params):
        super().__init__(server, params)
        self._client_cls = MyRedisClient

    def __getattr__(self, item):
        return getattr(self.client, item)
