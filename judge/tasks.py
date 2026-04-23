import dramatiq

from account.models import User
from submission.models import Submission, CodeRun
from judge.dispatcher import JudgeDispatcher
from utils.shortcuts import DRAMATIQ_WORKER_ARGS


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS())
def judge_task(submission_id, problem_id):
    uid = Submission.objects.get(id=submission_id).user_id
    if User.objects.get(id=uid).is_disabled:
        return
    JudgeDispatcher(submission_id, problem_id).judge()


@dramatiq.actor(**DRAMATIQ_WORKER_ARGS())
def code_run_task(code_run_id):
    """自由代码运行任务，直接调用判题服务器执行代码并返回输出"""
    from judge.code_runner import CodeRunner
    code_run = CodeRun.objects.get(id=code_run_id)
    runner = CodeRunner(code_run)
    runner.run()
