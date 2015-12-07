# coding=utf-8
from huey.djhuey import task

from judge_dispatcher.tasks import JudgeDispatcher


@task()
def _judge(submission, time_limit, memory_limit, test_case_id):
    JudgeDispatcher(submission, time_limit, memory_limit, test_case_id).judge()