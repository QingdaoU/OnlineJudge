# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    # submission 的 name 和 engine 请勿修改，其他代码会用到
    'submission': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db1.sqlite3'),
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

ALLOWED_HOSTS = []

# 在 debug 关闭的情况下，静态文件不是有 django runserver 来处理的，应该由 nginx 返回
# 在 debug 开启的情况下，django 会在下面两个文件夹中寻找对应的静态文件。
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/src/"), BASE_DIR]

# 模板文件夹
OJ_TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'template/src/')]

