# coding=utf-8
from __future__ import absolute_import
from judge.controller.celery import app
import subprocess32 as subprocess

subprocess.call("ping baidu.com", timeout=5)


@app.task
def judge(source_code, language, test_case_id):
    pass