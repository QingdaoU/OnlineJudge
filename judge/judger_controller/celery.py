# coding=utf-8
from __future__ import absolute_import
from celery import Celery, platforms
from .settings import redis_config

app = Celery("judge", broker='redis://%s:%s/%s' % (redis_config["host"], redis_config["port"], redis_config["db"]),
             include=["judge.judger_controller.tasks"])
			 
platforms.C_FORCE_ROOT =True
