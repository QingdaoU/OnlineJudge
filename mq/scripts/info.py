# coding=utf-8
import logging

import redis

from judge.judger_controller.settings import redis_config
from judge.judger.result import result
from submission.models import Submission
from problem.models import Problem
from contest.models import ContestProblem, Contest, ContestSubmission
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

            if submission.result == result["accepted"] and not submission.contest_id:
                # 更新普通题目的 ac 计数器
                try:
                    problem = Problem.objects.get(id=submission.problem_id)
                    problem.total_accepted_number += 1
                    problem.save()
                except Problem.DoesNotExist:
                    logger.warning("Submission problem does not exist, submission_id: " + submission_id)
                # 普通题目的话，到这里就结束了
                continue

            # 能运行到这里的都是比赛题目
            try:
                contest = Contest.objects.get(id=submission.contest_id)
                contest_problem = ContestProblem.objects.get(contest=contest, id=submission.problem_id)
            except Contest.DoesNotExist:
                logger.warning("Submission contest does not exist, submission_id: " + submission_id)
                continue
            except ContestProblem.DoesNotExist:
                logger.warning("Submission problem does not exist, submission_id: " + submission_id)
                continue

            try:
                contest_submission = ContestSubmission.objects.get(user_id=submission.user_id, contest=contest,
                                                                   problem_id=contest_problem.id)
                # 提交次数加1

                if submission.result == result["accepted"]:
                    # 避免这道题已经 ac 了，但是又重新提交了一遍
                    if not contest_submission.ac:
                        # 这种情况是这个题目前处于错误状态，就使用已经存储了的罚时加上这道题的实际用时
                        # logger.debug(contest.start_time)
                        # logger.debug(submission.create_time)
                        # logger.debug((submission.create_time - contest.start_time).total_seconds())
                        # logger.debug(int((submission.create_time - contest.start_time).total_seconds() / 60))
                        contest_submission.ac_time = int((submission.create_time - contest.start_time).total_seconds())
                        contest_submission.total_time += contest_submission.ac_time
                        contest_submission.total_submission_number += 1
                    # 标记为已经通过
                    if contest_problem.total_accepted_number == 0:
                        contest_submission.first_achieved = True
                    contest_submission.ac = True
                    # contest problem ac 计数器加1
                    contest_problem.total_accepted_number += 1
                else:
                    # 如果这个提交是错误的，就罚时20分钟
                    contest_submission.total_time += 1200
                    contest_submission.total_submission_number += 1
                contest_submission.save()
                contest_problem.save()
            except ContestSubmission.DoesNotExist:
                # 第一次提交
                is_ac = submission.result == result["accepted"]
                first_achieved = False
                ac_time = 0
                if is_ac:
                    ac_time = int((submission.create_time - contest.start_time).total_seconds())
                    total_time = int((submission.create_time - contest.start_time).total_seconds())
                    # 增加题目总的ac数计数器
                    if contest_problem.total_accepted_number == 0:
                        first_achieved = True
                    contest_problem.total_accepted_number += 1
                    contest_problem.save()
                else:
                    # 没过罚时20分钟
                    total_time = 1200
                ContestSubmission.objects.create(user_id=submission.user_id, contest=contest, problem=contest_problem,
                                                 ac=is_ac, total_time=total_time, first_achieved=first_achieved,
                                                 ac_time=ac_time)


logger.debug("Start message queue")
MessageQueue().listen_task()
