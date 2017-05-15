import json
import requests
import hashlib
import logging
from urllib.parse import urljoin
from functools import reduce

from django.db import transaction
from django.db.models import F
from django_redis import get_redis_connection

from judge.languages import languages
from account.models import User
from conf.models import JudgeServer, JudgeServerToken
from problem.models import Problem, ProblemRuleType
from submission.models import JudgeStatus, Submission

logger = logging.getLogger(__name__)

WAITING_QUEUE = "waiting_queue"


# 继续处理在队列中的问题
def process_pending_task(redis_conn):
    if redis_conn.llen(WAITING_QUEUE):
        # 防止循环引入
        from submission.tasks import judge_task
        data = json.loads(redis_conn.rpop(WAITING_QUEUE))
        judge_task.delay(**data)


class JudgeDispatcher(object):
    def __init__(self, submission_id, problem_id):
        token = JudgeServerToken.objects.first().token
        self.token = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.redis_conn = get_redis_connection("JudgeQueue")
        self.submission_obj = Submission.objects.get(pk=submission_id)
        self.problem_obj = Problem.objects.get(pk=problem_id)

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
            servers = JudgeServer.objects.select_for_update().all().order_by("task_number")
            servers = [s for s in servers if s.status == "normal"]
            if servers:
                server = servers[0]
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
            data = {"submission_id": self.submission_obj.id, "problem_id": self.problem_obj.id}
            self.redis_conn.lpush(WAITING_QUEUE, json.dumps(data))
            return

        language = list(filter(lambda item: self.submission_obj.language == item["name"], languages))[0]
        data = {
            "language_config": language["config"],
            "src": self.submission_obj.code,
            "max_cpu_time": self.problem_obj.time_limit,
            "max_memory": 1024 * 1024 * self.problem_obj.memory_limit,
            "test_case_id": self.problem_obj.test_case_id,
            "output": output
        }
        self.submission_obj.result = JudgeStatus.JUDGING
        self.submission_obj.save()
        # TODO: try catch
        resp = self._request(urljoin(server.service_url, "/judge"), data=data)
        self.submission_obj.info = resp
        if resp["err"]:
            self.submission_obj.result = JudgeStatus.COMPILE_ERROR
        else:
            error_test_case = list(filter(lambda case: case["result"] != 0, resp["data"]))
            # 多个测试点全部正确AC，否则ACM模式下取第一个测试点状态
            if not error_test_case:
                self.submission_obj.result = JudgeStatus.ACCEPTED
                self.submission_obj.accepted_time = reduce(lambda x, y: x + y["cpu_time"], resp["data"], 0)
            elif self.problem_obj.rule_type == ProblemRuleType.ACM:
                self.submission_obj.result = error_test_case[0]["result"]
            else:
                self.submission_obj.result = JudgeStatus.PARTIALLY_ACCEPTED
        self.submission_obj.save()
        self.release_judge_res(server.id)

        if self.submission_obj.contest_id:
            # ToDo: update contest status
            pass
        else:
            self.update_problem_status()
        process_pending_task(self.redis_conn)

    def compile_spj(self, service_url, src, spj_version, spj_compile_config, test_case_id):
        data = {"src": src, "spj_version": spj_version,
                "spj_compile_config": spj_compile_config,
                "test_case_id": test_case_id}
        return self._request(urljoin(service_url, "compile_spj"), data=data)

    def update_problem_status(self):
        with transaction.atomic():
            problem = Problem.objects.select_for_update().get(id=self.problem_obj.id)
            user = User.objects.select_for_update().get(id=self.submission_obj.user_id)
            # 更新提交计数器
            problem.add_submission_number()
            user_profile = user.userprofile
            user_profile.add_submission_number()

            if self.submission_obj.result == JudgeStatus.ACCEPTED:
                problem.add_ac_number()

            problems_status = user_profile.problems_status
            if "problems" not in problems_status:
                problems_status["problems"] = {}

            # 之前状态不是ac, 现在是ac了 需要更新用户ac题目数量计数器,这里需要判重
            if problems_status["problems"].get(str(problem.id), JudgeStatus.WRONG_ANSWER) != JudgeStatus.ACCEPTED:
                if self.submission_obj.result == JudgeStatus.ACCEPTED:
                    user_profile.add_accepted_problem_number()
                    problems_status["problems"][str(problem.id)] = JudgeStatus.ACCEPTED
                else:
                    problems_status["problems"][str(problem.id)] = JudgeStatus.WRONG_ANSWER
            user_profile.problems_status = problems_status
            user_profile.save(update_fields=["problems_status"])
