# coding=utf-8
import logging

import redis
import json

from django.db import transaction

from judge.judger_controller.settings import redis_config
from judge.judger.result import result
from submission.models import Submission
from problem.models import Problem
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

            # 更新该用户的解题状态
            try:
                user = User.objects.get(pk=submission.user_id)
            except User.DoesNotExist:
                logger.warning("Submission user does not exist, submission_id: " + submission_id)
                continue

            if not submission.contest_id:
                # 更新普通题目的 ac 计数器
                if submission.result == result["accepted"]:
                    try:
                        problem = Problem.objects.get(id=submission.problem_id)
                        problem.total_accepted_number += 1
                        problem.save()
                    except Problem.DoesNotExist:
                        logger.warning("Submission problem does not exist, submission_id: " + submission_id)
                        continue

                    problems_status = user.problems_status
                    problems_status["problems"][str(problem.id)] = 1
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

            with transaction.atomic():
                try:
                    contest_rank = ContestRank.objects.get(contest=contest, user=user)
                    contest_rank.update_rank(submission)
                except ContestRank.DoesNotExist:
                    ContestRank.objects.create(contest=contest, user=user).update_rank(submission)

                if submission.result == result["accepted"]:
                    contest_problem.total_accepted_number += 1
                    contest_problem.save()

                    problems_status = user.problems_status
                    problems_status["contest_problems"][str(contest_problem.id)] = 1
                    user.problems_status = problems_status
                    user.save()

logger.debug("Start message queue")
MessageQueue().listen_task()
