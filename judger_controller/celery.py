# coding=utf-8
from __future__ import absolute_import
from celery import Celery

app = Celery("judge", broker="redis://localhost:6379/0", include=["judger_controller.tasks"])