import hashlib
import json
import logging
from urllib.parse import urljoin

import requests
from django.db import transaction
from django.db.models import F

from account.models import User
from conf.models import JudgeServer
from contest.models import ContestRuleType, ACMContestRank, OIContestRank, ContestStatus
from judge.languages import languages
from options.options import SysOptions
from problem.models import Problem, ProblemRuleType
from submission.models import JudgeStatus, Submission
from utils.cache import cache
from utils.constants import CacheKey

logger = logging.getLogger(__name__)


# 继续处理在队列中的问题
def process_pending_task():
    if cache.llen(CacheKey.waiting_queue):
        # 防止循环引入
        from judge.tasks import judge_task
        data = json.loads(cache.rpop(CacheKey.waiting_queue).decode("utf-8"))
        judge_task.delay(**data)


class JudgeDispatcher(object):
    def __init__(self, submission_id, problem_id):
        self.token = hashlib.sha256(SysOptions.judge_server_token.encode("utf-8")).hexdigest()
        self.submission = Submission.objects.get(id=submission_id)
        self.contest_id = self.submission.contest_id
        if self.contest_id:
            self.problem = Problem.objects.select_related("contest").get(id=problem_id, contest_id=self.contest_id)
            self.contest = self.problem.contest
        else:
            self.problem = Problem.objects.get(id=problem_id)

    def _request(self, url, data=None):
        kwargs = {"headers": {"X-Judge-Server-Token": self.token}}
        if data:
            kwargs["json"] = data
        try:
            return requests.post(url, **kwargs).json()
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def choose_judge_server():
        with transaction.atomic():
            servers = JudgeServer.objects.select_for_update().all().order_by("task_number")
            servers = [s for s in servers if s.status == "normal"]
            if servers:
                server = servers[0]
                server.used_instance_number = F("task_number") + 1
                server.save()
                return server

    @staticmethod
    def release_judge_server(judge_server_id):
        with transaction.atomic():
            # 使用原子操作, 同时因为use和release中间间隔了判题过程,需要重新查询一下
            server = JudgeServer.objects.get(id=judge_server_id)
            server.used_instance_number = F("task_number") - 1
            server.save()

    def _compute_statistic_info(self, resp_data):
        # 用时和内存占用保存为多个测试点中最长的那个
        self.submission.statistic_info["time_cost"] = max([x["cpu_time"] for x in resp_data])
        self.submission.statistic_info["memory_cost"] = max([x["memory"] for x in resp_data])

        # sum up the score in OI mode
        if self.problem.rule_type == ProblemRuleType.OI:
            score = 0
            try:
                for i in range(len(resp_data)):
                    if resp_data[i]["result"] == JudgeStatus.ACCEPTED:
                        score += self.problem.test_case_score[i]["score"]
            except IndexError:
                logger.error(f"Index Error raised when summing up the score in problem {self.problem.id}")
                self.submission.statistic_info["score"] = 0
                return
            self.submission.statistic_info["score"] = score

    def judge(self, output=False):
        server = self.choose_judge_server()
        if not server:
            data = {"submission_id": self.submission.id, "problem_id": self.problem.id}
            cache.lpush(CacheKey.waiting_queue, json.dumps(data))
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
            self.submission.statistic_info["score"] = 0
        else:
            self._compute_statistic_info(resp["data"])
            error_test_case = list(filter(lambda case: case["result"] != 0, resp["data"]))
            # ACM模式下,多个测试点全部正确则AC，否则取第一个错误的测试点的状态
            # OI模式下, 若多个测试点全部正确则AC， 若全部错误则取第一个错误测试点状态，否则为部分正确
            if not error_test_case:
                self.submission.result = JudgeStatus.ACCEPTED
            elif self.problem.rule_type == ProblemRuleType.ACM or len(error_test_case) == len(resp["data"]):
                self.submission.result = error_test_case[0]["result"]
            else:
                self.submission.result = JudgeStatus.PARTIALLY_ACCEPTED
        self.submission.save()
        self.release_judge_server(server.id)

        self.update_problem_status()
        if self.contest_id:
            self.update_contest_rank()

        # 至此判题结束，尝试处理任务队列中剩余的任务
        process_pending_task()

    def compile_spj(self, service_url, src, spj_version, spj_compile_config, test_case_id):
        data = {"src": src, "spj_version": spj_version,
                "spj_compile_config": spj_compile_config,
                "test_case_id": test_case_id}
        return self._request(urljoin(service_url, "compile_spj"), data=data)

    def update_problem_status(self):
        if self.contest_id and self.contest.status != ContestStatus.CONTEST_UNDERWAY:
            logger.info("Contest debug mode, id: " + str(self.contest_id) + ", submission id: " + self.submission.id)
            return
        with transaction.atomic():
            # prepare problem and user_profile
            problem = Problem.objects.select_for_update().get(contest_id=self.contest_id, id=self.problem.id)
            problem_info = problem.statistic_info
            user = User.objects.select_for_update().select_for_update("userprofile").get(id=self.submission.user_id)
            user_profile = user.userprofile
            if self.contest_id:
                key = "contest_problems"
            else:
                key = "problems"
            acm_problems_status = user_profile.acm_problems_status.get(key, {})
            oi_problems_status = user_profile.oi_problems_status.get(key, {})

            # update submission and accepted number counter
            problem.submission_number += 1
            if self.submission.result == JudgeStatus.ACCEPTED:
                problem.accepted_number += 1
            # only when submission is not in contest, we update user profile,
            # in other words, users' submission in a contest will not be counted in user profile
            if not self.contest_id:
                user_profile.submission_number += 1
                if self.submission.result == JudgeStatus.ACCEPTED:
                    user_profile.accepted_number += 1

            problem_id = str(self.problem.id)
            if self.problem.rule_type == ProblemRuleType.ACM:
                # update acm problem info
                result = str(self.submission.result)
                problem_info[result] = problem_info.get(result, 0) + 1
                problem.statistic_info = problem_info

                # update user_profile
                if problem_id not in acm_problems_status:
                    acm_problems_status[problem_id] = self.submission.result
                # skip if the problem has been accepted
                elif acm_problems_status[problem_id] != JudgeStatus.ACCEPTED:
                    if self.submission.result == JudgeStatus.ACCEPTED:
                        acm_problems_status[problem_id] = JudgeStatus.ACCEPTED
                    else:
                        acm_problems_status[problem_id] = self.submission.result
                user_profile.acm_problems_status[key] = acm_problems_status

            else:
                # update oi problem info
                score = self.submission.statistic_info["score"]
                problem_info[score] = problem_info.get(score, 0) + 1
                problem.statistic_info = problem_info

                # update user_profile
                if problem_id not in oi_problems_status:
                    user_profile.add_score(score)
                    oi_problems_status[problem_id] = score
                else:
                    # minus last time score, add this time score
                    user_profile.add_score(this_time_score=score, last_time_score=oi_problems_status[problem_id])
                    oi_problems_status[problem_id] = score
                user_profile.oi_problems_status[key] = oi_problems_status

            problem.save(update_fields=["submission_number", "accepted_number", "statistic_info"])
            user_profile.save(update_fields=[
                "submission_number", "accepted_number", "acm_problems_status", "oi_problems_status"])

    def update_contest_rank(self):
        if self.contest_id and self.contest.status != ContestStatus.CONTEST_UNDERWAY:
            return
        if self.contest.real_time_rank:
            cache.delete(CacheKey.contest_rank_cache + str(self.contest_id))
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
        problem = Problem.objects.get(contest_id=self.contest_id, id=self.problem.id)
        # 此题提交过
        if info:
            if info["is_ac"]:
                return

            rank.submission_number += 1
            if self.submission.result == JudgeStatus.ACCEPTED:
                rank.accepted_number += 1
                info["is_ac"] = True
                info["ac_time"] = (self.submission.create_time - self.contest.start_time).total_seconds()
                rank.total_time += info["ac_time"] + info["error_number"] * 20 * 60

                if problem.accepted_number == 1:
                    info["is_first_ac"] = True
            else:
                info["error_number"] += 1

        # 第一次提交
        else:
            rank.submission_number += 1
            info = {"is_ac": False, "ac_time": 0, "error_number": 0, "is_first_ac": False}
            if self.submission.result == JudgeStatus.ACCEPTED:
                rank.accepted_number += 1
                info["is_ac"] = True
                info["ac_time"] = (self.submission.create_time - self.contest.start_time).total_seconds()
                rank.total_time += info["ac_time"]

                if problem.accepted_number == 1:
                    info["is_first_ac"] = True

            else:
                info["error_number"] = 1
        rank.submission_info[str(self.submission.problem_id)] = info
        rank.save()

    def _update_oi_contest_rank(self, rank):
        problem_id = str(self.submission.problem_id)
        current_score = self.submission.statistic_info["score"]
        last_score = rank.submission_info.get(problem_id)
        if last_score:
            rank.total_score = rank.total_score - last_score + current_score
        rank.submission_info[problem_id] = current_score
        rank.save()
