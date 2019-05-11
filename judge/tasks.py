import dramatiq

from account.models import User
from submission.models import Submission
from judge.dispatcher import JudgeDispatcher
from judge.ide import IDEDispatcher
from utils.shortcuts import DRAMATIQ_WORKER_ARGS


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS())
def judge_task(submission_id, problem_id):
    uid = Submission.objects.get(id=submission_id).user_id
    if User.objects.get(id=uid).is_disabled:
        return
    JudgeDispatcher(submission_id, problem_id).judge()


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS())
def judge_IDE_task(src, language, test_case):
    return IDEDispatcher(src, language, test_case).judge()
