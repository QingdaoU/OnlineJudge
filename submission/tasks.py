# coding=utf-8
from __future__ import absolute_import
from celery import shared_task
from judge_dispatcher.tasks import JudgeDispatcher


@shared_task
def _judge(submission_id, time_limit, memory_limit, test_case_id, spj=False, spj_language=None, spj_code=None, spj_version=None):
    JudgeDispatcher(submission_id, time_limit, memory_limit, test_case_id, spj, spj_language, spj_code, spj_version).judge()