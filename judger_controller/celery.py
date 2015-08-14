# coding=utf-8
from __future__ import absolute_import
from celery import Celery
from .settings import redis_config

app = Celery("judge", broker="redis://" +
                             redis_config["host"] + ":" +
                             str(redis_config["port"]) +
                             "/" + str(redis_config["db"]),
             include=["judger_controller.tasks"])
