# coding=utf-8
import os
import judger

WA = 1
AC = 0
SPJ_ERROR = -1


def file_exists(path):
    return os.path.exists(path)


def spj(path, max_cpu_time, max_memory, in_path, user_out_path):
    if file_exists(in_path) and file_exists(user_out_path):
        result = judger.run(path=path, in_file=in_path, out_file="/tmp/spj.out",
                            max_cpu_time=max_cpu_time, max_memory=max_memory,
                            args=[in_path, user_out_path], env=["PATH=" + os.environ.get("PATH", "")],
                            use_sandbox=True, use_nobody=True)
        if result["signal"] == 0 and result["exit_status"] in [AC, WA, SPJ_ERROR]:
            result["spj_result"] = result["exit_status"]
        else:
            result["spj_result"] = SPJ_ERROR
        return result
    else:
        raise ValueError("in_path or user_out_path does not exist")