import os


def get_env(name, default=""):
    return os.environ.get(name, default)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': get_env("POSTGRESQL_HOST", "postgresql"),
        'PORT': get_env("POSTGRESQL_PORT", "5433"),
        'NAME': get_env("POSTGRESQL_DBNAME"),
        'USER': get_env("POSTGRESQL_USER"),
        'PASSWORD': get_env("POSTGRESQL_PASSWORD")
    }
}

REDIS_CONF = {
    "host": get_env("REDIS_HOST", "redis"),
    "port": get_env("REDIS_PORT", "6379")
}

DEBUG = False

ALLOWED_HOSTS = ['*']

TEST_CASE_DIR = "/test_case"
