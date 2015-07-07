# coding=utf-8
import commands


class CompileError(Exception):
    pass


def compile_(language_item, src_path, exe_path):
    command = language_item["compile_command"].format(src_path=src_path, exe_path=exe_path)
    status, output = commands.getstatusoutput(command)
    if status:
        raise CompileError(output)
    return exe_path
