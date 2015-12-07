# coding=utf-8
import json
import logging
import time

from django.db import transaction

from rpc_client import TimeoutServerProxy

from judge.result import result
from contest.models import ContestProblem, ContestRank, Contest, CONTEST_UNDERWAY
from problem.models import Problem
from submission.models import Submission
from account.models import User
from utils.cache import get_cache_redis
from .models import JudgeServer,JudgeWaitingQueue

logger = logging.getLogger("app_info")


class JudgeDispatcher(object):
    def __init__(self, submission, time_limit, memory_limit, test_case_id):
        self.submission = submission
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.test_case_id = test_case_id
        self.user = User.objects.get(id=submission.user_id)
    
    def choose_judge_server(self):
        servers = JudgeServer.objects.filter(workload__lt=100, lock=False, status=True).order_by("-workload")
        if servers.exists():
            return servers[0]
    
    def judge(self):
        self.submission.judge_start_time = int(time.time() * 1000)
        try:
            judge_server = self.choose_judge_server()
            # 如果没有合适的判题服务器，就放入等待队列中等待判题
            if not judge_server:
                JudgeWaitingQueue.objects.create(submission_id=self.submission.id)
                return

            s = TimeoutServerProxy(judge_server.ip + ":" + judge_server.port, timeout=20)
            data = s.run(self.submission.id, self.submission.language_code,
                         self.submission.code, self.time_limit, self.memory_limit, self.test_case_id)
            # 编译错误
            if data["code"] == 1:
                self.submission.result = result["compile_error"]
                self.submission.info = data["data"]["error"]
            # system error
            elif data["code"] == 2:
                self.submission.result = result["system_error"]
                self.submission.info = data["data"]["error"]
            elif data["code"] == 0:
                self.submission.result = data["data"]["result"]
                self.submission.info = json.dumps(data["data"]["info"])
                self.submission.accepted_answer_time = data["data"]["accepted_answer_time"]
        except Exception as e:
            self.submission.result = result["system_error"]
            self.submission.info = str(e)
        finally:
            self.submission.judge_end_time = int(time.time() * 1000)
            self.submission.save()

        if self.submission.contest_id:
            self.update_contest_problem_status()
        else:
            self.update_problem_status()
    
    def update_problem_status(self):
        problem = Problem.objects.get(id=self.submission.problem_id)

        # 更新普通题目的计数器
        problem.add_submission_number()

        # 更新用户做题状态
        problems_status = self.user.problems_status
        if "problems" not in problems_status:
            problems_status["problems"] = {}
        if self.submission.result == result["accepted"]:
            problem.add_ac_number()
            problems_status["problems"][str(problem.id)] = 1
        else:
            problems_status["problems"][str(problem.id)] = 2
        self.user.problems_status = problems_status
        self.user.save()
        # 普通题目的话，到这里就结束了

    def update_contest_problem_status(self):
        # 能运行到这里的都是比赛题目
        contest = Contest.objects.get(id=self.submission.contest_id)
        if contest.status != CONTEST_UNDERWAY:
            logger.info("Contest debug mode, id: " + str(contest.id) + ", submission id: " + self.submission.id)
            return
        contest_problem = ContestProblem.objects.get(contest=contest, id=self.submission.problem_id)

        contest_problem.add_submission_number()

        problems_status = self.user.problems_status
        if "contest_problems" not in problems_status:
            problems_status["contest_problems"] = {}
        if self.submission.result == result["accepted"]:
            contest_problem.add_ac_number()
            problems_status["contest_problems"][str(contest_problem.id)] = 1
        else:
            problems_status["contest_problems"][str(contest_problem.id)] = 0
        self.user.problems_status = problems_status
        self.user.save()

        self.update_contest_rank(contest)
    
    def update_contest_rank(self, contest):
        if contest.real_time_rank:
            get_cache_redis().delete(str(contest.id) + "_rank_cache")

        with transaction.atomic():
            try:
                contest_rank = ContestRank.objects.get(contest=contest, user=self.user)
                contest_rank.update_rank(self.submission)
            except ContestRank.DoesNotExist:
                ContestRank.objects.create(contest=contest, user=self.user).update_rank(self.submission)
