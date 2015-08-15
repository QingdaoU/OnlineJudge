# coding=utf-8
import sys
import os
import pymongo

from bson.objectid import ObjectId

from client import JudgeClient
from language import languages
from compiler import compile_
from result import result
from settings import judger_workspace

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

from judger_controller.settings import celery_mongodb_config, docker_mongodb_config


# 简单的解析命令行参数
# 参数有 -solution_id -time_limit -memory_limit -test_case_id
# 获取到的值是['xxx.py', '-solution_id', '1111', '-time_limit', '1000', '-memory_limit', '100', '-test_case_id', 'aaaa']
args = sys.argv
submission_id = args[2]
time_limit = args[4]
memory_limit = args[6]
test_case_id = args[8]

connection = pymongo.MongoClient(host=docker_mongodb_config["host"], port=docker_mongodb_config["port"])
collection = connection["oj"]["oj_submission"]

submission = collection.find_one({"_id": ObjectId(submission_id)})
if not submission:
    exit()
connection.close()

# 将代码写入文件
language = languages[submission["language"]]
src_path = judger_workspace + "run/" + language["src_name"]
f = open(src_path, "w")
f.write(submission["code"].encode("utf8"))
f.close()

# 编译
try:
    exe_path = compile_(language, src_path, judger_workspace + "run/")
except Exception as e:
    print e
    connection = pymongo.MongoClient(host=docker_mongodb_config["host"], port=docker_mongodb_config["port"])
    collection = connection["oj"]["oj_submission"]
    data = {"result": result["compile_error"], "info": str(e)}
    collection.find_one_and_update({"_id": ObjectId(submission_id)}, {"$set": data})
    connection.close()
    exit()

print "Compile successfully"
# 运行
try:
    client = JudgeClient(language_code=submission["language"],
                         exe_path=exe_path,
                         max_cpu_time=int(time_limit),
                         max_real_time=int(time_limit) * 2,
                         max_memory=int(memory_limit),
                         test_case_dir=judger_workspace + "test_case/" + test_case_id + "/")
    judge_result = {"result": result["accepted"], "info": client.run()}

    for item in judge_result["info"]:
        if item["result"]:
            judge_result["result"] = item["result"]
            break
    else:
        l = sorted(judge_result["info"], key=lambda k: k["cpu_time"])
        judge_result["accepted_answer_info"] = {"time": l[-1]["cpu_time"]}

except Exception as e:
    print e
    judge_result = {"result": result["system_error"], "info": str(e)}

print "Run successfully"
print judge_result
connection = pymongo.MongoClient(host=docker_mongodb_config["host"], port=docker_mongodb_config["port"])
collection = connection["oj"]["oj_submission"]
collection.find_one_and_update({"_id": ObjectId(submission_id)}, {"$set": judge_result})
connection.close()
