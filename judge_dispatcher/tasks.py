# coding=utf-8
import json
import logging

from django.db import transaction

from celery import shared_task
from rpc_client import TimeoutServerProxy

from judge.result import result
from contest.models import ContestProblem, ContestRank, Contest, CONTEST_UNDERWAY
from problem.models import Problem
from submission.models import Submission
from account.models import User
from utils.cache import get_cache_redis

logger = logging.getLogger("app_info")


@shared_task
def create_judge_task(submission_id, code, language_code, time_limit, memory_limit, test_case_id):
    submission = Submission.objects.get(id=submission_id)
    try:
        s = TimeoutServerProxy('http://121.42.198.156:8080', timeout=20)
        data = s.run(submission_id, language_code, code, time_limit, memory_limit, test_case_id)
        # 编译错误
        if data["code"] == 1:
            submission.result = result["compile_error"]
            submission.info = data["data"]["error"]
        # system error
        elif data["code"] == 2:
            submission.result = result["system_error"]
            submission.info = data["data"]["error"]
        elif data["code"] == 0:
            submission.result = data["data"]["result"]
            submission.info = json.dumps(data["data"]["info"])
            submission.accepted_answer_time = data["data"]["accepted_answer_time"]
    except Exception as e:
        submission.result = result["system_error"]
        submission.info = str(e)
    finally:
        submission.save()

    # 更新该用户的解题状态用
    try:
        user = User.objects.get(pk=submission.user_id)
    except User.DoesNotExist:
        logger.warning("Submission user does not exist, submission_id: " + submission_id)
        return

    if not submission.contest_id:
        try:
            problem = Problem.objects.get(id=submission.problem_id)
        except Problem.DoesNotExist:
            logger.warning("Submission problem does not exist, submission_id: " + submission_id)
            return

        problems_status = user.problems_status

        # 更新普通题目的计数器
        problem.add_submission_number()
        if "problems" not in problems_status:
            problems_status["problems"] = {}
        if submission.result == result["accepted"]:
            problem.add_ac_number()
            problems_status["problems"][str(problem.id)] = 1
        else:
            problems_status["problems"][str(problem.id)] = 2
        user.problems_status = problems_status
        user.save()
        # 普通题目的话，到这里就结束了
        return

    # 能运行到这里的都是比赛题目
    try:
        contest = Contest.objects.get(id=submission.contest_id)
        if contest.status != CONTEST_UNDERWAY:
            logger.info("Contest debug mode, id: " + str(contest.id) + ", submission id: " + submission_id)
            return
        contest_problem = ContestProblem.objects.get(contest=contest, id=submission.problem_id)
    except Contest.DoesNotExist:
        logger.warning("Submission contest does not exist, submission_id: " + submission_id)
        return
    except ContestProblem.DoesNotExist:
        logger.warning("Submission problem does not exist, submission_id: " + submission_id)
        return

    # 如果比赛现在不是封榜状态，删除比赛的排名缓存
    if contest.real_time_rank:
        get_cache_redis().delete(str(contest.id) + "_rank_cache")

    with transaction.atomic():
        try:
            contest_rank = ContestRank.objects.get(contest=contest, user=user)
            contest_rank.update_rank(submission)
        except ContestRank.DoesNotExist:
            ContestRank.objects.create(contest=contest, user=user).update_rank(submission)

        problems_status = user.problems_status

        contest_problem.add_submission_number()
        if "contest_problems" not in problems_status:
            problems_status["contest_problems"] = {}
        if submission.result == result["accepted"]:
            contest_problem.add_ac_number()
            problems_status["contest_problems"][str(contest_problem.id)] = 1
        else:
            problems_status["contest_problems"][str(contest_problem.id)] = 0
        user.problems_status = problems_status
        user.save()
