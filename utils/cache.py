from django.conf import settings
from django_redis import get_redis_connection

judge_cache = get_redis_connection(settings.CACHE_JUDGE_QUEUE)
throttling_cache = get_redis_connection(settings.CACHE_THROTTLING)
default_cache = get_redis_connection("default")
