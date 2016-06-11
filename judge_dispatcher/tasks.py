# coding=utf-8
import json
import logging
import time

from django.db import transaction
from django.db.models import F

from rpc_client import TimeoutServerProxy

from judge.result import result
from contest.models import ContestProblem, ContestRank, Contest, CONTEST_UNDERWAY
from problem.models import Problem
from submission.models import Submission
from account.models import User
from utils.cache import get_cache_redis

from .models import JudgeServer, JudgeWaitingQueue

logger = logging.getLogger("app_info")


class JudgeDispatcher(object):
    def _none_to_false(self, value):
        # xml rpc不能使用None
        if value is None:
            return False
        else:
            return value

    def __init__(self, submission_id, time_limit, memory_limit, test_case_id, spj, spj_language, spj_code, spj_version):
        self.submission = Submission.objects.get(id=submission_id)
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.test_case_id = test_case_id
        self.spj = spj
        self.spj_language = spj_language
        self.spj_code = spj_code
        self.spj_version = spj_version

    def choose_judge_server(self):
        with transaction.atomic():
            servers = JudgeServer.objects.select_for_update().filter(used_instance_number__lt=F("max_instance_number"), status=True).order_by("max_instance_number")
            if servers.exists():
                server = servers.first()
                server.used_instance_number = F("used_instance_number") + 1
                server.save()
                return server

    def release_judge_instance(self, judge_server_id):
        with transaction.atomic():
            # 使用原子操作, 同时因为use和release中间间隔了判题过程,需要重新查询一下
            server = JudgeServer.objects.select_for_update().get(id=judge_server_id)
            server.used_instance_number = F("used_instance_number") - 1
            server.save()

    def judge(self):
        self.submission.judge_start_time = int(time.time() * 1000)

        judge_server = self.choose_judge_server()

        # 如果没有合适的判题服务器，就放入等待队列中等待判题
        if not judge_server:
            JudgeWaitingQueue.objects.create(submission_id=self.submission.id, time_limit=self.time_limit,
                                             memory_limit=self.memory_limit, test_case_id=self.test_case_id,
                                             spj=self.spj, spj_language=self.spj_language, spj_code=self.spj_code,
                                             spj_version=self.spj_version)
            return

        try:
            s = TimeoutServerProxy("http://" + judge_server.ip + ":" + str(judge_server.port),
                                   timeout=30)

            data = s.run(judge_server.token, self.submission.id, self.submission.language,
                         self.submission.code, self.time_limit, self.memory_limit, self.test_case_id,
                         self.spj, self._none_to_false(self.spj_language),
                         self._none_to_false(self.spj_code), self._none_to_false(self.spj_version))
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
            self.release_judge_instance(judge_server.id)

            self.submission.judge_end_time = int(time.time() * 1000)
            self.submission.save(update_fields=["judge_start_time", "result", "info", "accepted_answer_time", "judge_end_time"])

        if self.submission.contest_id:
            self.update_contest_problem_status()
        else:
            self.update_problem_status()

        with transaction.atomic():
            waiting_submissions = JudgeWaitingQueue.objects.select_for_update().all()
            if waiting_submissions.exists():
                # 防止循环依赖
                from submission.tasks import _judge

                waiting_submission = waiting_submissions.first()
                waiting_submission.delete()
                _judge.delay(submission_id=waiting_submission.submission_id,
                             time_limit=waiting_submission.time_limit,
                             memory_limit=waiting_submission.memory_limit,
                             test_case_id=waiting_submission.test_case_id,
                             spj=waiting_submission.spj,
                             spj_language=waiting_submission.spj_language,
                             spj_code=waiting_submission.spj_code,
                             spj_version=waiting_submission.spj_version)

    def update_problem_status(self):
        with transaction.atomic():
            problem = Problem.objects.select_for_update().get(id=self.submission.problem_id)
            # 更新普通题目的计数器
            problem.add_submission_number()

            # 更新用户做题状态
            user = User.objects.select_for_update().get(id=self.submission.user_id)

            problems_status = user.problems_status
            if "problems" not in problems_status:
                problems_status["problems"] = {}

            # 增加用户提交计数器
            user.userprofile.add_submission_number()

            # 之前状态不是ac, 现在是ac了 需要更新用户ac题目数量计数器,这里需要判重
            if problems_status["problems"].get(str(problem.id), -1) != 1 and self.submission.result == result["accepted"]:
                user.userprofile.add_accepted_problem_number()

            # 之前状态是ac, 现在不是ac了 需要用户ac题目数量计数器-1, 否则上一个逻辑胡重复增加ac计数器
            if problems_status["problems"].get(str(problem.id), -1) == 1 and self.submission.result != result["accepted"]:
                user.userprofile.minus_accepted_problem_number()

            if self.submission.result == result["accepted"]:
                problem.add_ac_number()
                problems_status["problems"][str(problem.id)] = 1
            else:
                problems_status["problems"][str(problem.id)] = 2
            user.problems_status = problems_status
            user.save(update_fields=["problems_status"])
        # 普通题目的话，到这里就结束了

    def update_contest_problem_status(self):
        # 能运行到这里的都是比赛题目
        contest = Contest.objects.get(id=self.submission.contest_id)
        if contest.status != CONTEST_UNDERWAY:
            logger.info("Contest debug mode, id: " + str(contest.id) + ", submission id: " + self.submission.id)
            return

        with transaction.atomic():
            contest_problem = ContestProblem.objects.select_for_update().get(contest=contest, id=self.submission.problem_id)
            contest_problem.add_submission_number()

            user = User.objects.select_for_update().get(id=self.submission.user_id)
            problems_status = user.problems_status

            if "contest_problems" not in problems_status:
                problems_status["contest_problems"] = {}

            # 增加用户提交计数器
            user.userprofile.add_submission_number()

            # 之前状态不是ac, 现在是ac了 需要更新用户ac题目数量计数器,这里需要判重
            if problems_status["contest_problems"].get(str(contest_problem.id), -1) != 1 and \
                            self.submission.result == result["accepted"]:
                user.userprofile.add_accepted_problem_number()

            if self.submission.result == result["accepted"]:
                contest_problem.add_ac_number()
                problems_status["contest_problems"][str(contest_problem.id)] = 1
            else:
                problems_status["contest_problems"][str(contest_problem.id)] = 2

            user.problems_status = problems_status
            user.save(update_fields=["problems_status"])

        self.update_contest_rank(contest)

    def update_contest_rank(self, contest):
        if contest.real_time_rank:
            get_cache_redis().delete(str(contest.id) + "_rank_cache")

        with transaction.atomic():
            try:
                contest_rank = ContestRank.objects.select_for_update().get(contest=contest, user_id=self.submission.user_id)
                contest_rank.update_rank(self.submission)
            except ContestRank.DoesNotExist:
                ContestRank.objects.create(contest=contest, user_id=self.submission.user_id).update_rank(self.submission)
