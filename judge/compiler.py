# coding=utf-8
import os
import judger
from judge_exceptions import CompileError
from logger import logger


def compile_(language_item, src_path, exe_path, judge_base_path, compile_spj=False):
    command_item = "spj_compile_command" if compile_spj else "compile_command"
    compile_command = language_item[command_item].format(src_path=src_path, exe_path=exe_path).split(" ")
    compiler = compile_command[0]
    compile_args = compile_command[1:]
    compiler_output_file = os.path.join(judge_base_path, "compiler.out")

    compile_result = judger.run(path=compiler,
                                in_file="/dev/null",
                                out_file=compiler_output_file,
                                max_cpu_time=language_item["compile_max_cpu_time"],
                                max_memory=language_item["compile_max_memory"],
                                args=compile_args,
                                env=["PATH=" + os.environ["PATH"]],
                                use_sandbox=False,
                                use_nobody=True)

    compile_output_handler = open(compiler_output_file)
    compile_output = compile_output_handler.read().strip()
    compile_output_handler.close()

    if compile_result["flag"] != 0:
        logger.error("Compiler error")
        logger.error(compile_output)
        logger.error(str(compile_result))
        if compile_output:
            raise CompileError(compile_output)
        else:
            raise CompileError("Compile error, info: " + str(compile_result))
    else:
        if "error" in compile_output:
            raise CompileError(compile_output)
        return exe_path
