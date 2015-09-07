# coding=utf-8
import sys
import json
import MySQLdb
import os

# 判断判题模式
judge_model = os.environ.get("judge_model", "default")
if judge_model == "default":
    from client import JudgeClient
elif judge_model == "loose":
    from loose_client import JudgeClient

from language import languages
from compiler import compile_
from result import result
from settings import judger_workspace

from settings import submission_db


# 简单的解析命令行参数
# 参数有 -solution_id -time_limit -memory_limit -test_case_id
# 获取到的值是['xxx.py', '-solution_id', '1111', '-time_limit', '1000', '-memory_limit', '100', '-test_case_id', 'aaaa']
args = sys.argv
submission_id = args[2]
time_limit = args[4]
memory_limit = args[6]
test_case_id = args[8]


def db_conn():
    return MySQLdb.connect(db=submission_db["db"],
                           user=submission_db["user"],
                           passwd=submission_db["password"],
                           host=submission_db["host"],
                           port=submission_db["port"], charset="utf8")


conn = db_conn()
cur = conn.cursor()
cur.execute("select language, code from submission where id = %s", (submission_id,))
data = cur.fetchall()
if not data:
    exit()
language_code = data[0][0]
code = data[0][1]

conn.close()

# 将代码写入文件
language = languages[language_code]
src_path = judger_workspace + "run/" + language["src_name"]
f = open(src_path, "w")
f.write(code.encode("utf8"))
f.close()

# 编译
try:
    exe_path = compile_(language, src_path, judger_workspace + "run/")
except Exception as e:
    print e
    conn = db_conn()
    cur = conn.cursor()
    cur.execute("update submission set result=%s, info=%s where id=%s",
                (result["compile_error"], str(e), submission_id))
    conn.commit()
    exit()

print "Compile successfully"
# 运行
try:
    client = JudgeClient(language_code=language_code,
                         exe_path=exe_path,
                         max_cpu_time=int(time_limit),
                         max_real_time=int(time_limit) * 2,
                         max_memory=int(memory_limit),
                         test_case_dir=judger_workspace + "test_case/" + test_case_id + "/")
    judge_result = {"result": result["accepted"], "info": client.run(), "accepted_answer_time": None}

    for item in judge_result["info"]:
        if item["result"]:
            judge_result["result"] = item["result"]
            break
    else:
        l = sorted(judge_result["info"], key=lambda k: k["cpu_time"])
        judge_result["accepted_answer_time"] = l[-1]["cpu_time"]

except Exception as e:
    print e
    conn = db_conn()
    cur = conn.cursor()
    cur.execute("update submission set result=%s, info=%s where id=%s", (result["system_error"], str(e), submission_id))
    conn.commit()
    exit()

print "Run successfully"
print judge_result

conn = db_conn()
cur = conn.cursor()
cur.execute("update submission set result=%s, info=%s, accepted_answer_time=%s where id=%s",
            (judge_result["result"], json.dumps(judge_result["info"]), judge_result["accepted_answer_time"],
             submission_id))
conn.commit()
conn.close()
