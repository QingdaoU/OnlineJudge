# coding=utf-8
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 下面是需要自己修改的
LOG_PATH = "LOG/"

# 注意这是web 服务器访问的地址，判题度武器访问的地址不一定一样，因为可能不在一台机器上
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'CONN_MAX_AGE': 0.3,
    }
}

mongodb_setting = {
    'HOST': '127.0.0.1',
    'USERNAME': 'root',
    'PASSWORD': 'root',
    'PORT': 27017
}

DEBUG = True

# 同理 这是 web 服务器的上传路径
TEST_CASE_DIR = "/Users/virusdefender/Desktop/test_case/"
