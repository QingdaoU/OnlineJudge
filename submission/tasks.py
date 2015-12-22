# coding=utf-8
from __future__ import absolute_import
from celery import shared_task
from judge_dispatcher.tasks import JudgeDispatcher


@shared_task
def _judge(submission, time_limit, memory_limit, test_case_id):
    JudgeDispatcher(submission, time_limit, memory_limit, test_case_id).judge()