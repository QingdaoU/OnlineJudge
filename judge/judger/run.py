# coding=utf-8
import sys
from client import JudgeClient
from language import languages
from compiler import compile_
from result import result


judger_workspace = "/var/judger/run/"
# 简单的解析命令行参数
# 参数有 -solution_id -max_cpu_time -max_memory -test_case_id
# 获取到的值是['xxx.py', '-solution_id', '1111', '-max_cpu_time', '1000', '-max_memory', '100', '-test_case_id', 'aaaa']
args = sys.argv
solution_id = args[2]
max_cpu_time = args[4]
max_memory = args[6]
test_case_id = args[8]

# todo 去数据库查一下
language_code = 1
source_string = """
#include <stdio.h>
int main()
{
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a + b);
    return 0;
}
"""
language = languages[str(language_code)]
src_path = judger_workspace + language["src_name"]
f = open(src_path, "w")
f.write(source_string)
f.close()

try:
    exe_path = compile_(languages[str(language_code)], src_path, judger_workspace)
except Exception as e:
    print e
    print [{"result": result["compile_error"]}]
    exit()

client = JudgeClient(language_code=language_code,
                     exe_path=exe_path,
                     max_cpu_time=1000000,
                     max_real_time=200000,
                     max_memory=1000,
                     test_case_dir="/var/test_cases/1/")
print client.run()


