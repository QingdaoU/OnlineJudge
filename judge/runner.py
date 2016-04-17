# coding=utf-8
import os
import socket
import shutil

from logger import logger
from client import JudgeClient
from language import languages
from compiler import compile_
from result import result
from settings import judger_workspace


class JudgeInstanceRunner(object):

    def run(self, token, submission_id, language_code, code, time_limit, memory_limit, test_case_id,
            spj, spj_language, spj_code, spj_version):
        language = languages[language_code]
        host_name = socket.gethostname()
        judge_base_path = os.path.join(judger_workspace, "run", submission_id)

        if not token or token != os.environ.get("rpc_token"):
            if token:
                logger.info("Invalid token: " + token)
            return {"code": 2, "data": {"error": "Invalid token", "server": host_name}}

        try:
            os.mkdir(judge_base_path)
            os.chmod(judge_base_path, 0777)

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
            exe_path = compile_(language_item=language, src_path=src_path,
                                exe_path=judge_base_path, judge_base_path=judge_base_path, compile_spj=False)
        except Exception as e:
            shutil.rmtree(judge_base_path, ignore_errors=True)
            return {"code": 1, "data": {"error": str(e), "server": host_name}}

        test_case_dir = os.path.join(judger_workspace, "test_case", test_case_id)

        # SPJ相关
        if spj:
            spj_path = os.path.join(test_case_dir, "spj-" + spj_version)
            if "spj-" + spj_version not in os.listdir(test_case_dir):
                spj_language_item = languages[spj_language]
                spj_code_path = os.path.join(test_case_dir, "spj-" + spj_language_item["src_name"])

                f = open(spj_code_path, "w")
                f.write(spj_code.encode("utf8"))
                f.close()

                try:
                    compile_(language_item=languages[spj_language], src_path=spj_code_path,
                             exe_path=spj_path,
                             judge_base_path=judge_base_path, compile_spj=True)
                except Exception as e:
                    return {"code": 2, "data": {"error": "SPJ Compile error: " + str(e), "server": host_name}}
        else:
            spj_path = None

        # 运行
        try:
            client = JudgeClient(language_code=language_code,
                                 exe_path=exe_path,
                                 max_cpu_time=int(time_limit),
                                 max_memory=int(memory_limit) * 1024 * 1024,
                                 test_case_dir=test_case_dir,
                                 judge_base_path=judge_base_path, spj_path=spj_path)
            judge_result = {"result": result["accepted"], "info": client.run(),
                            "accepted_answer_time": None, "server": host_name}

            for item in judge_result["info"]:
                if item["result"] != 0:
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