import hashlib
import logging
from urllib.parse import urljoin

import requests
from django.db.models import F

from conf.models import JudgeServer
from options.options import SysOptions
from submission.models import JudgeStatus
from utils.cache import cache

logger = logging.getLogger(__name__)


class ChooseJudgeServer:
    def __init__(self):
        self.server = None

    def __enter__(self):
        from django.db import transaction
        with transaction.atomic():
            servers = JudgeServer.objects.select_for_update().filter(is_disabled=False).order_by("task_number")
            servers = [s for s in servers if s.status == "normal"]
            for server in servers:
                if server.task_number <= server.cpu_core * 2:
                    server.task_number = F("task_number") + 1
                    server.save(update_fields=["task_number"])
                    self.server = server
                    return server
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.server:
            JudgeServer.objects.filter(id=self.server.id).update(task_number=F("task_number") - 1)


class CodeRunner:
    def __init__(self, code_run):
        self.code_run = code_run
        self.token = hashlib.sha256(SysOptions.judge_server_token.encode("utf-8")).hexdigest()

    def _request(self, url, data=None):
        kwargs = {"headers": {"X-Judge-Server-Token": self.token}}
        if data:
            kwargs["json"] = data
        try:
            return requests.post(url, **kwargs).json()
        except Exception as e:
            logger.exception(e)

    def run(self):
        language = self.code_run.language
        sub_config = list(filter(lambda item: language == item["name"], SysOptions.languages))
        if not sub_config:
            self.code_run.result = JudgeStatus.SYSTEM_ERROR
            self.code_run.info = {"error": f"Unsupported language: {language}"}
            self.code_run.save()
            return

        sub_config = sub_config[0]

        data = {
            "language_config": sub_config["config"],
            "src": self.code_run.code,
            "max_cpu_time": 5000,
            "max_memory": 1024 * 1024 * 256,
            "test_case_id": None,
            "output": True,
            "spj_version": "",
            "spj_config": {},
            "spj_compile_config": "",
            "spj_src": "",
            "io_mode": {"input": "stdin", "output": "stdout"}
        }

        with ChooseJudgeServer() as server:
            if not server:
                self.code_run.result = JudgeStatus.SYSTEM_ERROR
                self.code_run.info = {"error": "No available judge server"}
                self.code_run.save()
                return

            self.code_run.result = JudgeStatus.JUDGING
            self.code_run.save()

            resp = self._request(urljoin(server.service_url, "/judge"), data=data)

        if not resp:
            self.code_run.result = JudgeStatus.SYSTEM_ERROR
            self.code_run.info = {"error": "Failed to call judge server"}
            self.code_run.save()
            return

        if resp.get("err"):
            self.code_run.result = JudgeStatus.COMPILE_ERROR
            self.code_run.statistic_info = {"err_info": resp.get("data", "")}
            self.code_run.info = resp
            self.code_run.save()
        else:
            self.code_run.info = resp
            test_results = resp.get("data", [])
            if test_results:
                self.code_run.statistic_info = {
                    "time_cost": max([x.get("cpu_time", 0) for x in test_results]),
                    "memory_cost": max([x.get("memory", 0) for x in test_results]),
                    "output": test_results[0].get("output", "")
                }

                error_test_case = list(filter(lambda case: case["result"] != 0, test_results))
                if not error_test_case:
                    self.code_run.result = JudgeStatus.ACCEPTED
                else:
                    self.code_run.result = error_test_case[0]["result"]
                    self.code_run.statistic_info["err_info"] = error_test_case[0].get("output", "")
            else:
                self.code_run.result = JudgeStatus.ACCEPTED
                self.code_run.statistic_info = {"time_cost": 0, "memory_cost": 0, "output": ""}

            self.code_run.save()
