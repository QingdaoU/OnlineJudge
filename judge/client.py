# coding=utf-8
import json
import time
import commands
from Queue import Queue
from thread_pool import ThreadPool
from settings import MAX_RUNNING_NUMBER, LRUN_GID, LRUN_UID, USE_TMPFS


class JudgeClientException(Exception):
    pass


class JudgeClient(object):
    def __init__(self, language, exec_file_path, max_cpu_time,
                 max_real_time, max_memory, test_case_dir):
        # 语言 c cpp 或者 java
        self.language = language
        # 可执行文件路径，比如 /root/1/a.out /root/1/Main.class
        self.exec_file_path = exec_file_path
        # 最大的cpu时间
        self.max_cpu_time = max_cpu_time
        # 最大实际运行时间
        self.max_real_time = max_real_time
        # 最大cpu占用，注意不要小于500000
        self.max_memory = max_memory
        # 测试用例文件路径，比如/root/testcase/1/
        self.test_case_dir = test_case_dir
        # 判题结果队列
        self.result_queue = Queue()
        # 线程池
        self.thread_pool = ThreadPool(size=MAX_RUNNING_NUMBER,
                                      result_queue=self.result_queue)
        self.thread_pool.start()
        # 测试用例配置项
        self.test_case_config = {}
        self.load_test_case_config()

    def load_test_case_config(self):
        # 读取测试用例配置项 转换为dict
        # try:
        #     f = open(self.test_case_dir + "config")
        #     self.test_case_config = json.loads(f.read())
        # except IOError:
        #     raise JudgeClientException("Test case config file not found")
        # except ValueError:
        #     raise JudgeClientException("Test case config file format error")
        return {"test_case_number": 1,
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
        command = "lrun" + \
                  " --max-cpu-time " + str(self.max_cpu_time) + \
                  " --max-real-time " + str(self.max_real_time) + \
                  " --max-memory " + str(self.max_memory) + \
                  " --network false" + \
                  " --uid " + str(LRUN_UID) + \
                  " --gid " + str(LRUN_GID)
        if USE_TMPFS:
            command += (" --tmpfs /var " +
                        str(int(self.test_case_config["test_cases"][str(test_case_id)]["output_size"] * 1.2)))

        if self.language == "java":
            command += (" java " + self.exec_file_path)
        else:
            command += (" " + self.exec_file_path)
        # fixme 输出路径
        command += (" 0<" + self.test_case_dir + str(test_case_id) + ".in" +
                    " 1>" + "/var/" + str(test_case_id) + ".out" +
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
                if result == "none":
                    result[translate[name]] = None
                else:
                    result[translate[name]] = translate[value]
        return result

    def judge_one(self, test_case_id):
        command = self.generate_command(test_case_id + 1)
        status_code, output = commands.getstatusoutput(command)
        if status_code:
            raise JudgeClientException(output)
        return output

    def run(self):
        # 添加到任务队列
        for i in range(self.test_case_config["test_case_number"]):
            self.thread_pool.append_job(self.judge_one, i)

        self.thread_pool.join()
        self.thread_pool.stop()

        # 先判断lrun的返回结果 看是否有超过限制的 在判断输出结果
        for i in range(self.test_case_config["test_case_number"]):
            result = self.parse_lrun_output(self.result_queue.get(block=False))

        # todo


client = JudgeClient(language="c",
                     exec_file_path="/root/a.out",
                     max_cpu_time=1000,
                     max_real_time=2000,
                     max_memory=600000,
                     test_case_dir="/root/test_case/p1/")
