# coding=utf-8
import os
import json
import commands
import hashlib
from multiprocessing import Pool

from settings import max_running_number, lrun_gid, lrun_uid, judger_workspace
from language import languages
from result import result
from judge_exceptions import JudgeClientError
from utils import parse_lrun_output
from logger import logger


# 下面这个函数作为代理访问实例变量，否则Python2会报错，是Python2的已知问题
# http://stackoverflow.com/questions/1816958/cant-pickle-type-instancemethod-when-using-pythons-multiprocessing-pool-ma/7309686
def _run(instance, test_case_id):
    return instance._judge_one(test_case_id)


class JudgeClient(object):
    def __init__(self, language_code, exe_path, max_cpu_time,
                 max_real_time, max_memory, test_case_dir):
        """
        :param language_code: 语言编号
        :param exe_path: 可执行文件路径
        :param max_cpu_time: 最大cpu时间，单位ms
        :param max_real_time: 最大执行时间，单位ms
        :param max_memory: 最大内存，单位MB
        :param test_case_dir: 测试用例文件夹路径
        :return:返回结果list
        """
        self._language = languages[language_code]
        self._exe_path = exe_path
        self._max_cpu_time = max_cpu_time
        self._max_real_time = max_real_time
        self._max_memory = max_memory
        self._test_case_dir = test_case_dir
        # 进程池
        self._pool = Pool(processes=max_running_number)
        # 测试用例配置项
        self._test_case_info = self._load_test_case_info()

    def _load_test_case_info(self):
        # 读取测试用例信息 转换为dict
        try:
            f = open(self._test_case_dir + "info")
            return json.loads(f.read())
        except IOError:
            raise JudgeClientError("Test case config file not found")
        except ValueError:
            raise JudgeClientError("Test case config file format error")

    def _generate_command(self, test_case_id):
        """
        设置相关运行限制 进制访问网络 如果启用tmpfs 就把代码输出写入tmpfs，否则写入硬盘
        """
        # todo 系统调用白名单 chroot等参数
        command = "lrun" + \
                  " --max-cpu-time " + str(self._max_cpu_time / 1000.0) + \
                  " --max-real-time " + str(self._max_real_time / 1000.0 * 2) + \
                  " --max-memory " + str(self._max_memory * 1000 * 1000) + \
                  " --network false" + \
                  " --syscalls '" + self._language["syscalls"] + "'" + \
                  " --max-nprocess 20" + \
                  " --uid " + str(lrun_uid) + \
                  " --gid " + str(lrun_gid)

        execute_command = self._language["execute_command"].format(exe_path=self._exe_path)

        command += (" " +
                    execute_command +
                    # 0就是stdin
                    " 0<" + self._test_case_dir + str(test_case_id) + ".in" +
                    # 1就是stdout
                    " 1>" + judger_workspace + str(test_case_id) + ".out" +
                    # 3是stderr，包含lrun的输出和程序的异常输出
                    " 3>&2")
        return command

    def _parse_lrun_output(self, output):
        # 要注意的是 lrun把结果输出到了stderr，所以有些情况下lrun的输出可能与程序的一些错误输出的混合的，要先分离一下
        error = None
        # 倒序找到MEMORY的位置
        output_start = output.rfind("MEMORY")
        if output_start == -1:
            logger.error("Lrun result parse error")
            logger.error(output)
            raise JudgeClientError("Lrun result parse error")
        # 如果不是0，说明lrun输出前面有输出，也就是程序的stderr有内容
        if output_start != 0:
            error = output[0:output_start]
        # 分离出lrun的输出
        output = output[output_start:]

        return error, parse_lrun_output(output)

    def _compare_output(self, test_case_id):
        test_case_config = self._test_case_info["test_cases"][str(test_case_id)]
        output_path = judger_workspace + str(test_case_id) + ".out"

        try:
            f = open(output_path, "rb")
        except IOError:
            # 文件不存在等引发的异常 返回结果错误
            return "", False

        if "striped_output_md5" not in test_case_config:
            # 计算输出文件的md5 和之前测试用例文件的md5进行比较
            # 兼容之前没有striped_output_md5的测试用例
            # 现在比较的是完整的文件
            md5 = hashlib.md5()
            while True:
                data = f.read(2 ** 8)
                if not data:
                    break
                md5.update(data)
            output_md5 = md5.hexdigest()

            return output_md5, output_md5 == test_case_config["output_md5"]
        else:
            # 这时候需要去除用户输出最后的空格和换行 再去比较md5
            md5 = hashlib.md5()
            # 比较和返回去除空格后的md5比较结果
            md5.update(f.read().rstrip())
            output_md5 = md5.hexdigest()
            return output_md5, output_md5 == test_case_config["striped_output_md5"]

    def _judge_one(self, test_case_id):
        # 运行lrun程序 接收返回值
        command = self._generate_command(test_case_id)
        status_code, output = commands.getstatusoutput(command)
        if status_code:
            raise JudgeClientError(output)
        error, run_result = self._parse_lrun_output(output)

        run_result["test_case_id"] = test_case_id

        # 代表内存或者时间超过限制了 程序被终止掉 要在runtime error 之前判断
        if run_result["exceed"]:
            if run_result["exceed"] == "memory":
                run_result["result"] = result["memory_limit_exceeded"]
            elif run_result["exceed"] in ["cpu_time", "real_time"]:
                run_result["result"] = result["time_limit_exceeded"]
            else:
                logger.error("Error exceeded type: " + run_result["exceed"])
                logger.error(output)
                raise JudgeClientError("Error exceeded type: " + run_result["exceed"])
            return run_result

        # 如果返回值非0 或者信号量不是0 或者程序的stderr有输出 代表非正常结束
        if run_result["exit_code"] or run_result["term_sig"] or run_result["siginaled"] or error:
            run_result["result"] = result["runtime_error"]
            return run_result

        # 下面就是代码正常运行了 需要判断代码的输出是否正确
        output_md5, r = self._compare_output(test_case_id)
        if r:
            run_result["result"] = result["accepted"]
        else:
            run_result["result"] = result["wrong_answer"]
        run_result["output_md5"] = output_md5

        return run_result

    def run(self):
        # 添加到任务队列
        _results = []
        results = []
        for i in range(self._test_case_info["test_case_number"]):
            _results.append(self._pool.apply_async(_run, (self, i + 1)))
        self._pool.close()
        self._pool.join()
        for item in _results:
            # 注意多进程中的异常只有在get()的时候才会被引发
            # http://stackoverflow.com/questions/22094852/how-to-catch-exceptions-in-workers-in-multiprocessing
            try:
                results.append(item.get())
            except Exception as e:
                logger.error("system error")
                logger.error(e)
                results.append({"result": result["system_error"]})
        return results

    def __getstate__(self):
        # 不同的pool之间进行pickle的时候要排除自己，否则报错
        # http://stackoverflow.com/questions/25382455/python-notimplementederror-pool-objects-cannot-be-passed-between-processes
        self_dict = self.__dict__.copy()
        del self_dict['_pool']
        return self_dict