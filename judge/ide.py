import hashlib
import json
import logging
from urllib.parse import urljoin

import requests
from django.db import transaction
from django.db.models import F
from conf.models import JudgeServer
from options.options import SysOptions
from utils.cache import cache
from utils.constants import CacheKey
from judge.languages import _c_lang_config, _c_o2_lang_config, _cpp_lang_config, _cpp_o2_lang_config, _java_lang_config, _py2_lang_config, _py3_lang_config


logger = logging.getLogger(__name__)


class ChooseJudgeServer:
    def __init__(self):
        self.server = None

    def __enter__(self) -> [JudgeServer, None]:
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


class JudgeServerClientError(Exception):
    pass


class IDEDispatcher(object):
    def __init__(self, src, language, test_case=None):
        self.src = src
        self.language = language
        self.test_case = test_case
        self.token = hashlib.sha256(SysOptions.judge_server_token.encode("utf-8")).hexdigest()

    def _request(self, url, data=None):
        kwargs = {"headers": {"X-Judge-Server-Token": self.token,
                              "Content-Type": "application/json"}}
        if data:
            kwargs["data"] = json.dumps(data)
        try:
            return requests.post(url, **kwargs).json()
        except Exception as e:
            raise JudgeServerClientError(str(e))

    def judge(self):
        if not self.test_case:
            raise ValueError("invalid parameter")

        if self.language == "C":
            language_config = _c_lang_config
        if self.language == "C With O2":
            language_config = _c_o2_lang_config
        if self.language == "C++":
            language_config = _cpp_lang_config
        if self.language == "C++ With O2":
            language_config = _cpp_o2_lang_config
        if self.language == "Java":
            language_config = _java_lang_config
        if self.language == "Python2":
            language_config = _py2_lang_config
        if self.language == "Python3":
            language_config = _py3_lang_config

        # sub_config = list(filter(lambda item: self.language == item["name"], SysOptions.languages))[0]

        max_cpu_time = 2000
        max_memory = 1024 * 1024 * 128
        output = True
        data = {
            "language_config": language_config,
            "src": self.src,
            "max_cpu_time": max_cpu_time,
            "max_memory": max_memory,
            "test_case": self.test_case,
            "output": output
        }
        with ChooseJudgeServer() as server:
            if not server:
                cache.lpush(CacheKey.waiting_queue, json.dumps(data))
                return "JudgeServer ERROR"
            return self._request(urljoin(server.service_url, "/judge"), data=data)
            # return data
