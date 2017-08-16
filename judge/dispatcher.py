import hashlib
import json
import logging
from urllib.parse import urljoin

import requests
from django.core.cache import cache
from django.db import transaction
from django.db.models import F

from account.models import User
from conf.models import JudgeServer, JudgeServerToken
from contest.models import ContestRuleType, ACMContestRank, OIContestRank
from judge.languages import languages
from problem.models import Problem, ProblemRuleType, ContestProblem
from submission.models import JudgeStatus, Submission
from utils.cache import judge_cache
from utils.constants import CacheKey

logger = logging.getLogger(__name__)


# 继续处理在队列中的问题
def process_pending_task():
    if judge_cache.llen(CacheKey.waiting_queue):
        # 防止循环引入
        from judge.tasks import judge_task
        data = json.loads(judge_cache.rpop(CacheKey.waiting_queue).decode("utf-8"))
        judge_task.delay(**data)


class JudgeDispatcher(object):
    def __init__(self, submission_id, problem_id):
        token = JudgeServerToken.objects.first().token
        self.token = hashlib.sha256(token.encode("utf-8")).hexdigest()
        self.redis_conn = judge_cache
        self.submission = Submission.objects.get(pk=submission_id)
        if self.submission.contest_id:
            self.problem = ContestProblem.objects.select_related("contest")\
                .get(_id=problem_id, contest_id=self.submission.contest_id)
            self.contest = self.problem.contest
        else:
            self.problem = Problem.objects.get(pk=problem_id)

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
            data = {"submission_id": self.submission.id, "problem_id": self.problem.id}
            self.redis_conn.lpush(CacheKey.waiting_queue, json.dumps(data))
            return

        sub_config = list(filter(lambda item: self.submission.language == item["name"], languages))[0]
        spj_config = {}
        if self.problem.spj_code:
            for lang in languages:
                if lang["name"] == self.problem.spj_language:
                    spj_config = lang["spj"]
                    break
        data = {
            "language_config": sub_config["config"],
            "src": self.submission.code,
            "max_cpu_time": self.problem.time_limit,
            "max_memory": 1024 * 1024 * self.problem.memory_limit,
            "test_case_id": self.problem.test_case_id,
            "output": output,
            "spj_version": self.problem.spj_version,
            "spj_config": spj_config.get("config"),
            "spj_compile_config": spj_config.get("compile"),
            "spj_src": self.problem.spj_code
        }

        Submission.objects.filter(id=self.submission.id).update(result=JudgeStatus.JUDGING)

        # TODO: try catch
        resp = self._request(urljoin(server.service_url, "/judge"), data=data)
        self.submission.info = resp
        if resp["err"]:
            self.submission.result = JudgeStatus.COMPILE_ERROR
            self.submission.statistic_info["err_info"] = resp["data"]
        else:
            # 用时和内存占用保存为多个测试点中最长的那个
            self.submission.statistic_info["time_cost"] = max([x["cpu_time"] for x in resp["data"]])
            self.submission.statistic_info["memory_cost"] = max([x["memory"] for x in resp["data"]])

            error_test_case = list(filter(lambda case: case["result"] != 0, resp["data"]))
            # 多个测试点全部正确则AC，否则 ACM模式下取第一个错误的测试点的状态, OI模式若全部错误则取第一个错误测试点状态，否则为部分正确
            if not error_test_case:
                self.submission.result = JudgeStatus.ACCEPTED
            elif self.problem.rule_type == ProblemRuleType.ACM or len(error_test_case) == len(resp["data"]):
                self.submission.result = error_test_case[0]["result"]
            else:
                self.submission.result = JudgeStatus.PARTIALLY_ACCEPTED
        self.submission.save()
        self.release_judge_res(server.id)

        self.update_problem_status()

        if self.submission.contest_id:
            self.update_contest_rank()
        else:
            self.update_user_profile()
        # 至此判题结束，尝试处理任务队列中剩余的任务
        process_pending_task()

    def compile_spj(self, service_url, src, spj_version, spj_compile_config, test_case_id):
        data = {"src": src, "spj_version": spj_version,
                "spj_compile_config": spj_compile_config,
                "test_case_id": test_case_id}
        return self._request(urljoin(service_url, "compile_spj"), data=data)

    def update_problem_status(self):
        self.problem.add_submission_number()
        if self.submission.result == JudgeStatus.ACCEPTED:
            self.problem.add_ac_number()
        with transaction.atomic():
            if self.submission.contest_id:
                problem = ContestProblem.objects.select_for_update().get(_id=self.problem.id, contest_id=self.contest.id)
            else:
                problem = Problem.objects.select_related().get(_id=self.problem.id)
            info = problem.statistic_info
            result = str(self.submission.result)
            info[result] = info.get(result, 0) + 1
            problem.statistic_info = info
            problem.save(update_fields=["statistic_info"])

    def update_user_profile(self):
        with transaction.atomic():
            # 更新user profile
            user = User.objects.select_for_update().get(id=self.submission.user_id)
            user_profile = user.userprofile
            user_profile.add_submission_number()
            problems_status = user_profile.problems_status
            if "problems" not in problems_status:
                problems_status["problems"] = {}

            # 之前状态不是ac, 现在是ac了 需要更新用户ac题目数量计数器,这里需要判重
            if problems_status["problems"].get(str(self.problem.id), JudgeStatus.WRONG_ANSWER) != JudgeStatus.ACCEPTED:
                if self.submission.result == JudgeStatus.ACCEPTED:
                    user_profile.add_accepted_problem_number()
                    problems_status["problems"][str(self.problem.id)] = JudgeStatus.ACCEPTED
                else:
                    problems_status["problems"][str(self.problem.id)] = JudgeStatus.WRONG_ANSWER
            user_profile.problems_status = problems_status
            user_profile.save(update_fields=["problems_status"])

    def update_contest_rank(self):
        if self.contest.real_time_rank:
            cache.delete(str(self.contest.id) + "_rank_cache")
        with transaction.atomic():
            if self.contest.rule_type == ContestRuleType.ACM:
                acm_rank, _ = ACMContestRank.objects.select_for_update(). \
                    get_or_create(user_id=self.submission.user_id, contest=self.contest)
                self._update_acm_contest_rank(acm_rank)
            else:
                oi_rank, _ = OIContestRank.objects.select_for_update(). \
                    get_or_create(user_id=self.submission.user_id, contest=self.contest)
                self._update_oi_contest_rank(oi_rank)

    def _update_acm_contest_rank(self, rank):
        info = rank.submission_info.get(str(self.submission.problem_id))
        # 因前面更改过，这里需要重新获取
        problem = ContestProblem.objects.get(contest_id=self.contest.id, _id=self.problem._id)
        # 此题提交过
        if info:
            if info["is_ac"]:
                return

            rank.total_submission_number += 1
            if self.submission.result == JudgeStatus.ACCEPTED:
                rank.total_ac_number += 1
                info["is_ac"] = True
                info["ac_time"] = (self.submission.create_time - self.contest.start_time).total_seconds()
                rank.total_time += info["ac_time"] + info["error_number"] * 20 * 60

                if problem.total_accepted_number == 1:
                    info["is_first_ac"] = True
            else:
                info["error_number"] += 1

        # 第一次提交
        else:
            rank.total_submission_number += 1
            info = {"is_ac": False, "ac_time": 0, "error_number": 0, "is_first_ac": False}
            if self.submission.result == JudgeStatus.ACCEPTED:
                rank.total_ac_number += 1
                info["is_ac"] = True
                info["ac_time"] = (self.submission.create_time - self.contest.start_time).total_seconds()
                rank.total_time += info["ac_time"]

                if problem.total_accepted_number == 1:
                    info["is_first_ac"] = True

            else:
                info["error_number"] = 1
        rank.submission_info[str(self.submission.problem_id)] = info
        rank.save()

    def _update_oi_contest_rank(self, rank):
        pass
