# coding=utf-8
import json
import time
import commands
from Queue import Queue
from thread_pool import ThreadPool
from settings import max_running_number, lrun_gid, lrun_uid, use_tmpfs
from consts import Language, Result


class JudgeClientException(Exception):
    pass


class JudgeClient(object):
    def __init__(self, language, exec_file_path, max_cpu_time,
                 max_real_time, max_memory, test_case_dir):
        # 语言 c cpp 或者 java
        self.language = language
        # 可执行文件路径，比如 /root/1/a.out /root/1/Main.class
        self.exec_file_path = exec_file_path
        # 最大的cpu时间 单位ms
        self.max_cpu_time = max_cpu_time
        # 最大实际运行时间 单位ms
        self.max_real_time = max_real_time
        # 最大cpu占用，注意不要小于500000 单位byte
        self.max_memory = max_memory
        # 测试用例文件路径，比如/root/testcase/1/
        self.test_case_dir = test_case_dir
        # 判题结果队列
        self.result_queue = Queue()
        # 线程池
        self.thread_pool = ThreadPool(size=max_running_number,
                                      result_queue=self.result_queue)
        self.thread_pool.start()
        # 测试用例配置项
        self.test_case_info = self.load_test_case_info()

    def load_test_case_info(self):
        # 读取测试用例信息 转换为dict
        # try:
        #     f = open(self.test_case_dir + "info")
        #     return json.loads(f.read())
        # except IOError:
        #     raise JudgeClientException("Test case config file not found")
        # except ValueError:
        #     raise JudgeClientException("Test case config file format error")
        return {"test_case_number": 2,
                "test_cases":
                    {
                        "1": {"input_name": "1.in",
                              "output_name": "1.out",
                              "output_md5": "yyy",
                              "output_size": 100},

                        "2": {"input_name": "2.in",
                              "output_name": "2.out",
                              "output_md5": "yyy",
                              "output_size": 100}
                    }
                }

    def generate_command(self, test_case_id):
        """
        设置相关运行限制 进制访问网络 如果启用tmpfs 就把代码输出写入tmpfs，否则写入硬盘
        """
        # todo 系统调用白名单 chroot等参数
        # fixme 时间的单位问题
        command = "lrun" + \
                  " --max-cpu-time " + str(self.max_cpu_time) + \
                  " --max-real-time " + str(self.max_real_time) + \
                  " --max-memory " + str(self.max_memory) + \
                  " --network false" + \
                  " --uid " + str(lrun_uid) + \
                  " --gid " + str(lrun_gid)
        #if use_tmpfs:
        #    command += (" --tmpfs /var " +
        #                str(int(self.test_case_info["test_cases"][str(test_case_id)]["output_size"] * 1.2)))

        if self.language == Language.JAVA:
            command += (" java " + self.exec_file_path)
        else:
            command += (" " + self.exec_file_path)
        # fixme 输出路径
        command += (" 0<" + self.test_case_dir + str(test_case_id) + ".in" +
                    " 1>" + "/var/judge/" + str(test_case_id) + ".out" +
                    " 3>&2")
        return command

    def parse_lrun_output(self, output):
        lines = output.split("\n")
        if len(lines) != 7:
            raise JudgeClientException("Lrun result parse error")
        result = {}
        # 将lrun输出的各种带下划线 不带下划线的字符串统一处理
        translate = {"MEMORY": "memory",
                     "CPUTIME": "cpu_time",
                     "CPU_TIME": "cpu_time",
                     "REALTIME": "real_time",
                     "REAL_TIME": "real_time",
                     "EXITCODE": "exit_code",
                     "EXCEED": "exceed"}
        for line in lines:
            name = line[:9].strip(" ")
            value = line[9:]
            print name, value
            if name == "MEMORY":
                result[translate[name]] = int(value)
            elif name == "CPUTIME":
                result[translate[name]] = float(value) * 1000
            elif name == "REALTIME":
                result[translate[name]] = float(value) * 1000
            elif name == "EXITCODE":
                result[translate[name]] = int(value)
            elif name == "EXCEED":
                if value == "none":
                    result[translate[name]] = None
                else:
                    result[translate[name]] = translate[value]
        return result

    def judge_one(self, test_case_id):
        # 运行lrun程序 接收返回值
        command = self.generate_command(test_case_id)
        status_code, output = commands.getstatusoutput(command)
        if status_code:
            raise JudgeClientException(output)
        run_result = self.parse_lrun_output(output)

        run_result["test_case_id"] = test_case_id

        # 如果返回值非0，代表非正常结束
        if run_result["exit_code"]:
            run_result["result"] = Result.RUNTIME_ERROR
            return run_result

        # 代表内存或者时间超过限制了
        if run_result["exceed"]:
            if run_result["exceed"] == "memory":
                run_result["result"] = Result.MEMORY_LIMIT_EXCEEDED
            elif run_result["exceed"] in ["cpu_time", "real_time"]:
                run_result["result"] = Result.TIME_LIMIT_EXCEEDED
            else:
                run_result["result"] = Result.SYSTEM_ERROR
            return run_result

        # 下面就是代码正常运行了
        run_result["result"] = Result.ACCEPTED
        return run_result

    def run(self):
        # 添加到任务队列
        for i in range(self.test_case_info["test_case_number"]):
            self.thread_pool.append_job(self.judge_one, i + 1)

        self.thread_pool.join()
        self.thread_pool.stop()

        for i in range(self.test_case_info["test_case_number"]):
            print self.result_queue.get(block=False)


client = JudgeClient(language=Language.C,
                     exec_file_path="/var/judge/a.out",
                     max_cpu_time=1000,
                     max_real_time=2000,
                     max_memory=600000,
                     test_case_dir="/var/test_case/1/")
client.run()
