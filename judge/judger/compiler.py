# coding=utf-8
import commands

from settings import lrun_uid, lrun_gid
from judge_exceptions import CompileError, JudgeClientError
from utils import parse_lrun_output


def compile_(language_item, src_path, exe_path):
    compile_command = language_item["compile_command"].format(src_path=src_path, exe_path=exe_path)

    # 防止编译器卡死 或者 include </dev/random>等
    execute_command = "lrun" + \
                      " --max-real-time 5" + \
                      " --uid " + str(lrun_uid) + \
                      " --gid " + str(lrun_gid) + \
                      " " + \
                      compile_command + \
                      " 3>&2"
    status, output = commands.getstatusoutput(execute_command)

    output_start = output.rfind("MEMORY")

    if output_start == -1:
        raise JudgeClientError("Error running compiler in lrun")

    # 返回值不为 0 或者 stderr 中 lrun 的输出之前有 erro r字符串
    # 判断 error 字符串的原因是链接的时候可能会有一些不推荐使用的函数的的警告，
    # 但是 -w 参数并不能关闭链接时的警告
    if status or "error" in output[0:output_start]:
        raise CompileError(output[0:output_start])

    parse_result = parse_lrun_output(output[output_start:])

    if parse_result["exit_code"] or parse_result["term_sig"] or parse_result["siginaled"] or parse_result["exceed"]:
        raise CompileError("Compile error")
    return exe_path
