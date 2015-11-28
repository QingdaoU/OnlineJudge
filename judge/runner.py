# coding=utf-8
import os
import socket
import shutil

from client import JudgeClient
from language import languages
from compiler import compile_
from result import result
from settings import judger_workspace


class JudgeInstanceRunner(object):
    def __init__(self):
        pass

    def run(self, submission_id, language_code, code, time_limit, memory_limit, test_case_id):
        language = languages[language_code]
        host_name = socket.gethostname()
        judge_base_path = os.path.join(judger_workspace, "run", submission_id)

        try:
            os.mkdir(judge_base_path)

            # 将代码写入文件
            src_path = os.path.join(judge_base_path, language["src_name"])
            f = open(src_path, "w")
            f.write(code.encode("utf8"))
            f.close()
        except Exception as e:
            shutil.rmtree(judge_base_path, ignore_errors=True)
            return {"code": 2, "data": {"error": str(e), "server": host_name}}

        # 编译
        try:
            exe_path = compile_(language, src_path, judge_base_path)
        except Exception as e:
            shutil.rmtree(judge_base_path, ignore_errors=True)
            return {"code": 1, "data": {"error": str(e), "server": host_name}}

        # 运行
        try:
            client = JudgeClient(language_code=language_code,
                                 exe_path=exe_path,
                                 max_cpu_time=int(time_limit),
                                 max_real_time=int(time_limit) * 2,
                                 max_memory=int(memory_limit),
                                 test_case_dir=judger_workspace + "test_case/" + test_case_id + "/")
            judge_result = {"result": result["accepted"], "info": client.run(),
                            "accepted_answer_time": None, "server": host_name}

            for item in judge_result["info"]:
                if item["result"]:
                    judge_result["result"] = item["result"]
                    break
            else:
                l = sorted(judge_result["info"], key=lambda k: k["cpu_time"])
                judge_result["accepted_answer_time"] = l[-1]["cpu_time"]
            return {"code": 0, "data": judge_result}
        except Exception as e:
            return {"code": 2, "data": {"error": str(e), "server": host_name}}
        finally:
            shutil.rmtree(judge_base_path, ignore_errors=True)