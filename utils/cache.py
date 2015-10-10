# coding=utf-8
import redis
from django.conf import settings


def get_cache_redis():
    return redis.Redis(host=settings.REDIS_CACHE["host"],
                       port=settings.REDIS_CACHE["port"],
                       db=settings.REDIS_CACHE["db"])