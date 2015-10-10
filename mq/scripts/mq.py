# coding=utf-8
import logging

import redis

from django.db import transaction

from judge.judger_controller.settings import redis_config
from judge.judger.result import result
from submission.models import Submission
from problem.models import Problem
from utils.cache import get_cache_redis
from contest.models import ContestProblem, Contest, ContestSubmission, CONTEST_UNDERWAY, ContestRank
from account.models import User

logger = logging.getLogger("app_info")


class MessageQueue(object):
    def __init__(self):
        self.conn = redis.StrictRedis(host=redis_config["host"], port=redis_config["port"], db=redis_config["db"])
        self.queue = 'queue'

    def listen_task(self):
        while True:
            submission_id = self.conn.blpop(self.queue, 0)[1]
            logger.debug("receive submission_id: " + submission_id)

            try:
                submission = Submission.objects.get(id=submission_id)
            except Submission.DoesNotExist:
                logger.warning("Submission does not exist, submission_id: " + submission_id)
                continue

            # 更新该用户的解题状态用
            try:
                user = User.objects.get(pk=submission.user_id)
            except User.DoesNotExist:
                logger.warning("Submission user does not exist, submission_id: " + submission_id)
                continue

            if not submission.contest_id:
                try:
                    problem = Problem.objects.get(id=submission.problem_id)
                except Problem.DoesNotExist:
                    logger.warning("Submission problem does not exist, submission_id: " + submission_id)
                    continue

                problems_status = user.problems_status

                # 更新普通题目的计数器
                problem.add_submission_number()
                if submission.result == result["accepted"]:
                    problem.add_ac_number()
                    problems_status["problems"][str(problem.id)] = 1
                else:
                    problems_status["problems"][str(problem.id)] = 2
                user.problems_status = problems_status
                user.save()
                # 普通题目的话，到这里就结束了
                continue

            # 能运行到这里的都是比赛题目
            try:
                contest = Contest.objects.get(id=submission.contest_id)
                if contest.status != CONTEST_UNDERWAY:
                    logger.info("Contest debug mode, id: " + str(contest.id) + ", submission id: " + submission_id)
                    continue
                contest_problem = ContestProblem.objects.get(contest=contest, id=submission.problem_id)
            except Contest.DoesNotExist:
                logger.warning("Submission contest does not exist, submission_id: " + submission_id)
                continue
            except ContestProblem.DoesNotExist:
                logger.warning("Submission problem does not exist, submission_id: " + submission_id)
                continue

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
                if submission.result == result["accepted"]:
                    contest_problem.add_ac_number()
                    problems_status["contest_problems"][str(contest_problem.id)] = 1
                else:
                    problems_status["contest_problems"][str(contest_problem.id)] = 1
                user.problems_status = problems_status
                user.save()

logger.debug("Start message queue")
MessageQueue().listen_task()
