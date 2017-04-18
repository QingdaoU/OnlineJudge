# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "oj",
        'CONN_MAX_AGE': 0.1,
        'HOST': os.environ["MYSQL_PORT_3306_TCP_ADDR"],
        'PORT': 3306,
        'USER': os.environ["MYSQL_ENV_MYSQL_USER"],
        'PASSWORD': os.environ["MYSQL_ENV_MYSQL_ROOT_PASSWORD"]
    }
}

REDIS_CACHE = {
    "host": os.environ["REDIS_PORT_6379_TCP_ADDR"],
    "port": 6379,
    "db": 1
}

REDIS_QUEUE = {
    "host": os.environ["REDIS_PORT_6379_TCP_ADDR"],
    "port": 6379,
    "db": 2
}

DEBUG = False

ALLOWED_HOSTS = ['*']


TEST_CASE_DIR = "/test_case"

LOG_PATH = "log/"
