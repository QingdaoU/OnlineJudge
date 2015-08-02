# coding=utf-8
import os

LOG_PATH = "LOG/"

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'CONN_MAX_AGE': 1,
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True