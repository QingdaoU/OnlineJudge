# coding=utf-8
import socket
import redis

from .rpc_client import TimeoutServerProxy
from .settings import redis_config
from .models import JudgeServer


class JudgeDispatcher(object):
    def __init__(self):
        self.redis = redis.StrictRedis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])

    def judge(self):
        pass

