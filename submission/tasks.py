from celery import shared_task
from judge.tasks import JudgeDispatcher


@shared_task
def _judge(submission_obj, problem_obj):
    return JudgeDispatcher(submission_obj, problem_obj).judge()
