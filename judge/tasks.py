import time
import json
import requests
import hashlib
import logging
from urllib.parse import urljoin

from django.db import transaction
from django.db.models import F
from django_redis import get_redis_connection

from judge.languages import languages
from account.models import User, UserProfile
from conf.models import JudgeServer, JudgeServerToken
from contest.models import Contest
from problem.models import Problem, ProblemRuleType
from submission.models import Submission, JudgeStatus

logger = logging.getLogger(__name__)

WAITING_QUEUE = "waiting_queue"


class JudgeDispatcher(object):
    def __init__(self, submission_obj, problem_obj):
        token = JudgeServerToken.objects.first().token
        self.token = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.redis_conn = get_redis_connection("JudgeQueue")
        self.submission_obj = submission_obj
        self.problem_obj = problem_obj

    def _request(self, url, data=None):
        kwargs = {"headers": {"X-Judge-Server-Token": self.token,
                              "Content-Type": "application/json"}}
        if data:
            kwargs["data"] = json.dumps(data)
        try:
            return requests.post(url, **kwargs).json()
        except Exception as e:
            logger.error(e.with_traceback())

    @staticmethod
    def choose_judge_server():
        with transaction.atomic():
            # TODO: use more reasonable way
            servers = JudgeServer.objects.select_for_update().filter(
                status="normal").order_by("task_number")
            if servers.exists():
                server = servers.first()
                server.used_instance_number = F("task_number") + 1
                server.save()
                return server

    @staticmethod
    def release_judge_res(judge_server_id):
        with transaction.atomic():
            # 使用原子操作, 同时因为use和release中间间隔了判题过程,需要重新查询一下
            server = JudgeServer.objects.select_for_update().get(id=judge_server_id)
            server.used_instance_number = F("task_number") - 1
            server.save()

    def judge(self, output=False):
        server = self.choose_judge_server()
        if not server:
            self.redis_conn.lpush(WAITING_QUEUE, self.submission_obj.id)
            return

        language = list(filter(lambda item: self.submission_obj.language == item['name'], languages))[0]
        data = {"language_config": language['config'],
                "src": self.submission_obj.code,
                "max_cpu_time": self.problem_obj.time_limit,
                "max_memory": self.problem_obj.memory_limit,
                "test_case_id": self.problem_obj.test_case_id,
                "output": output}
        # TODO: try catch
        resp = self._request(urljoin(server.service_url, "/judge"), data=data)
        self.submission_obj.info = resp
        if resp['err']:
            self.submission_obj.result = JudgeStatus.COMPILE_ERROR
        else:
            error_test_case = list(filter(lambda case: case['result'] != 0, resp))
            # 多个测试点全部正确AC，否则ACM模式下取第一个测试点状态
            if not error_test_case:
                self.submission_obj.result = JudgeStatus.ACCEPTED
            elif self.problem_obj.rule_tyle == ProblemRuleType.ACM:
                self.submission_obj.result = error_test_case[0].result
            else:
                self.submission_obj.result = JudgeStatus.PARTIALLY_ACCEPTED
        self.submission_obj.save()
        self.release_judge_res(server.id)

        if self.submission_obj.contest_id:
            # ToDo: update contest status
            pass
        else:
            self.update_problem_status()
        # 取redis中等待中的提交
        if self.redis_conn.llen(WAITING_QUEUE):
            pass

    def compile_spj(self, service_url, src, spj_version, spj_compile_config, test_case_id):
        data = {"src": src, "spj_version": spj_version,
                "spj_compile_config": spj_compile_config, "test_case_id": test_case_id}
        return self._request(service_url + "/compile_spj", data=data)

    def update_problem_status(self):
        with transaction.atomic():
            problem = Problem.objects.select_for_update().get(id=self.problem_obj.problem_id)
            # 更新普通题目的计数器
            problem.add_submission_number()

            # 更新用户做题状态
            user = User.objects.select_for_update().get(id=self.submission_obj.user_id)
            problems_status = UserProfile.objects.get(user=user).problem_status

            if "problems" not in problems_status:
                problems_status["problems"] = {}

            # 增加用户提交计数器
            user.userprofile.add_submission_number()

            # 之前状态不是ac, 现在是ac了 需要更新用户ac题目数量计数器,这里需要判重
            if problems_status["problems"].get(str(problem.id), JudgeStatus.WRONG_ANSWER) != JudgeStatus.ACCEPTED:
                if self.submission_obj.result == JudgeStatus.ACCEPTED:
                    user.userprofile.add_accepted_problem_number()
                    problems_status["problems"][str(problem.id)] = JudgeStatus.ACCEPTED
                else:
                    problems_status["problems"][str(problem.id)] = JudgeStatus.WRONG_ANSWER
            user.problems_status = problems_status
            user.save(update_fields=["problems_status"])
