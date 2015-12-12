# coding=utf-8
from huey.djhuey import db_task

from judge_dispatcher.tasks import JudgeDispatcher


@db_task()
def _judge(submission, time_limit, memory_limit, test_case_id, is_waiting_task=False):
    JudgeDispatcher(submission, time_limit, memory_limit, test_case_id).judge(is_waiting_task)