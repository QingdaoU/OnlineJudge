# coding=utf-8
# from __future__ import absolute_import
import pymongo
from bson import ObjectId
import subprocess32 as subprocess
from ..judger.result import result
from ..judger_controller.celery import app
from settings import docker_config, source_code_dir, test_case_dir, mongodb_config


@app.task
def judge(submission_id, time_limit, memory_limit, test_case_id):
    try:
        command = "%s run -t -i --privileged --rm=true " \
                  "-v %s:/var/judger/test_case/ " \
                  "-v %s:/var/judger/code/ " \
                  "%s " \
                  "python judge/judger/run.py " \
                  "--solution_id %s --time_limit %s --memory_limit %s --test_case_id %s" % \
                  (docker_config["docker_path"],
                   test_case_dir,
                   source_code_dir,
                   docker_config["image_name"],
                   submission_id, str(time_limit), str(memory_limit), test_case_id)
        subprocess.call(command, timeout=(time_limit / 1000.0 * 10), shell=docker_config["shell"])
    except Exception as e:
        connection = pymongo.MongoClient(host=mongodb_config["host"], port=mongodb_config["port"])
        collection = connection["oj"]["oj_submission"]
        data = {"result": result["system_error"], "info": str(e)}
        collection.find_one_and_update({"_id": ObjectId(submission_id)}, {"$set": data})
        connection.close()
