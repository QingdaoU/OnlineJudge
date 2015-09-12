# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 下面是需要自己修改的
LOG_PATH = "/var/log/oj/"

# 注意这是web 服务器访问的地址，判题端访问的地址不一定一样，因为可能不在一台机器上
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "oj",
        'CONN_MAX_AGE': 0.1,
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'mypwd'
    },
    'submission': {
        'NAME': 'oj_submission',
        'ENGINE': 'django.db.backends.mysql',
        'CONN_MAX_AGE': 0.1,
        'HOST': "127.0.0.1",
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'mypwd'
    }
}

REDIS_CACHE = {
    "host": "127.0.0.1",
    "port": 6379,
    "db": 1
}

DEBUG = True

# 同理 这是 web 服务器的上传路径
TEST_CASE_DIR = '/root/test_case/'

ALLOWED_HOSTS = ['*']

IMAGE_UPLOAD_DIR = '/var/mnt/source/OnlineJudge/static/src/upload_image/'
