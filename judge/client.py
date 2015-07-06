# coding=utf-8
import commands
import hashlib
from multiprocessing import Pool

from settings import max_running_number, lrun_gid, lrun_uid, judger_workspace
from consts import Language, Result


class JudgeClientException(Exception):
    pass


# 下面这个函数作为代理访问实例变量，否则Python2会报错，是Python2的已知问题
# http://stackoverflow.com/questions/1816958/cant-pickle-type-instancemethod-when-using-pythons-multiprocessing-pool-ma/7309686
def _run(instance, test_case_id):
    return instance.judge_one(test_case_id)


class JudgeClient(object):
    def __init__(self, language, exec_file_path, max_cpu_time,
                 max_real_time, max_memory, test_case_dir):
        """
        :param language: 语言，见consts.py
        :param exec_file_path: 可执行文件路径
        :param max_cpu_time: 最大cpu时间，单位ms
        :param max_real_time: 最大执行时间，单位ms
        :param max_memory: 最大内存，单位MB
        :param test_case_dir: 测试用户文件夹路径
        :return:返回结果list
        """
        self.language = language
        self.exec_file_path = exec_file_path
        self.max_cpu_time = max_cpu_time
        self.max_real_time = max_real_time
        self.max_memory = max_memory
        self.test_case_dir = test_case_dir
        # 进程池
        self.pool = Pool(processes=max_running_number)
        # 结果数组
        self.results = []
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
                              "output_md5": "b10a8db164e0754105b7a99be72e3fe5",
                              "output_size": 100},

                        "2": {"input_name": "2.in",
                              "output_name": "2.out",
                              "output_md5": "3e25960a79dbc69b674cd4ec67a72c62",
                              "output_size": 100}
                    },
                "output_total_size": 200
                }

    def generate_command(self, test_case_id):
        """
        设置相关运行限制 进制访问网络 如果启用tmpfs 就把代码输出写入tmpfs，否则写入硬盘
        """
        # todo 系统调用白名单 chroot等参数
        # fixme 时间的单位问题
        command = "lrun" + \
                  " --max-cpu-time " + str(self.max_cpu_time / 1000.0) + \
                  " --max-real-time " + str(self.max_real_time / 1000.0) + \
                  " --max-memory " + str(self.max_memory * 1000 * 1000) + \
                  " --network false" + \
                  " --uid " + str(lrun_uid) + \
                  " --gid " + str(lrun_gid)

        if self.language == Language.JAVA:
            command += (" java " + self.exec_file_path)
        else:
            command += (" " + self.exec_file_path)

        command += (" 0<" + self.test_case_dir + str(test_case_id) + ".in" +
                    " 1>" + judger_workspace + str(test_case_id) + ".out" +
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
                     "TERMSIG": "term_sig",
                     "SIGNALED": "siginaled",
                     "EXITCODE": "exit_code",
                     "EXCEED": "exceed"}
        for line in lines:
            name = line[:9].strip(" ")
            value = line[9:]
            if name == "MEMORY":
                result[translate[name]] = int(value)
            elif name == "CPUTIME":
                result[translate[name]] = int(float(value) * 1000)
            elif name == "REALTIME":
                result[translate[name]] = int(float(value) * 1000)
            elif name == "EXITCODE":
                result[translate[name]] = int(value)
            elif name == "TERMSIG":
                result[translate[name]] = int(value)
            elif name == "SIGNALED":
                result[translate[name]] = int(value)
            elif name == "EXCEED":
                if value == "none":
                    result[translate[name]] = None
                else:
                    result[translate[name]] = translate[value]
        return result

    def compare_output(self, test_case_id):
        test_case_md5 = self.test_case_info["test_cases"][str(test_case_id)]["output_md5"]
        output_path = judger_workspace + str(test_case_id) + ".out"

        try:
            f = open(output_path, "rb")
        except IOError:
            # 文件不存在等引发的异常 返回结果错误
            return False

        # 计算输出文件的md5 和之前测试用例文件的md5进行比较
        md5 = hashlib.md5()
        while True:
            data = f.read(2 ** 8)
            if not data:
                break
            md5.update(data)

        # 对比文件是否一致
        print "my", md5.hexdigest()
        print test_case_md5
        # todo 去除最后的空行
        return md5.hexdigest() == test_case_md5

    def judge_one(self, test_case_id):
        # 运行lrun程序 接收返回值
        command = self.generate_command(test_case_id)
        status_code, output = commands.getstatusoutput(command)
        if status_code:
            raise JudgeClientException(output)
        run_result = self.parse_lrun_output(output)

        run_result["test_case_id"] = test_case_id

        # 如果返回值非0 或者信号量不是0 代表非正常结束
        if run_result["exit_code"] or run_result["term_sig"] or run_result["siginaled"]:
            run_result["result"] = Result.RUNTIME_ERROR
            return run_result

        # 代表内存或者时间超过限制了
        if run_result["exceed"]:
            if run_result["exceed"] == "memory":
                run_result["result"] = Result.MEMORY_LIMIT_EXCEEDED
            elif run_result["exceed"] in ["cpu_time", "real_time"]:
                run_result["result"] = Result.TIME_LIMIT_EXCEEDED
            else:
                raise JudgeClientException("Error exceeded type: " + run_result["exceed"])
            return run_result

        # 下面就是代码正常运行了 需要判断代码的输出是否正确

        if self.compare_output(test_case_id):
            run_result["result"] = Result.ACCEPTED
        else:
            run_result["result"] = Result.WRONG_ANSWER

        return run_result

    def collect_result(self, result):
        self.results.append(result)

    def run(self):
        # 添加到任务队列
        _results = []
        results = []
        for i in range(self.test_case_info["test_case_number"]):
            _results.append(self.pool.apply_async(_run, (self, i + 1)))
        self.pool.close()
        self.pool.join()
        for item in _results:
            # 注意多进程中的异常只有在get()的时候才会被引发
            # http://stackoverflow.com/questions/22094852/how-to-catch-exceptions-in-workers-in-multiprocessing
            try:
                results.append(item.get())
            except Exception as e:
                print e
                results.append({"result": Result.SYSTEM_ERROR})
        return results

    def __getstate__(self):
        # 不同的pool之间进行pickle的时候要排除自己，否则报错
        # http://stackoverflow.com/questions/25382455/python-notimplementederror-pool-objects-cannot-be-passed-between-processes
        self_dict = self.__dict__.copy()
        del self_dict['pool']
        return self_dict


client = JudgeClient(language=Language.C,
                     exec_file_path="/var/judger/a.out",
                     max_cpu_time=1000000,
                     max_real_time=200000,
                     max_memory=1,
                     test_case_dir="/var/test_cases/1/")
print client.run()
