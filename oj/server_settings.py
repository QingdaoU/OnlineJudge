# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 注意这是web 服务器访问的地址，判题端访问的地址不一定一样，因为可能不在一台机器上
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "oj",
        'CONN_MAX_AGE': 0.1,
        'HOST': os.environ.get("MYSQL_PORT_3306_TCP_ADDR", "127.0.0.1"),
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': os.environ.get("MYSQL_ENV_MYSQL_ROOT_PASSWORD", "root")
    },
    'submission': {
        'NAME': 'oj_submission',
        'ENGINE': 'django.db.backends.mysql',
        'CONN_MAX_AGE': 0.1,
        'HOST': os.environ.get("MYSQL_PORT_3306_TCP_ADDR", "127.0.0.1"),
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': os.environ.get("MYSQL_ENV_MYSQL_ROOT_PASSWORD", "root")
    }
}

REDIS_CACHE = {
    "host": os.environ.get("REDIS_PORT_6379_TCP_ADDR", "127.0.0.1"),
    "port": 6379,
    "db": 1
}

REDIS_QUEUE = {
    "host": os.environ.get("REDIS_PORT_6379_TCP_ADDR", "127.0.0.1"),
    "port": 6379,
    "db": 2
}


DEBUG = False

ALLOWED_HOSTS = ['*']

# 在 debug 关闭的情况下，静态文件不是有 django runserver 来处理的，应该由 nginx 返回
# 在 debug 开启的情况下，django 会在下面两个文件夹中寻找对应的静态文件。
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static/release/"), os.path.join(BASE_DIR, "static/release/")]

# 模板文件夹
TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'template/release/')]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SSO = {"callback": "https://discuss.acmer.site/login"}
