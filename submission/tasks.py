from celery import shared_task


@shared_task
def _judge(submission_obj, problem_obj):
    pass
