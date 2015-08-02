# coding=utf-8
from judge_exceptions import JudgeClientError


def parse_lrun_output(output):
    lines = output.split("\n")
    if len(lines) != 7:
        raise JudgeClientError("Lrun result parse error")
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
