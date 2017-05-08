# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "JudgeQueue": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

REDIS_CACHE = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 1
}

REDIS_QUEUE = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 2
}

DEBUG = True

ALLOWED_HOSTS = ["*"]

TEST_CASE_DIR = "/tmp"

LOG_PATH = "log/"
