import os


def get_env(name, default=""):
    return os.environ.get(name, default)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': get_env("POSTGRES_HOST", "postgres"),
        'PORT': get_env("POSTGRES_PORT", "5433"),
        'NAME': get_env("POSTGRES_DB"),
        'USER': get_env("POSTGRES_USER"),
        'PASSWORD': get_env("POSTGRES_PASSWORD")
    }
}

REDIS_CONF = {
    "host": get_env("REDIS_HOST", "redis"),
    "port": get_env("REDIS_PORT", "6379")
}

DEBUG = False

ALLOWED_HOSTS = ['*']

AVATAR_URI_PREFIX = "/static/avatar"
AVATAR_UPLOAD_DIR = "/data/avatar"

UPLOAD_PREFIX = "/static/upload"
UPLOAD_DIR = "/data/upload"

TEST_CASE_DIR = "/data/test_case"
LOG_PATH = "/data/log"
DEFAULT_JUDGE_SERVER_SERVICE_URL = "http://judge-server:8080/"
