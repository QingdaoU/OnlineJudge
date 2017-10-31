# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': '127.0.0.1',
        'PORT': 5433,
        'NAME': "onlinejudge",
        'USER': "onlinejudge",
        'PASSWORD': 'onlinejudge'
    }
}

REDIS_CONF = {
    "host": "127.0.0.1",
    "port": "6379"
}


DEBUG = True

ALLOWED_HOSTS = ["*"]

TEST_CASE_DIR = "/tmp"

LOG_PATH = f"{BASE_DIR}/log/"

AVATAR_URI_PREFIX = "/static/avatar"
AVATAR_UPLOAD_DIR = f"{BASE_DIR}{AVATAR_URI_PREFIX}"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
