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
    },
    'submission': {
        'NAME': 'oj_submission',
        'ENGINE': 'django.db.backends.mysql',
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

# 在 debug 关闭的情况下，静态文件不是有 django runserver 来处理的，应该由 nginx 返回
# 在 debug 开启的情况下，django 会在下面两个文件夹中寻找对应的静态文件。
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/release/")]

# 模板文件夹
OJ_TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'template/release/')]


