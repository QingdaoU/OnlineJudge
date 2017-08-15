from __future__ import absolute_import, unicode_literals
from celery import shared_task
from judge.dispatcher import JudgeDispatcher


@shared_task
def judge_task(submission_id, problem_id):
    JudgeDispatcher(submission_id, problem_id).judge()
