# coding=utf-8
from __future__ import absolute_import
from judge.controller.celery import app


@app.task
def judge(source_code, language, test_case_id):
    print source_code, language, test_case_id