# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 下面是需要自己修改的
LOG_PATH = "LOG/"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'CONN_MAX_AGE': 0.3,
    },
    'mongodb': {
        'HOST': '127.0.0.1',
        'USERNAME': 'root',
        'PASSWORD': 'root',
        'PORT': 27017
    }
}


DEBUG = True

TEST_CASE_DIR = "/var/test_case/"

